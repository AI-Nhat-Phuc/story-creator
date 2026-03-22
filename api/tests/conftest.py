"""Shared pytest fixtures for Phase 6 integration tests."""

import os
import sys
import tempfile
import pytest

# Ensure TEST_MODE is set before any imports
os.environ['TEST_MODE'] = '1'
os.environ['PYTHONUTF8'] = '1'

# Add api/ to sys.path so bare imports (from interfaces..., from core...) work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from interfaces.api_backend import APIBackend  # noqa: E402


@pytest.fixture(scope='function')
def app():
    """Create a fresh APIBackend with a temporary TinyDB database for each test.

    MONGODB_URI is removed so that every test runs against an isolated
    in-memory TinyDB file, regardless of environment configuration.
    """
    tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_path = tmp.name
    tmp.close()

    # Force TinyDB — load_dotenv() runs at import time, so pop AFTER imports
    original_mongo_uri = os.environ.pop('MONGODB_URI', None)
    try:
        backend = APIBackend(storage_type='nosql', db_path=db_path)
        yield backend.app
    finally:
        if original_mongo_uri:
            os.environ['MONGODB_URI'] = original_mongo_uri

    try:
        backend.storage.close()
    except Exception:
        pass
    try:
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def admin_token(client):
    resp = client.post('/api/auth/login',
                       json={'username': 'admin', 'password': 'Admin@123'})
    assert resp.status_code == 200, f"Admin login failed: {resp.data}"
    return resp.get_json()['token']


@pytest.fixture
def admin_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}'}


@pytest.fixture
def user_token(client):
    """Register and log in a standard (non-admin) user."""
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'Test@1234'
    })
    resp = client.post('/api/auth/login',
                       json={'username': 'testuser', 'password': 'Test@1234'})
    assert resp.status_code == 200
    return resp.get_json()['token']


@pytest.fixture
def user_headers(user_token):
    return {'Authorization': f'Bearer {user_token}'}


@pytest.fixture
def world(client, admin_headers):
    """Create a private test world owned by admin."""
    resp = client.post('/api/worlds', json={
        'name': 'Test World',
        'world_type': 'fantasy',
        'description': 'A magical world for testing purposes',
        'visibility': 'private'
    }, headers=admin_headers)
    assert resp.status_code == 201, f"World creation failed: {resp.data}"
    return resp.get_json()['data']


@pytest.fixture
def story(client, admin_headers, world):
    """Create a private test story in the test world."""
    resp = client.post('/api/stories', json={
        'world_id': world['world_id'],
        'title': 'Test Story',
        'description': 'A story for testing purposes',
        'genre': 'adventure',
        'visibility': 'private'
    }, headers=admin_headers)
    assert resp.status_code == 201, f"Story creation failed: {resp.data}"
    return resp.get_json()['data']['story']
