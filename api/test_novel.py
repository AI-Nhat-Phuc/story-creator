#!/usr/bin/env python
"""Integration tests for the novel feature.

Spec clauses covered:
  S1 — novel.owner_permissions
  S2 — novel.word_count_container  (API shape: chapters have word_count, not content)
  S3 — novel.word_count_list       (same API shape assertion)
  S4 — story.updated_at_put
  S5 — story.draft_resume          (response shape of GET /stories/my-draft)
  S6 — novel.reorder_validation
"""

import sys
import os
import json
import time
import tempfile

os.environ['TEST_MODE'] = '1'

from interfaces.api_backend import APIBackend


def _create_test_app():
    os.environ.pop('MONGODB_URI', None)
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    path = temp_db.name
    temp_db.close()
    backend = APIBackend(storage_type='nosql', db_path=path)
    return backend, path


def _register_and_login(client, username, email, password):
    """Register a user and return their auth token."""
    resp = client.post(
        '/api/auth/register',
        json={'username': username, 'email': email, 'password': password},
        content_type='application/json'
    )
    assert resp.status_code == 201, f"Register failed: {resp.data}"
    return resp.get_json()['token']


def _create_world(client, token, name='Test World'):
    resp = client.post(
        '/api/worlds',
        json={'name': name, 'description': 'A test world for novel tests', 'world_type': 'fantasy'},
        headers={'Authorization': f'Bearer {token}'},
        content_type='application/json'
    )
    assert resp.status_code == 201, f"Create world failed: {resp.data}"
    return resp.get_json()['data']['world_id']


def _create_story(client, token, world_id, title='Test Chapter', content='word1 word2 word3', visibility='private'):
    resp = client.post(
        '/api/stories',
        json={'world_id': world_id, 'title': title, 'content': content,
              'visibility': visibility, 'format': 'plain'},
        headers={'Authorization': f'Bearer {token}'},
        content_type='application/json'
    )
    assert resp.status_code == 201, f"Create story failed: {resp.data}"
    return resp.get_json()['data']['story_id']


# ---------------------------------------------------------------------------
# S1 — novel.owner_permissions
# ---------------------------------------------------------------------------

def test_get_novel_includes_permissions(client):
    """GET /api/worlds/:id/novel must return owner_id and co_authors (S1)."""
    print("S1 — test_get_novel_includes_permissions...")

    token = _register_and_login(client, 's1user', 's1@test.com', 'Test@1234')
    world_id = _create_world(client, token, 'Novel World S1')

    resp = client.get(
        f'/api/worlds/{world_id}/novel',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200, f"get_novel failed: {resp.data}"

    data = resp.get_json()['data']
    assert 'owner_id' in data, "Response missing 'owner_id'"
    assert 'co_authors' in data, "Response missing 'co_authors'"
    assert isinstance(data['co_authors'], list), "'co_authors' must be a list"
    assert data['owner_id'] is not None, "'owner_id' must not be null"

    print("  ✅ owner_id and co_authors present in response")


# ---------------------------------------------------------------------------
# S2 + S3 — novel.word_count_container / novel.word_count_list
# ---------------------------------------------------------------------------

def test_novel_chapters_have_word_count_not_content(client):
    """Chapters in GET /novel must have 'word_count' (int), not raw 'content' (S2, S3)."""
    print("S2+S3 — test_novel_chapters_have_word_count_not_content...")

    token = _register_and_login(client, 's23user', 's23@test.com', 'Test@1234')
    world_id = _create_world(client, token, 'Novel World S23')
    _create_story(client, token, world_id, 'Chapter One', 'alpha beta gamma delta')

    # Assign chapter_number=1 via PATCH
    story_resp = client.get(
        '/api/stories',
        headers={'Authorization': f'Bearer {token}'}
    )
    raw = story_resp.get_json()['data']
    stories = raw['items'] if isinstance(raw, dict) else raw
    story_id = next(s['story_id'] for s in stories if s['world_id'] == world_id)

    client.patch(
        f'/api/stories/{story_id}',
        json={'chapter_number': 1},
        headers={'Authorization': f'Bearer {token}'},
        content_type='application/json'
    )

    resp = client.get(
        f'/api/worlds/{world_id}/novel',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    chapters = resp.get_json()['data']['chapters']
    assert len(chapters) >= 1, "Expected at least one chapter"

    chapter = chapters[0]
    assert 'word_count' in chapter, "Chapter must have 'word_count' field"
    assert isinstance(chapter['word_count'], int), "'word_count' must be int"
    assert chapter['word_count'] >= 0, "'word_count' must be >= 0"
    assert 'content' not in chapter, "Chapter must NOT expose raw 'content' (use word_count)"
    assert chapter['word_count'] == 4, f"Expected 4 words, got {chapter['word_count']}"

    print(f"  ✅ chapter.word_count={chapter['word_count']}, no 'content' field")


# ---------------------------------------------------------------------------
# S4 — story.updated_at_put
# ---------------------------------------------------------------------------

def test_update_story_put_refreshes_updated_at(client):
    """PUT /api/stories/:id must refresh updated_at (S4)."""
    print("S4 — test_update_story_put_refreshes_updated_at...")

    token = _register_and_login(client, 's4user', 's4@test.com', 'Test@1234')
    world_id = _create_world(client, token, 'Novel World S4')
    story_id = _create_story(client, token, world_id, 'S4 Story', 'initial content')

    # Get original updated_at
    get_resp = client.get(
        f'/api/stories/{story_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    original_updated_at = get_resp.get_json()['data']['updated_at']

    time.sleep(0.01)  # ensure clock advances

    # Update via PUT
    put_resp = client.put(
        f'/api/stories/{story_id}',
        json={'title': 'S4 Story Updated'},
        headers={'Authorization': f'Bearer {token}'},
        content_type='application/json'
    )
    assert put_resp.status_code == 200, f"PUT failed: {put_resp.data}"

    new_updated_at = put_resp.get_json()['data']['updated_at']
    assert new_updated_at is not None, "'updated_at' must be in PUT response"
    assert new_updated_at != original_updated_at, (
        f"updated_at must change after PUT: before={original_updated_at}, after={new_updated_at}"
    )

    print(f"  ✅ updated_at refreshed: {original_updated_at} → {new_updated_at}")


# ---------------------------------------------------------------------------
# S5 — story.draft_resume
# ---------------------------------------------------------------------------

def test_get_my_draft_response_shape(client):
    """GET /api/stories/my-draft must return { story: {...}|null } not { story_id: ... } (S5)."""
    print("S5 — test_get_my_draft_response_shape...")

    token = _register_and_login(client, 's5user', 's5@test.com', 'Test@1234')

    # No draft yet — story should be null
    resp = client.get(
        '/api/stories/my-draft',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200, f"my-draft failed: {resp.data}"
    data = resp.get_json()['data']
    assert 'story' in data, "Response must have 'story' key (not story_id at top level)"
    assert data['story'] is None, "Should be null when no draft exists"

    # Create a draft story
    world_id = _create_world(client, token, 'Novel World S5')
    story_id = _create_story(client, token, world_id, 'My Draft', 'draft content', visibility='draft')

    resp2 = client.get(
        '/api/stories/my-draft',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp2.status_code == 200
    data2 = resp2.get_json()['data']
    assert 'story' in data2, "Response must have 'story' key"
    assert data2['story'] is not None, "Story must not be null when draft exists"
    assert 'story_id' in data2['story'], "story_id must be inside 'story' dict"
    assert data2['story']['story_id'] == story_id

    # Verify top-level does NOT have story_id (old broken shape)
    assert 'story_id' not in data2, (
        "story_id must NOT be at top level of data — frontend reads data.story.story_id"
    )

    print(f"  ✅ response shape: data.story.story_id = {data2['story']['story_id']}")


# ---------------------------------------------------------------------------
# S6 — novel.reorder_validation
# ---------------------------------------------------------------------------

def test_reorder_chapters_ignores_foreign_stories(client):
    """PATCH reorder_chapters must not set chapter_number on stories from other worlds (S6)."""
    print("S6 — test_reorder_chapters_ignores_foreign_stories...")

    token = _register_and_login(client, 's6user', 's6@test.com', 'Test@1234')

    world1_id = _create_world(client, token, 'World One S6')
    world2_id = _create_world(client, token, 'World Two S6')

    story1_id = _create_story(client, token, world1_id, 'Story W1', 'content w1')
    story2_id = _create_story(client, token, world2_id, 'Story W2', 'content w2')

    # Reorder world1 chapters but include story2 (which belongs to world2)
    resp = client.patch(
        f'/api/worlds/{world1_id}/novel/chapters',
        json={'order': [story1_id, story2_id]},
        headers={'Authorization': f'Bearer {token}'},
        content_type='application/json'
    )
    assert resp.status_code == 200, f"Reorder failed: {resp.data}"
    updated = resp.get_json()['data']['chapters']

    updated_ids = [c['story_id'] for c in updated]
    assert story1_id in updated_ids, "story1 (belongs to world1) must be updated"
    assert story2_id not in updated_ids, "story2 (belongs to world2) must be skipped"

    # Verify story2 chapter_number was NOT modified
    s2_resp = client.get(
        f'/api/stories/{story2_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    s2_data = s2_resp.get_json()['data']
    assert s2_data.get('chapter_number') is None, (
        f"story2.chapter_number must remain None, got {s2_data.get('chapter_number')}"
    )

    print(f"  ✅ story2 chapter_number unchanged, story1 updated to chapter 1")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("  NOVEL — TEST SUITE")
    print("=" * 70 + "\n")

    backend, temp_db_path = _create_test_app()
    results = []

    try:
        backend.storage.clear_all()
        with backend.app.test_client() as client:
            tests = [
                test_get_novel_includes_permissions,
                test_novel_chapters_have_word_count_not_content,
                test_update_story_put_refreshes_updated_at,
                test_get_my_draft_response_shape,
                test_reorder_chapters_ignores_foreign_stories,
            ]
            for fn in tests:
                try:
                    fn(client)
                    results.append((fn.__name__, True, None))
                except AssertionError as e:
                    results.append((fn.__name__, False, str(e)))
                    import traceback; traceback.print_exc()
                except Exception as e:
                    results.append((fn.__name__, False, str(e)))
                    import traceback; traceback.print_exc()

    finally:
        try:
            backend.storage.close()
        except Exception:
            pass
        if os.path.exists(temp_db_path):
            try:
                os.unlink(temp_db_path)
            except PermissionError:
                pass

    print("\n" + "=" * 70)
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    for name, ok, err in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {name}" + (f": {err}" if err else ""))
    print(f"\n  {passed}/{total} tests passed")
    print("=" * 70)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
