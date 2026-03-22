"""Tests for Phase 1 error handler contract — every error must return the standard envelope."""


def _err(resp):
    """Return the error dict from a response."""
    return resp.get_json()['error']


# ---------------------------------------------------------------------------
# Envelope structure
# ---------------------------------------------------------------------------

class TestErrorEnvelope:
    """Verify the exact JSON shape of every error response."""

    def test_404_unknown_route(self, client):
        resp = client.get('/api/nonexistent-endpoint')
        assert resp.status_code == 404
        body = resp.get_json()
        assert body['success'] is False
        assert 'error' in body
        assert 'code' in body['error']
        assert 'message' in body['error']

    def test_resource_not_found(self, client, admin_headers):
        resp = client.get('/api/worlds/does-not-exist', headers=admin_headers)
        assert resp.status_code == 404
        err = _err(resp)
        assert err['code'] == 'resource_not_found'
        assert 'World' in err['message']
        assert 'details' in err

    def test_authentication_error_missing_token(self, client):
        resp = client.post('/api/worlds',
                           json={'name': 'X', 'world_type': 'fantasy',
                                 'description': 'Ten chars+', 'visibility': 'private'})
        assert resp.status_code == 401
        err = _err(resp)
        assert err['code'] == 'authentication_error'

    def test_authentication_error_invalid_token(self, client):
        resp = client.get('/api/auth/me',
                          headers={'Authorization': 'Bearer this.is.garbage'})
        assert resp.status_code == 401
        assert resp.get_json()['success'] is False

    def test_validation_error_has_details(self, client, admin_headers):
        resp = client.post('/api/worlds',
                           json={'world_type': 'fantasy'},
                           headers=admin_headers)
        assert resp.status_code == 400
        err = _err(resp)
        assert err['code'] == 'validation_error'
        assert 'details' in err

    def test_success_response_has_data_key(self, client, admin_headers, world):
        resp = client.get(f'/api/worlds/{world["world_id"]}', headers=admin_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['success'] is True
        assert 'data' in body

    def test_created_response_is_201(self, client, admin_headers):
        resp = client.post('/api/worlds', json={
            'name': 'New World',
            'world_type': 'fantasy',
            'description': 'A new world for testing envelope',
            'visibility': 'private'
        }, headers=admin_headers)
        assert resp.status_code == 201
        body = resp.get_json()
        assert body['success'] is True
        assert 'data' in body

    def test_paginated_response_has_pagination_key(self, client):
        resp = client.get('/api/worlds')
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['success'] is True
        assert 'data' in body
        assert 'pagination' in body
        pagination = body['pagination']
        assert 'page' in pagination
        assert 'per_page' in pagination
        assert 'total' in pagination
        assert 'total_pages' in pagination

    def test_deleted_response_data_is_null(self, client, admin_headers, world):
        resp = client.delete(f'/api/worlds/{world["world_id"]}',
                             headers=admin_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['success'] is True
        assert body['data'] is None
