"""Tests for admin routes — user list, role change, ban."""


# ---------------------------------------------------------------------------
# GET /api/admin/users
# ---------------------------------------------------------------------------

class TestListUsers:
    def test_admin_gets_paginated_user_list(self, client, admin_headers):
        resp = client.get('/api/admin/users', headers=admin_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['success'] is True
        assert isinstance(body['data'], list)
        assert 'pagination' in body

    def test_admin_list_contains_admin_user(self, client, admin_headers):
        resp = client.get('/api/admin/users', headers=admin_headers)
        usernames = [u['username'] for u in resp.get_json()['data']]
        assert 'admin' in usernames

    def test_passwords_not_in_response(self, client, admin_headers):
        resp = client.get('/api/admin/users', headers=admin_headers)
        for user in resp.get_json()['data']:
            assert 'password_hash' not in user

    def test_regular_user_forbidden(self, client, user_headers):
        resp = client.get('/api/admin/users', headers=user_headers)
        assert resp.status_code == 403

    def test_unauthenticated_forbidden(self, client):
        resp = client.get('/api/admin/users')
        assert resp.status_code == 401

    def test_pagination_params_respected(self, client, admin_headers, user_token):
        # There are at least 2 users now (admin + testuser created by user_token fixture)
        resp = client.get('/api/admin/users?per_page=1', headers=admin_headers)
        body = resp.get_json()
        assert body['pagination']['per_page'] == 1
        assert len(body['data']) == 1


# ---------------------------------------------------------------------------
# GET /api/admin/users/<id>
# ---------------------------------------------------------------------------

class TestGetUserDetail:
    def test_admin_can_get_user_detail(self, client, admin_headers, user_token):
        resp = client.get('/api/auth/me',
                          headers={'Authorization': f'Bearer {user_token}'})
        user_id = resp.get_json()['user']['user_id']

        resp = client.get(f'/api/admin/users/{user_id}', headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['user']['user_id'] == user_id

    def test_get_nonexistent_user(self, client, admin_headers):
        resp = client.get('/api/admin/users/no-such-user', headers=admin_headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/admin/users/<id>/role
# ---------------------------------------------------------------------------

class TestChangeUserRole:
    def test_admin_can_change_role(self, client, admin_headers, user_token):
        resp = client.get('/api/auth/me',
                          headers={'Authorization': f'Bearer {user_token}'})
        user_id = resp.get_json()['user']['user_id']

        resp = client.put(f'/api/admin/users/{user_id}/role',
                          json={'role': 'moderator'}, headers=admin_headers)
        assert resp.status_code == 200

    def test_invalid_role_rejected(self, client, admin_headers, user_token):
        resp = client.get('/api/auth/me',
                          headers={'Authorization': f'Bearer {user_token}'})
        user_id = resp.get_json()['user']['user_id']

        resp = client.put(f'/api/admin/users/{user_id}/role',
                          json={'role': 'superadmin'}, headers=admin_headers)
        assert resp.status_code == 400
        assert resp.get_json()['error']['code'] == 'validation_error'

    def test_missing_role_rejected(self, client, admin_headers, user_token):
        resp = client.get('/api/auth/me',
                          headers={'Authorization': f'Bearer {user_token}'})
        user_id = resp.get_json()['user']['user_id']

        resp = client.put(f'/api/admin/users/{user_id}/role',
                          json={}, headers=admin_headers)
        assert resp.status_code == 400

    def test_regular_user_cannot_change_role(self, client, user_headers, user_token):
        resp = client.get('/api/auth/me',
                          headers={'Authorization': f'Bearer {user_token}'})
        user_id = resp.get_json()['user']['user_id']

        resp = client.put(f'/api/admin/users/{user_id}/role',
                          json={'role': 'admin'}, headers=user_headers)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /api/admin/users/<id>/ban
# ---------------------------------------------------------------------------

class TestBanUser:
    def test_admin_can_ban_user(self, client, admin_headers, user_token):
        resp = client.get('/api/auth/me',
                          headers={'Authorization': f'Bearer {user_token}'})
        user_id = resp.get_json()['user']['user_id']

        resp = client.post(f'/api/admin/users/{user_id}/ban',
                           json={'reason': 'Test ban', 'banned': True},
                           headers=admin_headers)
        assert resp.status_code == 200

    def test_regular_user_cannot_ban(self, client, user_headers, user_token):
        resp = client.get('/api/auth/me',
                          headers={'Authorization': f'Bearer {user_token}'})
        user_id = resp.get_json()['user']['user_id']

        resp = client.post(f'/api/admin/users/{user_id}/ban',
                           json={'reason': 'Unauthorized ban', 'banned': True},
                           headers=user_headers)
        assert resp.status_code == 403
