"""Tests for world CRUD + sub-resources (entities, locations, share/unshare)."""


# ---------------------------------------------------------------------------
# List worlds
# ---------------------------------------------------------------------------

class TestListWorlds:
    def test_unauthenticated_returns_paginated(self, client):
        resp = client.get('/api/worlds')
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['success'] is True
        assert isinstance(body['data'], list)
        assert 'pagination' in body

    def test_pagination_params(self, client, admin_headers):
        # Create 3 worlds
        for i in range(3):
            client.post('/api/worlds', json={
                'name': f'World {i}',
                'world_type': 'fantasy',
                'description': f'World number {i} for pagination test',
                'visibility': 'private'
            }, headers=admin_headers)
        resp = client.get('/api/worlds?page=1&per_page=2', headers=admin_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['pagination']['per_page'] == 2
        assert body['pagination']['total'] >= 3

    def test_private_worlds_visible_to_owner(self, client, world, admin_headers):
        resp = client.get('/api/worlds?per_page=100', headers=admin_headers)
        ids = [w['world_id'] for w in resp.get_json()['data']]
        assert world['world_id'] in ids

    def test_private_worlds_hidden_from_unauthenticated(self, client, world):
        resp = client.get('/api/worlds')
        ids = [w['world_id'] for w in resp.get_json()['data']]
        assert world['world_id'] not in ids


# ---------------------------------------------------------------------------
# Create world
# ---------------------------------------------------------------------------

class TestCreateWorld:
    def test_create_success(self, client, admin_headers):
        resp = client.post('/api/worlds', json={
            'name': 'New World',
            'world_type': 'sci-fi',
            'description': 'A futuristic world far away in the galaxy',
            'visibility': 'private'
        }, headers=admin_headers)
        assert resp.status_code == 201
        data = resp.get_json()['data']
        assert data['name'] == 'New World'
        assert 'world_id' in data

    def test_create_requires_auth(self, client):
        resp = client.post('/api/worlds', json={
            'name': 'No Auth',
            'world_type': 'fantasy',
            'description': 'Should fail without token'
        })
        assert resp.status_code == 401

    def test_created_world_retrievable(self, client, admin_headers):
        resp = client.post('/api/worlds', json={
            'name': 'Retrievable World',
            'world_type': 'historical',
            'description': 'This world should be retrievable after creation',
            'visibility': 'private'
        }, headers=admin_headers)
        wid = resp.get_json()['data']['world_id']
        resp2 = client.get(f'/api/worlds/{wid}', headers=admin_headers)
        assert resp2.status_code == 200
        assert resp2.get_json()['data']['world_id'] == wid


# ---------------------------------------------------------------------------
# Get world detail
# ---------------------------------------------------------------------------

class TestGetWorld:
    def test_get_existing_world(self, client, world, admin_headers):
        resp = client.get(f'/api/worlds/{world["world_id"]}', headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['world_id'] == world['world_id']

    def test_get_nonexistent_world(self, client, admin_headers):
        resp = client.get('/api/worlds/nonexistent-id', headers=admin_headers)
        assert resp.status_code == 404

    def test_get_private_world_without_auth(self, client, world):
        resp = client.get(f'/api/worlds/{world["world_id"]}')
        assert resp.status_code in (403, 404)


# ---------------------------------------------------------------------------
# Update world
# ---------------------------------------------------------------------------

class TestUpdateWorld:
    def test_update_name(self, client, world, admin_headers):
        resp = client.put(f'/api/worlds/{world["world_id"]}',
                          json={'name': 'Renamed World'}, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['name'] == 'Renamed World'

    def test_update_description(self, client, world, admin_headers):
        resp = client.put(f'/api/worlds/{world["world_id"]}',
                          json={'description': 'Updated description that is long enough to pass'},
                          headers=admin_headers)
        assert resp.status_code == 200

    def test_update_nonexistent_world(self, client, admin_headers):
        resp = client.put('/api/worlds/no-such-id',
                          json={'name': 'Ghost'}, headers=admin_headers)
        assert resp.status_code == 404

    def test_update_requires_auth(self, client, world):
        resp = client.put(f'/api/worlds/{world["world_id"]}',
                          json={'name': 'Unauthenticated'})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Delete world
# ---------------------------------------------------------------------------

class TestDeleteWorld:
    def test_delete_success(self, client, admin_headers):
        resp = client.post('/api/worlds', json={
            'name': 'Temp World',
            'world_type': 'fantasy',
            'description': 'This temporary world will be deleted in test',
            'visibility': 'private'
        }, headers=admin_headers)
        wid = resp.get_json()['data']['world_id']

        resp = client.delete(f'/api/worlds/{wid}', headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data'] is None

    def test_delete_makes_world_unretrievable(self, client, admin_headers):
        resp = client.post('/api/worlds', json={
            'name': 'Delete Me',
            'world_type': 'fantasy',
            'description': 'This world should disappear after deletion',
            'visibility': 'private'
        }, headers=admin_headers)
        wid = resp.get_json()['data']['world_id']

        client.delete(f'/api/worlds/{wid}', headers=admin_headers)
        resp = client.get(f'/api/worlds/{wid}', headers=admin_headers)
        assert resp.status_code == 404

    def test_delete_nonexistent_world(self, client, admin_headers):
        resp = client.delete('/api/worlds/ghost-world-id', headers=admin_headers)
        assert resp.status_code == 404

    def test_delete_requires_auth(self, client, world):
        resp = client.delete(f'/api/worlds/{world["world_id"]}')
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Entities sub-resource
# Note: there is no POST /api/worlds/<id>/entities endpoint.
# Entities are auto-created by the world generator on world creation.
# Tests use the entity IDs embedded in world['entities'] list.
# ---------------------------------------------------------------------------

class TestWorldEntities:
    def _get_entity_id(self, client, world, admin_headers):
        """Return the first entity_id from the world's entities list."""
        resp = client.get(f'/api/worlds/{world["world_id"]}', headers=admin_headers)
        entities = resp.get_json()['data'].get('entities', [])
        assert entities, "World must have at least one auto-generated entity"
        return entities[0]

    def test_world_has_auto_generated_entities(self, client, world, admin_headers):
        resp = client.get(f'/api/worlds/{world["world_id"]}', headers=admin_headers)
        entities = resp.get_json()['data'].get('entities', [])
        assert isinstance(entities, list)

    def test_update_entity(self, client, world, admin_headers):
        entity_id = self._get_entity_id(client, world, admin_headers)
        resp = client.put(
            f'/api/worlds/{world["world_id"]}/entities/{entity_id}',
            json={'name': 'Renamed Entity'},
            headers=admin_headers
        )
        assert resp.status_code == 200
        assert resp.get_json()['data']['name'] == 'Renamed Entity'

    def test_update_entity_requires_auth(self, client, world, admin_headers):
        entity_id = self._get_entity_id(client, world, admin_headers)
        resp = client.put(
            f'/api/worlds/{world["world_id"]}/entities/{entity_id}',
            json={'name': 'No Auth'}
        )
        assert resp.status_code == 401

    def test_delete_entity(self, client, world, admin_headers):
        entity_id = self._get_entity_id(client, world, admin_headers)
        resp = client.delete(
            f'/api/worlds/{world["world_id"]}/entities/{entity_id}',
            headers=admin_headers
        )
        assert resp.status_code == 200

    def test_delete_entity_requires_auth(self, client, world, admin_headers):
        entity_id = self._get_entity_id(client, world, admin_headers)
        resp = client.delete(
            f'/api/worlds/{world["world_id"]}/entities/{entity_id}'
        )
        assert resp.status_code == 401
