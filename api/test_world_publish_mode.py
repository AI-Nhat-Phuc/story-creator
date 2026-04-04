#!/usr/bin/env python
"""Tests for world publish mode feature.

Spec clauses covered:
  1. Default visibility when creating a world without specifying visibility → 'draft'
  2. Publish: owner can update world visibility from draft → private
  3. Publish: owner can update world visibility from draft → public
  4. Draft world is not visible to unauthenticated users
  5. Draft world is not visible to other authenticated users
"""

import sys
import os
import json
import tempfile

os.environ['TEST_MODE'] = '1'

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from interfaces.api_backend import APIBackend


def _create_test_app():
    os.environ.pop('MONGODB_URI', None)
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()
    backend = APIBackend(storage_type='nosql', db_path=temp_db_path)
    return backend, temp_db_path


def _register_and_login(client, username, password='Test@1234', email=None):
    email = email or f'{username}@test.com'
    client.post('/api/auth/register', json={
        'username': username, 'email': email, 'password': password
    }, content_type='application/json')
    resp = client.post('/api/auth/login', json={
        'username': username, 'password': password
    }, content_type='application/json')
    assert resp.status_code == 200, f"Login failed for {username}: {resp.data}"
    return resp.get_json()['token']


def _create_world(client, token, **kwargs):
    payload = {
        'name': 'Test World',
        'world_type': 'fantasy',
        'description': 'A world for publish mode testing',
    }
    payload.update(kwargs)
    return client.post('/api/worlds', json=payload,
                       headers={'Authorization': f'Bearer {token}'},
                       content_type='application/json')


# ---------------------------------------------------------------------------
# Test 1: Default visibility is 'draft'
# ---------------------------------------------------------------------------

def test_create_world_defaults_to_draft(client):
    """Spec: Default khi tạo: draft"""
    print("\nTest 1: Create world without visibility → defaults to draft...")

    token = _register_and_login(client, 'user_draft')
    resp = _create_world(client, token)  # no visibility field

    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.data}"
    world = resp.get_json()['data']
    assert world['visibility'] == 'draft', (
        f"Expected visibility='draft', got '{world['visibility']}'"
    )
    print("✅ Test 1 passed")


# ---------------------------------------------------------------------------
# Test 2: Owner can publish draft → private
# ---------------------------------------------------------------------------

def test_publish_draft_to_private(client):
    """Spec: Owner có thể chuyển draft → private"""
    print("\nTest 2: Publish draft world to private...")

    token = _register_and_login(client, 'user_priv')
    world_id = _create_world(client, token).get_json()['data']['world_id']

    resp = client.put(f'/api/worlds/{world_id}',
                      json={'visibility': 'private'},
                      headers={'Authorization': f'Bearer {token}'},
                      content_type='application/json')

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.data}"
    updated = resp.get_json()['data']
    assert updated['visibility'] == 'private', (
        f"Expected 'private', got '{updated['visibility']}'"
    )
    print("✅ Test 2 passed")


# ---------------------------------------------------------------------------
# Test 3: Owner can publish draft → public
# ---------------------------------------------------------------------------

def test_publish_draft_to_public(client):
    """Spec: Owner có thể chuyển draft → public (nếu còn quota)"""
    print("\nTest 3: Publish draft world to public...")

    token = _register_and_login(client, 'user_pub')
    world_id = _create_world(client, token).get_json()['data']['world_id']

    resp = client.put(f'/api/worlds/{world_id}',
                      json={'visibility': 'public'},
                      headers={'Authorization': f'Bearer {token}'},
                      content_type='application/json')

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.data}"
    updated = resp.get_json()['data']
    assert updated['visibility'] == 'public', (
        f"Expected 'public', got '{updated['visibility']}'"
    )
    print("✅ Test 3 passed")


# ---------------------------------------------------------------------------
# Test 4: Draft world not visible to unauthenticated users
# ---------------------------------------------------------------------------

def test_draft_world_hidden_from_unauthenticated(client):
    """Spec: Draft world chỉ owner thấy"""
    print("\nTest 4: Draft world hidden from unauthenticated users...")

    token = _register_and_login(client, 'user_owner4')
    world_id = _create_world(client, token).get_json()['data']['world_id']

    resp = client.get(f'/api/worlds/{world_id}')  # no auth
    assert resp.status_code in (403, 404), (
        f"Expected 403 or 404 for unauthenticated access to draft, got {resp.status_code}"
    )
    print("✅ Test 4 passed")


# ---------------------------------------------------------------------------
# Test 5: Draft world not visible to other authenticated users
# ---------------------------------------------------------------------------

def test_draft_world_hidden_from_other_users(client):
    """Spec: Draft world chỉ owner thấy — không ai khác"""
    print("\nTest 5: Draft world hidden from other authenticated users...")

    owner_token = _register_and_login(client, 'user_owner5')
    other_token = _register_and_login(client, 'user_other5')

    world_id = _create_world(client, owner_token).get_json()['data']['world_id']

    resp = client.get(f'/api/worlds/{world_id}',
                      headers={'Authorization': f'Bearer {other_token}'})
    assert resp.status_code in (403, 404), (
        f"Expected 403 or 404 for other user accessing draft, got {resp.status_code}"
    )
    print("✅ Test 5 passed")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("  WORLD PUBLISH MODE — TEST SUITE")
    print("=" * 70 + "\n")

    backend, temp_db_path = _create_test_app()
    passed = 0
    failed = 0

    try:
        backend.storage.clear_all()
        with backend.app.test_client() as client:
            tests = [
                test_create_world_defaults_to_draft,
                test_publish_draft_to_private,
                test_publish_draft_to_public,
                test_draft_world_hidden_from_unauthenticated,
                test_draft_world_hidden_from_other_users,
            ]
            for t in tests:
                try:
                    t(client)
                    passed += 1
                except AssertionError as e:
                    print(f"  ❌ FAIL: {t.__name__}: {e}")
                    failed += 1

    finally:
        try:
            os.unlink(temp_db_path)
        except OSError:
            pass

    print(f"\n{'=' * 70}")
    print(f"  Results: {passed} passed, {failed} failed")
    print('=' * 70)
    return 1 if failed > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
