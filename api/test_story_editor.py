#!/usr/bin/env python
"""Tests for Story Editor Page feature.

Covers all spec clauses for:
  SUB-2 — format field on Story model + schemas
  SUB-3 — Auto-save (PATCH endpoint already exists; draft lifecycle via PUT)
  SUB-4 — One-draft-per-user rule + GET /stories/my-draft + PUT /auth/profile (signature)

All tests are expected to FAIL (red state) until implementation is complete.
"""

import sys
import os
import json
import tempfile

os.environ['TEST_MODE'] = '1'

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from interfaces.api_backend import APIBackend


# ── Test app setup ────────────────────────────────────────────────────────────

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
        'name': name,
        'world_type': 'fantasy',
        'description': 'A test world.',
        'visibility': 'private'
    }, headers=_auth(token), content_type='application/json')
    assert resp.status_code == 201, f"Create world failed: {resp.data}"
    return resp.get_json()['data']['world_id']


def _create_story(client, token, world_id, title='Test Story',
                  visibility='private', fmt='plain'):
    resp = client.post('/api/stories', json={
        'title': title,
        'world_id': world_id,
        'visibility': visibility,
        'format': fmt,
    }, headers=_auth(token), content_type='application/json')
    return resp


# ── Results tracker ───────────────────────────────────────────────────────────

results = []

def check(name, passed, detail=''):
    status = '✅' if passed else '❌'
    results.append((name, passed))
    print(f"  {status} {name}" + (f": {detail}" if detail and not passed else ''))


# ══════════════════════════════════════════════════════════════════════════════
# SUB-2 (model): format field on Story
# ══════════════════════════════════════════════════════════════════════════════

def test_story_model_format_field():
    print("\n[SUB-2] Story model format field...")
    from core.models.story import Story

    # Default is 'plain'
    s = Story(title='T', content='C', world_id='w1')
    check('SUB-2: default format is plain', s.format == 'plain')

    # Explicit markdown
    s2 = Story(title='T', content='C', world_id='w1', format='markdown')
    check('SUB-2: explicit format=markdown', s2.format == 'markdown')

    # Roundtrip via to_dict / from_dict
    d = s2.to_dict()
    check('SUB-2: format in to_dict()', 'format' in d and d['format'] == 'markdown')
    s3 = Story.from_dict(d)
    check('SUB-2: from_dict() preserves format', s3.format == 'markdown')

    # from_dict without format key defaults to plain (BR-9 — old stories)
    d_legacy = {k: v for k, v in d.items() if k != 'format'}
    s4 = Story.from_dict(d_legacy)
    check('SUB-2: from_dict() defaults to plain when key missing', s4.format == 'plain')


# ══════════════════════════════════════════════════════════════════════════════
# SUB-2 (API): format field in create and update endpoints
# ══════════════════════════════════════════════════════════════════════════════

def test_story_create_with_format():
    print("\n[SUB-2] Create story with format field...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_fmt', 'fmt@test.com')
    world_id = _create_world(client, token)

    # Create with format=markdown
    resp = _create_story(client, token, world_id, fmt='markdown')
    check('SUB-2: create with format=markdown returns 201', resp.status_code == 201,
          f"status={resp.status_code} body={resp.data}")
    if resp.status_code == 201:
        story = resp.get_json()['data']['story']
        check('SUB-2: returned story has format=markdown', story.get('format') == 'markdown')

    # Create without format defaults to plain
    resp2 = client.post('/api/stories', json={
        'title': 'Plain Story', 'world_id': world_id
    }, headers=_auth(token), content_type='application/json')
    check('SUB-2: create without format returns 201', resp2.status_code == 201,
          f"status={resp2.status_code}")
    if resp2.status_code == 201:
        story2 = resp2.get_json()['data']['story']
        check('SUB-2: default format is plain', story2.get('format') == 'plain')

    # Invalid format rejected
    resp3 = client.post('/api/stories', json={
        'title': 'Bad', 'world_id': world_id, 'format': 'richtext'
    }, headers=_auth(token), content_type='application/json')
    check('SUB-2: invalid format value rejected (400)', resp3.status_code == 400,
          f"status={resp3.status_code}")


def test_story_update_format():
    print("\n[SUB-2] Update story format field...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_updfmt', 'updfmt@test.com')
    world_id = _create_world(client, token)

    resp = _create_story(client, token, world_id)
    assert resp.status_code == 201
    story_id = resp.get_json()['data']['story_id']

    # Update format via PUT
    resp2 = client.put(f'/api/stories/{story_id}', json={'format': 'markdown'},
                       headers=_auth(token), content_type='application/json')
    check('SUB-2: PUT with format=markdown returns 200', resp2.status_code == 200,
          f"status={resp2.status_code} body={resp2.data}")
    if resp2.status_code == 200:
        updated = resp2.get_json()['data']
        check('SUB-2: PUT updates format field', updated.get('format') == 'markdown')

    # Verify persistence via GET
    resp3 = client.get(f'/api/stories/{story_id}', headers=_auth(token))
    if resp3.status_code == 200:
        fetched = resp3.get_json()['data']
        check('SUB-2: format persisted after PUT', fetched.get('format') == 'markdown')


# ══════════════════════════════════════════════════════════════════════════════
# SUB-3: auto-save via PATCH (endpoint already exists)
# ══════════════════════════════════════════════════════════════════════════════

def test_patch_autosave():
    print("\n[SUB-3] Auto-save PATCH endpoint...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_patch', 'patch@test.com')
    world_id = _create_world(client, token)

    resp = _create_story(client, token, world_id)
    assert resp.status_code == 201
    story_id = resp.get_json()['data']['story_id']

    # PATCH content only
    resp2 = client.patch(f'/api/stories/{story_id}',
                         json={'content': '# Chapter 1\n\nHello world.'},
                         headers=_auth(token), content_type='application/json')
    check('SUB-3: PATCH content returns 200', resp2.status_code == 200,
          f"status={resp2.status_code} body={resp2.data}")
    if resp2.status_code == 200:
        data = resp2.get_json()['data']
        check('SUB-3: PATCH returns story_id', 'story_id' in data)
        check('SUB-3: PATCH returns updated_at', 'updated_at' in data)


# ══════════════════════════════════════════════════════════════════════════════
# SUB-4-B/C: one-draft rule + GET /stories/my-draft
# ══════════════════════════════════════════════════════════════════════════════

def test_my_draft_empty():
    print("\n[SUB-4] GET /stories/my-draft — no draft exists...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_nodraft', 'nodraft@test.com')

    resp = client.get('/api/stories/my-draft', headers=_auth(token))
    check('SUB-4: GET /my-draft returns 200', resp.status_code == 200,
          f"status={resp.status_code} body={resp.data}")
    if resp.status_code == 200:
        data = resp.get_json()['data']
        check('SUB-4: story is null when no draft', data.get('story') is None)


def test_my_draft_returns_draft():
    print("\n[SUB-4] GET /stories/my-draft — returns existing draft...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_hasdraft', 'hasdraft@test.com')
    world_id = _create_world(client, token)

    # Create a draft story
    resp = _create_story(client, token, world_id, title='My Draft', visibility='draft')
    assert resp.status_code == 201, f"Create draft failed: {resp.data}"
    draft_id = resp.get_json()['data']['story_id']

    resp2 = client.get('/api/stories/my-draft', headers=_auth(token))
    check('SUB-4: GET /my-draft returns 200 with draft', resp2.status_code == 200,
          f"status={resp2.status_code} body={resp2.data}")
    if resp2.status_code == 200:
        data = resp2.get_json()['data']
        check('SUB-4: returned story is not null', data.get('story') is not None)
        if data.get('story'):
            check('SUB-4: returned story_id matches', data['story']['story_id'] == draft_id)


def test_one_draft_per_user_create():
    print("\n[SUB-4] One draft per user — POST blocks second draft...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_2draft', '2draft@test.com')
    world_id = _create_world(client, token)

    # First draft succeeds
    resp1 = _create_story(client, token, world_id, title='Draft 1', visibility='draft')
    check('SUB-4: first draft created (201)', resp1.status_code == 201,
          f"status={resp1.status_code} body={resp1.data}")

    # Second draft blocked
    resp2 = _create_story(client, token, world_id, title='Draft 2', visibility='draft')
    check('SUB-4: second draft rejected (409)', resp2.status_code == 409,
          f"status={resp2.status_code} body={resp2.data}")


def test_one_draft_per_user_put():
    print("\n[SUB-4] One draft per user — PUT blocks changing to draft when one exists...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_putdraft', 'putdraft@test.com')
    world_id = _create_world(client, token)

    # Create a draft
    resp1 = _create_story(client, token, world_id, title='Existing Draft', visibility='draft')
    assert resp1.status_code == 201

    # Create a private story
    resp2 = _create_story(client, token, world_id, title='Private Story', visibility='private')
    assert resp2.status_code == 201
    private_id = resp2.get_json()['data']['story_id']

    # Try to change private → draft (blocked)
    resp3 = client.put(f'/api/stories/{private_id}', json={'visibility': 'draft'},
                       headers=_auth(token), content_type='application/json')
    check('SUB-4: changing to draft when one exists returns 409', resp3.status_code == 409,
          f"status={resp3.status_code} body={resp3.data}")


def test_publish_draft():
    print("\n[SUB-4] Publish draft — changes visibility to private...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_publish', 'publish@test.com')
    world_id = _create_world(client, token)

    resp1 = _create_story(client, token, world_id, title='To Publish', visibility='draft')
    assert resp1.status_code == 201
    story_id = resp1.get_json()['data']['story_id']

    resp2 = client.put(f'/api/stories/{story_id}', json={'visibility': 'private'},
                       headers=_auth(token), content_type='application/json')
    check('SUB-4: publish (draft→private) returns 200', resp2.status_code == 200,
          f"status={resp2.status_code} body={resp2.data}")

    # After publishing, can create a new draft
    resp3 = _create_story(client, token, world_id, title='New Draft', visibility='draft')
    check('SUB-4: can create new draft after publishing', resp3.status_code == 201,
          f"status={resp3.status_code}")


def test_my_draft_requires_auth():
    print("\n[SUB-4] GET /stories/my-draft — requires authentication...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    resp = client.get('/api/stories/my-draft')
    check('SUB-4: /my-draft without token returns 401', resp.status_code == 401,
          f"status={resp.status_code}")


# ══════════════════════════════════════════════════════════════════════════════
# SUB-4-D/E: PUT /auth/profile — signature field
# ══════════════════════════════════════════════════════════════════════════════

def test_update_profile_signature():
    print("\n[SUB-4] PUT /auth/profile — set signature...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_sig', 'sig@test.com')

    resp = client.put('/api/auth/profile', json={'signature': '— Test Author'},
                      headers=_auth(token), content_type='application/json')
    check('SUB-4: PUT /auth/profile returns 200', resp.status_code == 200,
          f"status={resp.status_code} body={resp.data}")
    if resp.status_code == 200:
        user = resp.get_json()['data']['user']
        sig = user.get('metadata', {}).get('signature')
        check('SUB-4: signature saved in user metadata', sig == '— Test Author',
              f"got: {sig}")


def test_update_profile_signature_persisted():
    print("\n[SUB-4] PUT /auth/profile — signature visible in GET /auth/me...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_sig2', 'sig2@test.com')

    put_resp = client.put('/api/auth/profile', json={'signature': '— Phuc'},
                          headers=_auth(token), content_type='application/json')
    # If PUT doesn't exist yet, skip persistence check but still record failure
    if put_resp.status_code != 200:
        check('SUB-4: PUT /auth/profile persists signature', False,
              f"PUT returned {put_resp.status_code}")
        return

    resp = client.get('/api/auth/me', headers=_auth(token))
    check('SUB-4: GET /auth/me returns 200', resp.status_code == 200,
          f"status={resp.status_code}")
    if resp.status_code == 200:
        body = resp.get_json()
        user = body.get('data') or body
        sig = user.get('metadata', {}).get('signature')
        check('SUB-4: signature visible in GET /auth/me', sig == '— Phuc', f"got: {sig}")


def test_update_profile_signature_too_long():
    print("\n[SUB-4] PUT /auth/profile — signature max length 200 chars...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_sig3', 'sig3@test.com')

    resp = client.put('/api/auth/profile', json={'signature': 'x' * 201},
                      headers=_auth(token), content_type='application/json')
    check('SUB-4: signature >200 chars rejected (400)', resp.status_code == 400,
          f"status={resp.status_code}")


def test_update_profile_requires_auth():
    print("\n[SUB-4] PUT /auth/profile — requires authentication...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    resp = client.put('/api/auth/profile', json={'signature': 'x'},
                      content_type='application/json')
    check('SUB-4: PUT /auth/profile without token returns 401', resp.status_code == 401,
          f"status={resp.status_code}")


def test_update_profile_empty_body():
    print("\n[SUB-4] PUT /auth/profile — empty body rejected...")
    backend, _ = _create_test_app()
    client = backend.app.test_client()

    token = _register_and_login(client, 'user_sig4', 'sig4@test.com')

    resp = client.put('/api/auth/profile', json={},
                      headers=_auth(token), content_type='application/json')
    check('SUB-4: PUT /auth/profile with empty body returns 400', resp.status_code == 400,
          f"status={resp.status_code}")


# ══════════════════════════════════════════════════════════════════════════════
# Runner
# ══════════════════════════════════════════════════════════════════════════════

def run_all():
    print("=" * 60)
    print("  Story Editor Page — Test Suite")
    print("=" * 60)

    test_story_model_format_field()
    test_story_create_with_format()
    test_story_update_format()
    test_patch_autosave()
    test_my_draft_empty()
    test_my_draft_returns_draft()
    test_one_draft_per_user_create()
    test_one_draft_per_user_put()
    test_publish_draft()
    test_my_draft_requires_auth()
    test_update_profile_signature()
    test_update_profile_signature_persisted()
    test_update_profile_signature_too_long()
    test_update_profile_requires_auth()
    test_update_profile_empty_body()

    passing = sum(1 for _, p in results if p)
    failing = len(results) - passing
    print("\n" + "=" * 60)
    print(f"  Results: {passing}/{len(results)} passing  |  {failing} failing")
    print("=" * 60)
    return failing


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(__file__))
    failing = run_all()
    sys.exit(0 if failing == 0 else 1)
