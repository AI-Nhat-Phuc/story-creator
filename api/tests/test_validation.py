"""Tests for Phase 1/5 Marshmallow schema rejection — bad input must return 400 validation_error."""


def _is_validation_error(resp):
    assert resp.status_code == 400
    body = resp.get_json()
    assert body['success'] is False
    assert body['error']['code'] == 'validation_error'
    return body['error']


# ---------------------------------------------------------------------------
# World schemas
# ---------------------------------------------------------------------------

class TestCreateWorldValidation:
    def test_missing_name(self, client, admin_headers):
        resp = client.post('/api/worlds', json={
            'world_type': 'fantasy',
            'description': 'A world without a name'
        }, headers=admin_headers)
        err = _is_validation_error(resp)
        assert 'name' in err['details']

    def test_missing_world_type(self, client, admin_headers):
        resp = client.post('/api/worlds', json={
            'name': 'No Type World',
            'description': 'A world without a type'
        }, headers=admin_headers)
        err = _is_validation_error(resp)
        assert 'world_type' in err['details']

    def test_invalid_world_type(self, client, admin_headers):
        resp = client.post('/api/worlds', json={
            'name': 'Bad Type',
            'world_type': 'underwater',
            'description': 'An invalid world type here'
        }, headers=admin_headers)
        err = _is_validation_error(resp)
        assert 'world_type' in err['details']

    def test_description_too_short(self, client, admin_headers):
        resp = client.post('/api/worlds', json={
            'name': 'Short Desc',
            'world_type': 'fantasy',
            'description': 'Too short'
        }, headers=admin_headers)
        err = _is_validation_error(resp)
        assert 'description' in err['details']

    def test_invalid_visibility(self, client, admin_headers):
        resp = client.post('/api/worlds', json={
            'name': 'Bad Visibility',
            'world_type': 'fantasy',
            'description': 'A world with invalid visibility value',
            'visibility': 'secret'
        }, headers=admin_headers)
        err = _is_validation_error(resp)
        assert 'visibility' in err['details']


class TestUpdateWorldValidation:
    def test_empty_body_rejected(self, client, admin_headers, world):
        resp = client.put(f'/api/worlds/{world["world_id"]}',
                          json={}, headers=admin_headers)
        _is_validation_error(resp)

    def test_invalid_visibility_on_update(self, client, admin_headers, world):
        resp = client.put(f'/api/worlds/{world["world_id"]}',
                          json={'visibility': 'hidden'}, headers=admin_headers)
        err = _is_validation_error(resp)
        assert 'visibility' in err['details']


# ---------------------------------------------------------------------------
# Story schemas
# ---------------------------------------------------------------------------

class TestCreateStoryValidation:
    def test_missing_world_id(self, client, admin_headers):
        resp = client.post('/api/stories', json={
            'title': 'No World Story',
            'genre': 'adventure'
        }, headers=admin_headers)
        err = _is_validation_error(resp)
        assert 'world_id' in err['details']

    def test_missing_title(self, client, admin_headers, world):
        resp = client.post('/api/stories', json={
            'world_id': world['world_id'],
            'genre': 'adventure'
        }, headers=admin_headers)
        err = _is_validation_error(resp)
        assert 'title' in err['details']


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class TestRegisterValidation:
    def test_missing_username(self, client):
        resp = client.post('/api/auth/register', json={
            'email': 'x@x.com',
            'password': 'ValidPass@1'
        })
        err = _is_validation_error(resp)
        assert 'username' in err['details']

    def test_missing_email(self, client):
        resp = client.post('/api/auth/register', json={
            'username': 'nomail',
            'password': 'ValidPass@1'
        })
        err = _is_validation_error(resp)
        assert 'email' in err['details']

    def test_missing_password(self, client):
        resp = client.post('/api/auth/register', json={
            'username': 'nopass',
            'email': 'nopass@example.com'
        })
        err = _is_validation_error(resp)
        assert 'password' in err['details']


class TestLoginValidation:
    def test_missing_username(self, client):
        resp = client.post('/api/auth/login', json={'password': 'something'})
        err = _is_validation_error(resp)
        assert 'username' in err['details']

    def test_missing_password(self, client):
        resp = client.post('/api/auth/login', json={'username': 'admin'})
        err = _is_validation_error(resp)
        assert 'password' in err['details']


# ---------------------------------------------------------------------------
# Entity schemas (PUT endpoint only — no POST /entities endpoint exists)
# ---------------------------------------------------------------------------

class TestUpdateEntityValidation:
    def _get_entity_id(self, client, world, admin_headers):
        resp = client.get(f'/api/worlds/{world["world_id"]}', headers=admin_headers)
        entities = resp.get_json()['data'].get('entities', [])
        assert entities, "World must have auto-generated entities"
        return entities[0]

    def test_update_entity_empty_body_rejected(self, client, admin_headers, world):
        entity_id = self._get_entity_id(client, world, admin_headers)
        resp = client.put(
            f'/api/worlds/{world["world_id"]}/entities/{entity_id}',
            json={}, headers=admin_headers
        )
        _is_validation_error(resp)
