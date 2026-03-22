"""Tests for Phase 5 permission enforcement — cross-user authorization matrix."""

import pytest


@pytest.fixture
def other_user_token(client):
    """Register a second user 'otheruser'."""
    client.post('/api/auth/register', json={
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'Other@1234'
    })
    resp = client.post('/api/auth/login',
                       json={'username': 'otheruser', 'password': 'Other@1234'})
    return resp.get_json()['token']


@pytest.fixture
def other_headers(other_user_token):
    return {'Authorization': f'Bearer {other_user_token}'}


@pytest.fixture
def public_world(client, user_headers):
    """Create a public world owned by a regular user (admin has public_worlds_limit=0)."""
    resp = client.post('/api/worlds', json={
        'name': 'Public World',
        'world_type': 'modern',
        'description': 'A public world visible to everyone',
        'visibility': 'public'
    }, headers=user_headers)
    assert resp.status_code == 201, f"Public world creation failed: {resp.data}"
    return resp.get_json()['data']


# ---------------------------------------------------------------------------
# World visibility
# ---------------------------------------------------------------------------

class TestWorldVisibility:
    def test_private_world_hidden_from_unauthenticated(self, client, world):
        resp = client.get(f'/api/worlds/{world["world_id"]}')
        assert resp.status_code in (403, 404)

    def test_private_world_hidden_from_other_user(self, client, world, other_headers):
        resp = client.get(f'/api/worlds/{world["world_id"]}', headers=other_headers)
        assert resp.status_code in (403, 404)

    def test_private_world_visible_to_owner(self, client, world, admin_headers):
        resp = client.get(f'/api/worlds/{world["world_id"]}', headers=admin_headers)
        assert resp.status_code == 200

    def test_public_world_visible_to_unauthenticated(self, client, public_world):
        resp = client.get(f'/api/worlds/{public_world["world_id"]}')
        assert resp.status_code == 200

    def test_public_world_visible_to_other_user(self, client, public_world, other_headers):
        resp = client.get(f'/api/worlds/{public_world["world_id"]}', headers=other_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# World mutations — only owner can modify
# ---------------------------------------------------------------------------

class TestWorldMutationPermissions:
    def test_other_user_cannot_update_world(self, client, world, other_headers):
        resp = client.put(f'/api/worlds/{world["world_id"]}',
                          json={'name': 'Hijacked Name'}, headers=other_headers)
        assert resp.status_code == 403

    def test_other_user_cannot_delete_world(self, client, world, other_headers):
        resp = client.delete(f'/api/worlds/{world["world_id"]}', headers=other_headers)
        assert resp.status_code == 403

    def test_unauthenticated_cannot_update_world(self, client, world):
        resp = client.put(f'/api/worlds/{world["world_id"]}',
                          json={'name': 'No Auth Name'})
        assert resp.status_code == 401

    def test_unauthenticated_cannot_delete_world(self, client, world):
        resp = client.delete(f'/api/worlds/{world["world_id"]}')
        assert resp.status_code == 401

    def test_owner_can_update_world(self, client, world, admin_headers):
        resp = client.put(f'/api/worlds/{world["world_id"]}',
                          json={'name': 'Updated Name'}, headers=admin_headers)
        assert resp.status_code == 200

    def test_owner_can_delete_world(self, client, admin_headers):
        # Create a separate world so we don't break other tests
        resp = client.post('/api/worlds', json={
            'name': 'Delete Me',
            'world_type': 'fantasy',
            'description': 'This world will be deleted in the test',
            'visibility': 'private'
        }, headers=admin_headers)
        wid = resp.get_json()['data']['world_id']
        resp = client.delete(f'/api/worlds/{wid}', headers=admin_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Admin-only routes
# ---------------------------------------------------------------------------

class TestAdminPermissions:
    def test_regular_user_cannot_list_users(self, client, user_headers):
        resp = client.get('/api/admin/users', headers=user_headers)
        assert resp.status_code == 403

    def test_unauthenticated_cannot_list_users(self, client):
        resp = client.get('/api/admin/users')
        assert resp.status_code == 401

    def test_admin_can_list_users(self, client, admin_headers):
        resp = client.get('/api/admin/users', headers=admin_headers)
        assert resp.status_code == 200

    def test_regular_user_cannot_change_role(self, client, user_headers, user_token):
        # Get user id first (via /api/auth/me)
        resp = client.get('/api/auth/me',
                          headers={'Authorization': f'Bearer {user_token}'})
        user_id = resp.get_json()['user']['user_id']
        resp = client.put(f'/api/admin/users/{user_id}/role',
                          json={'role': 'editor'}, headers=user_headers)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Story permissions
# ---------------------------------------------------------------------------

class TestStoryPermissions:
    def test_unauthenticated_cannot_create_story(self, client, world):
        resp = client.post('/api/stories', json={
            'world_id': world['world_id'],
            'title': 'No Auth Story',
            'genre': 'adventure'
        })
        assert resp.status_code == 401

    def test_other_user_cannot_delete_story(self, client, story, other_headers):
        resp = client.delete(f'/api/stories/{story["story_id"]}', headers=other_headers)
        assert resp.status_code == 403
