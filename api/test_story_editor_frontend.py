#!/usr/bin/env python
"""Tests for Story Editor Page Frontend — backend API coverage.

Covers spec clauses for the novel/TipTap editor integration:
  - format='html' accepted by POST /api/stories
  - format='html' accepted by PUT /api/stories/:id
  - format='html' accepted by PATCH /api/stories/:id (auto-save)
  - GET /api/stories/my-draft returns story with format field
  - POST /api/gpt/paraphrase returns 3 suggestions
  - PUT /api/auth/profile accepts signature
  - GET /api/auth/me returns signature in metadata
  - HTML content round-trip (store and retrieve)
  - PATCH auto-save with HTML content + title
  - Publish flow: PUT visibility=private on a draft
  - 409 on second draft creation
"""

import sys
import os
import tempfile

os.environ['TEST_MODE'] = '1'
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from interfaces.api_backend import APIBackend


# ── Helpers ───────────────────────────────────────────────────────────────────

def _create_test_app():
    os.environ.pop('MONGODB_URI', None)
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    path = temp_db.name
    temp_db.close()
    backend = APIBackend(storage_type='nosql', db_path=path)
    return backend, path


def _register_and_login(client, username, email, password='Test@1234'):
    resp = client.post('/api/auth/register', json={
        'username': username, 'email': email, 'password': password
    }, content_type='application/json')
    assert resp.status_code == 201, f"Register failed: {resp.data}"
    return resp.get_json()['token']


def _auth(token):
    return {'Authorization': f'Bearer {token}'}


def _create_world(client, token, name='Test World'):
    resp = client.post('/api/worlds', json={
        'name': name, 'world_type': 'fantasy',
        'description': 'A test world.', 'visibility': 'private'
    }, headers=_auth(token), content_type='application/json')
    assert resp.status_code == 201, f"Create world failed: {resp.data}"
    return resp.get_json()['data']['world_id']


def _create_story(client, token, world_id, title='Test Story',
                  visibility='private', fmt='html', content=''):
    return client.post('/api/stories', json={
        'title': title, 'world_id': world_id,
        'visibility': visibility, 'format': fmt, 'content': content,
    }, headers=_auth(token), content_type='application/json')


results = []

def check(name, passed, detail=''):
    status = '✅' if passed else '❌'
    results.append((name, passed))
    print(f"  {status} {name}" + (f": {detail}" if detail and not passed else ''))
    return passed

def _unlink(path):
    try:
        os.unlink(path)
    except OSError:
        pass  # Windows may keep file locked briefly


# ══════════════════════════════════════════════════════════════════════════════
# 1. format='html' schema validation
# ══════════════════════════════════════════════════════════════════════════════

def test_create_story_html_format():
    print("\n[1] POST /api/stories with format='html'...")
    backend, path = _create_test_app()
    client = backend.app.test_client()
    token = _register_and_login(client, 'user1', 'u1@x.com')
    world_id = _create_world(client, token)

    # html format accepted
    resp = _create_story(client, token, world_id, fmt='html')
    check('format=html accepted (201)', resp.status_code == 201,
          f"got {resp.status_code}: {resp.data}")

    if resp.status_code == 201:
        data = resp.get_json()['data']
        story = data.get('story', {})
        check('story.format == html', story.get('format') == 'html',
              f"got {story.get('format')}")

    # invalid format rejected
    resp2 = _create_story(client, token, world_id, fmt='docx', title='Bad')
    check('format=docx rejected (400)', resp2.status_code == 400,
          f"got {resp2.status_code}")

    _unlink(path)


def test_update_story_html_format():
    print("\n[2] PUT /api/stories/:id with format='html'...")
    backend, path = _create_test_app()
    client = backend.app.test_client()
    token = _register_and_login(client, 'user2', 'u2@x.com')
    world_id = _create_world(client, token)

    cr = _create_story(client, token, world_id, fmt='plain')
    if not check('setup: create plain story (201)', cr.status_code == 201,
                 f"got {cr.status_code}: {cr.data}"):
        _unlink(path); return
    story_id = cr.get_json()['data']['story_id']

    resp = client.put(f'/api/stories/{story_id}', json={
        'format': 'html', 'content': '<p>Hello world</p>'
    }, headers=_auth(token), content_type='application/json')
    check('PUT format=html accepted (200)', resp.status_code == 200,
          f"got {resp.status_code}: {resp.data}")

    if resp.status_code == 200:
        story = resp.get_json().get('data') or resp.get_json()
        fmt = story.get('format') if isinstance(story, dict) else None
        check('format updated to html', fmt == 'html', f"got {fmt}")

    _unlink(path)


def test_patch_story_html_content():
    print("\n[3] PATCH /api/stories/:id — auto-save with HTML content + title...")
    backend, path = _create_test_app()
    client = backend.app.test_client()
    token = _register_and_login(client, 'user3', 'u3@x.com')
    world_id = _create_world(client, token)

    cr = _create_story(client, token, world_id, fmt='html')
    if not check('setup: create html story (201)', cr.status_code == 201,
                 f"got {cr.status_code}: {cr.data}"):
        _unlink(path); return
    story_id = cr.get_json()['data']['story_id']

    html = '<h1>Chapter One</h1><p>It was a dark night.</p>'
    resp = client.patch(f'/api/stories/{story_id}', json={
        'title': 'Updated Title',
        'content': html,
        'format': 'html',
    }, headers=_auth(token), content_type='application/json')
    check('PATCH with HTML accepted (200)', resp.status_code == 200,
          f"got {resp.status_code}: {resp.data}")

    # verify content persisted
    get_resp = client.get(f'/api/stories/{story_id}',
                          headers=_auth(token))
    if get_resp.status_code == 200:
        body = get_resp.get_json()
        story = body.get('data') or body
        if isinstance(story, dict):
            check('HTML content persisted', story.get('content') == html,
                  f"got: {story.get('content', '')[:50]}")
            check('title persisted via PATCH', story.get('title') == 'Updated Title',
                  f"got: {story.get('title')}")
        else:
            check('HTML content persisted', False, 'story not a dict')
    else:
        check('GET after PATCH succeeds', False, f"got {get_resp.status_code}")

    _unlink(path)


# ══════════════════════════════════════════════════════════════════════════════
# 2. GET /api/stories/my-draft — format field included
# ══════════════════════════════════════════════════════════════════════════════

def test_my_draft_includes_format():
    print("\n[4] GET /api/stories/my-draft — format field present...")
    backend, path = _create_test_app()
    client = backend.app.test_client()
    token = _register_and_login(client, 'user4', 'u4@x.com')
    world_id = _create_world(client, token)

    _create_story(client, token, world_id, visibility='draft', fmt='html',
                  title='My Draft')

    resp = client.get('/api/stories/my-draft', headers=_auth(token))
    check('GET /my-draft 200', resp.status_code == 200,
          f"got {resp.status_code}")

    if resp.status_code == 200:
        story = resp.get_json()['data']['story']
        check('my-draft story not None', story is not None)
        if story:
            check('my-draft has format field', 'format' in story,
                  f"keys: {list(story.keys())}")
            check('my-draft format is html', story.get('format') == 'html',
                  f"got {story.get('format')}")

    _unlink(path)


# ══════════════════════════════════════════════════════════════════════════════
# 3. Publish flow: draft → private
# ══════════════════════════════════════════════════════════════════════════════

def test_publish_draft():
    print("\n[5] Publish flow: PUT visibility=private on draft...")
    backend, path = _create_test_app()
    client = backend.app.test_client()
    token = _register_and_login(client, 'user5', 'u5@x.com')
    world_id = _create_world(client, token)

    cr = _create_story(client, token, world_id, visibility='draft', fmt='html')
    if not check('setup: create draft (201)', cr.status_code == 201,
                 f"got {cr.status_code}: {cr.data}"):
        _unlink(path); return
    story_id = cr.get_json()['data']['story_id']

    resp = client.put(f'/api/stories/{story_id}', json={
        'visibility': 'private'
    }, headers=_auth(token), content_type='application/json')
    check('publish draft → private (200)', resp.status_code == 200,
          f"got {resp.status_code}: {resp.data}")

    # can now create a new draft (one-draft rule no longer blocks)
    cr2 = _create_story(client, token, world_id, visibility='draft',
                        title='Draft 2', fmt='html')
    check('new draft allowed after publish', cr2.status_code == 201,
          f"got {cr2.status_code}: {cr2.data}")

    _unlink(path)


def test_second_draft_rejected():
    print("\n[6] One-draft rule — second draft rejected (409)...")
    backend, path = _create_test_app()
    client = backend.app.test_client()
    token = _register_and_login(client, 'user6', 'u6@x.com')
    world_id = _create_world(client, token)

    cr1 = _create_story(client, token, world_id, visibility='draft', fmt='html',
                        title='Draft 1')
    check('first draft created', cr1.status_code == 201,
          f"got {cr1.status_code}")

    cr2 = _create_story(client, token, world_id, visibility='draft', fmt='html',
                        title='Draft 2')
    check('second draft rejected (409)', cr2.status_code == 409,
          f"got {cr2.status_code}: {cr2.data}")

    _unlink(path)


# ══════════════════════════════════════════════════════════════════════════════
# 4. GPT paraphrase — 3 suggestions returned
# ══════════════════════════════════════════════════════════════════════════════

def test_gpt_paraphrase_returns_suggestions():
    print("\n[7] POST /api/gpt/paraphrase — returns 3 suggestions...")
    backend, path = _create_test_app()
    client = backend.app.test_client()
    token = _register_and_login(client, 'user7', 'u7@x.com')

    resp = client.post('/api/gpt/paraphrase', json={
        'text': 'He walked into the dark room carefully.',
        'mode': 'paraphrase',
    }, headers=_auth(token), content_type='application/json')
    check('paraphrase 200', resp.status_code == 200,
          f"got {resp.status_code}: {resp.data}")

    if resp.status_code == 200:
        body = resp.get_json()
        # response may be { suggestions: [...] } or unwrapped
        suggestions = (body.get('data') or body).get('suggestions', [])
        check('3 suggestions returned', len(suggestions) == 3,
              f"got {len(suggestions)}: {suggestions}")

    # expand mode
    resp2 = client.post('/api/gpt/paraphrase', json={
        'text': 'She stood at the window.',
        'mode': 'expand',
    }, headers=_auth(token), content_type='application/json')
    check('expand mode 200', resp2.status_code == 200,
          f"got {resp2.status_code}")

    # missing text → 400
    resp3 = client.post('/api/gpt/paraphrase', json={
        'mode': 'paraphrase'
    }, headers=_auth(token), content_type='application/json')
    check('missing text → 400', resp3.status_code == 400,
          f"got {resp3.status_code}")

    # unauthenticated → 401
    resp4 = client.post('/api/gpt/paraphrase', json={
        'text': 'test text here.'
    }, content_type='application/json')
    check('no auth → 401', resp4.status_code == 401,
          f"got {resp4.status_code}")

    _unlink(path)


# ══════════════════════════════════════════════════════════════════════════════
# 5. Signature — PUT /auth/profile + GET /auth/me
# ══════════════════════════════════════════════════════════════════════════════

def test_signature_roundtrip():
    print("\n[8] Signature: PUT /auth/profile → GET /auth/me...")
    backend, path = _create_test_app()
    client = backend.app.test_client()
    token = _register_and_login(client, 'user8', 'u8@x.com')

    sig = 'Nguyễn Văn A, nhà văn'

    resp = client.put('/api/auth/profile', json={
        'signature': sig
    }, headers=_auth(token), content_type='application/json')
    check('PUT /auth/profile 200', resp.status_code == 200,
          f"got {resp.status_code}: {resp.data}")

    me_resp = client.get('/api/auth/me', headers=_auth(token))
    check('GET /auth/me 200', me_resp.status_code == 200,
          f"got {me_resp.status_code}")

    if me_resp.status_code == 200:
        body = me_resp.get_json()
        user = body.get('data') or body
        metadata = user.get('metadata', {}) if isinstance(user, dict) else {}
        check('signature persisted in metadata',
              metadata.get('signature') == sig,
              f"got: {metadata.get('signature')}")

    _unlink(path)


def test_signature_max_length():
    print("\n[9] Signature validation — max 200 chars...")
    backend, path = _create_test_app()
    client = backend.app.test_client()
    token = _register_and_login(client, 'user9', 'u9@x.com')

    resp = client.put('/api/auth/profile', json={
        'signature': 'x' * 201
    }, headers=_auth(token), content_type='application/json')
    check('201-char signature rejected (400)', resp.status_code == 400,
          f"got {resp.status_code}")

    resp2 = client.put('/api/auth/profile', json={
        'signature': 'x' * 200
    }, headers=_auth(token), content_type='application/json')
    check('200-char signature accepted', resp2.status_code == 200,
          f"got {resp2.status_code}")

    _unlink(path)


# ══════════════════════════════════════════════════════════════════════════════
# 6. HTML content round-trip
# ══════════════════════════════════════════════════════════════════════════════

def test_html_content_roundtrip():
    print("\n[10] HTML content round-trip (POST → GET)...")
    backend, path = _create_test_app()
    client = backend.app.test_client()
    token = _register_and_login(client, 'user10', 'u10@x.com')
    world_id = _create_world(client, token)

    html = '<h1>Title</h1><h2>Chapter 1</h2><p>Once upon a time <strong>darkness</strong> fell.</p><hr/><ul><li>item one</li><li>item two</li></ul>'

    cr = _create_story(client, token, world_id, fmt='html',
                       title='HTML Story', content=html)
    check('create with HTML content (201)', cr.status_code == 201,
          f"got {cr.status_code}: {cr.data}")

    if cr.status_code == 201:
        story_id = cr.get_json()['data']['story_id']
        gr = client.get(f'/api/stories/{story_id}', headers=_auth(token))
        check('GET story 200', gr.status_code == 200, f"got {gr.status_code}")

        if gr.status_code == 200:
            body = gr.get_json()
            story = body.get('data') or body
            if isinstance(story, dict):
                check('format=html stored', story.get('format') == 'html',
                      f"got {story.get('format')}")

    _unlink(path)


# ══════════════════════════════════════════════════════════════════════════════
# Run all
# ══════════════════════════════════════════════════════════════════════════════

def run_all():
    print('=' * 60)
    print('  Story Editor Frontend — API Tests')
    print('=' * 60)

    test_create_story_html_format()
    test_update_story_html_format()
    test_patch_story_html_content()
    test_my_draft_includes_format()
    test_publish_draft()
    test_second_draft_rejected()
    test_gpt_paraphrase_returns_suggestions()
    test_signature_roundtrip()
    test_signature_max_length()
    test_html_content_roundtrip()

    passing = sum(1 for _, p in results if p)
    failing = [n for n, p in results if not p]
    total = len(results)

    print()
    print('=' * 60)
    print(f'  Results: {passing}/{total} passing  |  {total - passing} failing')
    print('=' * 60)
    if failing:
        print('  Failing:')
        for name in failing:
            print(f'    - {name}')
    return failing


if __name__ == '__main__':
    failing = run_all()
    sys.exit(1 if failing else 0)
