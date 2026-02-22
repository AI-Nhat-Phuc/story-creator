#!/usr/bin/env python
"""Test script to verify API endpoint logic using Flask test client."""

import sys
import os
import json
import tempfile

# Set TEST_MODE to allow database clearing
os.environ['TEST_MODE'] = '1'

from interfaces.api_backend import APIBackend


def _create_test_app():
    """Create a test APIBackend with a temporary database."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()
    backend = APIBackend(db_path=temp_db_path)
    return backend, temp_db_path


def _login_admin(client):
    """Login as the default admin and return the Bearer token."""
    resp = client.post(
        '/api/auth/login',
        json={'username': 'admin', 'password': 'Admin@123'},
        content_type='application/json'
    )
    assert resp.status_code == 200, f"Admin login failed: {resp.data}"
    data = resp.get_json()
    return data['token']


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health(client):
    """GET /api/health should return status ok."""
    print("Testing health endpoint...")
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'ok'
    assert 'storage' in data
    assert 'gpt_enabled' in data
    print("✅ Health endpoint passed")


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def test_auth_register_and_login(client):
    """Test user registration and login flow."""
    print("\nTesting auth register and login...")

    # Register a new user
    resp = client.post(
        '/api/auth/register',
        json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        },
        content_type='application/json'
    )
    assert resp.status_code == 201, f"Register failed: {resp.data}"
    reg_data = resp.get_json()
    assert reg_data['success'] is True
    assert 'token' in reg_data
    assert reg_data['user']['username'] == 'testuser'

    # Login with the new user
    resp = client.post(
        '/api/auth/login',
        json={'username': 'testuser', 'password': 'Test@1234'},
        content_type='application/json'
    )
    assert resp.status_code == 200
    login_data = resp.get_json()
    assert login_data['success'] is True
    assert 'token' in login_data

    # Login with wrong password
    resp = client.post(
        '/api/auth/login',
        json={'username': 'testuser', 'password': 'wrongpassword'},
        content_type='application/json'
    )
    assert resp.status_code == 401

    # Duplicate registration
    resp = client.post(
        '/api/auth/register',
        json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        },
        content_type='application/json'
    )
    assert resp.status_code == 400

    print("✅ Auth register and login passed")


def test_auth_verify_and_me(client):
    """Test token verification and current user endpoint."""
    print("\nTesting auth verify and me...")

    token = _login_admin(client)
    headers = {'Authorization': f'Bearer {token}'}

    # Verify token
    resp = client.get('/api/auth/verify', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['user']['username'] == 'admin'

    # Get current user
    resp = client.get('/api/auth/me', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['user']['username'] == 'admin'

    # Invalid token
    resp = client.get('/api/auth/verify', headers={'Authorization': 'Bearer invalidtoken'})
    assert resp.status_code == 401

    # Missing token
    resp = client.get('/api/auth/me')
    assert resp.status_code == 401

    print("✅ Auth verify and me passed")


# ---------------------------------------------------------------------------
# Worlds
# ---------------------------------------------------------------------------

def test_worlds_crud(client):
    """Test world CRUD endpoints."""
    print("\nTesting worlds CRUD...")

    token = _login_admin(client)
    headers = {'Authorization': f'Bearer {token}'}

    # List worlds (initially only worlds visible to admin)
    resp = client.get('/api/worlds')
    assert resp.status_code == 200
    worlds_before = resp.get_json()
    assert isinstance(worlds_before, list)

    # Create a private world
    resp = client.post(
        '/api/worlds',
        json={
            'name': 'Test World',
            'world_type': 'fantasy',
            'description': 'A magical world for testing',
            'visibility': 'private'
        },
        headers=headers,
        content_type='application/json'
    )
    assert resp.status_code == 201, f"Create world failed: {resp.data}"
    world = resp.get_json()
    assert world['name'] == 'Test World'
    world_id = world['world_id']

    # Get the world detail (as owner)
    resp = client.get(f'/api/worlds/{world_id}', headers=headers)
    assert resp.status_code == 200
    detail = resp.get_json()
    assert detail['world_id'] == world_id

    # Unauthenticated access to private world should be denied
    resp = client.get(f'/api/worlds/{world_id}')
    assert resp.status_code in (403, 404)

    # List worlds as authenticated admin should include new world
    resp = client.get('/api/worlds', headers=headers)
    assert resp.status_code == 200
    worlds_after = resp.get_json()
    ids = [w['world_id'] for w in worlds_after]
    assert world_id in ids

    # Non-existent world
    resp = client.get('/api/worlds/non-existent-id', headers=headers)
    assert resp.status_code == 404

    # Create without auth should fail
    resp = client.post(
        '/api/worlds',
        json={'name': 'No Auth World', 'world_type': 'fantasy'},
        content_type='application/json'
    )
    assert resp.status_code == 401

    print("✅ Worlds CRUD passed")


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------

def test_stories_crud(client):
    """Test story CRUD endpoints."""
    print("\nTesting stories CRUD...")

    token = _login_admin(client)
    headers = {'Authorization': f'Bearer {token}'}

    # Create a world first
    resp = client.post(
        '/api/worlds',
        json={
            'name': 'Story World',
            'world_type': 'fantasy',
            'description': 'World for story tests',
            'visibility': 'private'
        },
        headers=headers,
        content_type='application/json'
    )
    assert resp.status_code == 201
    world_id = resp.get_json()['world_id']

    # List stories
    resp = client.get('/api/stories')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

    # Create a story
    resp = client.post(
        '/api/stories',
        json={
            'world_id': world_id,
            'title': 'Test Story',
            'description': 'A thrilling adventure',
            'genre': 'adventure',
            'visibility': 'private'
        },
        headers=headers,
        content_type='application/json'
    )
    assert resp.status_code == 201, f"Create story failed: {resp.data}"
    story = resp.get_json()['story']
    assert story['title'] == 'Test Story'
    story_id = story['story_id']

    # Get the story detail
    resp = client.get(f'/api/stories/{story_id}', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['story_id'] == story_id

    # Create story without auth
    resp = client.post(
        '/api/stories',
        json={'world_id': world_id, 'title': 'No Auth', 'genre': 'adventure'},
        content_type='application/json'
    )
    assert resp.status_code == 401

    # Story in non-existent world
    resp = client.post(
        '/api/stories',
        json={'world_id': 'fake-world-id', 'title': 'Bad Story', 'genre': 'adventure'},
        headers=headers,
        content_type='application/json'
    )
    assert resp.status_code == 404

    print("✅ Stories CRUD passed")


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def test_stats(client):
    """Test stats endpoint."""
    print("\nTesting stats endpoint...")

    # Anonymous access
    resp = client.get('/api/stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'total_worlds' in data
    assert 'total_stories' in data
    assert 'has_gpt' in data
    assert 'storage_type' in data
    assert 'breakdown' in data

    # Authenticated access includes extra breakdown fields
    token = _login_admin(client)
    resp = client.get('/api/stats', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    auth_data = resp.get_json()
    assert 'breakdown' in auth_data
    assert 'worlds' in auth_data['breakdown']
    assert 'stories' in auth_data['breakdown']

    print("✅ Stats endpoint passed")


# ---------------------------------------------------------------------------
# GPT routes (without actual GPT)
# ---------------------------------------------------------------------------

def test_gpt_results_not_found(client):
    """GET /api/gpt/results/<task_id> with unknown id should return 404."""
    print("\nTesting GPT results not found...")
    resp = client.get('/api/gpt/results/non-existent-task-id')
    assert resp.status_code == 404
    data = resp.get_json()
    assert 'error' in data
    print("✅ GPT results not found passed")


def test_gpt_unavailable(client):
    """GPT endpoints return 503 when GPT is not configured."""
    print("\nTesting GPT unavailable responses...")

    # generate-description
    resp = client.post(
        '/api/gpt/generate-description',
        json={'type': 'world', 'world_name': 'Test', 'world_type': 'fantasy'},
        content_type='application/json'
    )
    assert resp.status_code == 503
    assert resp.get_json()['error'] == 'GPT not available'

    # analyze
    resp = client.post(
        '/api/gpt/analyze',
        json={'world_description': 'A kingdom with three kings'},
        content_type='application/json'
    )
    assert resp.status_code == 503

    # batch-analyze-stories
    resp = client.post(
        '/api/gpt/batch-analyze-stories',
        json={'world_id': 'some-world-id'},
        content_type='application/json'
    )
    assert resp.status_code == 503

    print("✅ GPT unavailable responses passed")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run all API tests."""
    print("=" * 70)
    print("  STORY CREATOR - API TEST SUITE")
    print("=" * 70 + "\n")

    backend, temp_db_path = _create_test_app()
    try:
        backend.storage.clear_all()
        with backend.app.test_client() as client:
            test_health(client)
            test_auth_register_and_login(client)
            test_auth_verify_and_me(client)
            test_worlds_crud(client)
            test_stories_crud(client)
            test_stats(client)
            test_gpt_results_not_found(client)
            test_gpt_unavailable(client)

        print("\n" + "=" * 70)
        print("  ✅ ALL API TESTS PASSED")
        print("=" * 70)
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        try:
            backend.storage.close()
        except Exception:
            pass
        if os.path.exists(temp_db_path):
            try:
                os.unlink(temp_db_path)
            except PermissionError:
                print(f"   ⚠️  Could not delete temp file: {temp_db_path}")


if __name__ == "__main__":
    sys.exit(main())
