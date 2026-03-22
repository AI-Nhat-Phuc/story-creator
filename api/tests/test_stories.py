"""Tests for story CRUD + link-entities + clear-links."""


# ---------------------------------------------------------------------------
# List stories
# ---------------------------------------------------------------------------

class TestListStories:
    def test_list_returns_paginated(self, client):
        resp = client.get('/api/stories')
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['success'] is True
        assert isinstance(body['data'], list)
        assert 'pagination' in body

    def test_created_story_appears_in_list(self, client, story, admin_headers):
        resp = client.get('/api/stories?per_page=100', headers=admin_headers)
        ids = [s['story_id'] for s in resp.get_json()['data']]
        assert story['story_id'] in ids


# ---------------------------------------------------------------------------
# Create story
# ---------------------------------------------------------------------------

class TestCreateStory:
    def test_create_success(self, client, world, admin_headers):
        resp = client.post('/api/stories', json={
            'world_id': world['world_id'],
            'title': 'The Beginning',
            'description': 'An epic journey begins in the dark forest',
            'genre': 'adventure',
            'visibility': 'private'
        }, headers=admin_headers)
        assert resp.status_code == 201
        data = resp.get_json()['data']
        assert 'story' in data
        assert 'time_cone' in data
        assert data['story']['title'] == 'The Beginning'

    def test_create_requires_auth(self, client, world):
        resp = client.post('/api/stories', json={
            'world_id': world['world_id'],
            'title': 'No Auth',
            'genre': 'adventure'
        })
        assert resp.status_code == 401

    def test_create_in_nonexistent_world(self, client, admin_headers):
        resp = client.post('/api/stories', json={
            'world_id': 'fake-world-id',
            'title': 'Ghost Story',
            'genre': 'mystery'
        }, headers=admin_headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Get story detail
# ---------------------------------------------------------------------------

class TestGetStory:
    def test_get_success(self, client, story, admin_headers):
        resp = client.get(f'/api/stories/{story["story_id"]}', headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['story_id'] == story['story_id']

    def test_get_nonexistent(self, client, admin_headers):
        resp = client.get('/api/stories/no-such-story', headers=admin_headers)
        assert resp.status_code == 404

    def test_get_private_story_without_auth(self, client, story):
        resp = client.get(f'/api/stories/{story["story_id"]}')
        assert resp.status_code in (403, 404)


# ---------------------------------------------------------------------------
# Update story
# ---------------------------------------------------------------------------

class TestUpdateStory:
    def test_update_title(self, client, story, admin_headers):
        resp = client.put(f'/api/stories/{story["story_id"]}',
                          json={'title': 'Updated Title'}, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['title'] == 'Updated Title'

    def test_update_requires_auth(self, client, story):
        resp = client.put(f'/api/stories/{story["story_id"]}',
                          json={'title': 'No Auth'})
        assert resp.status_code == 401

    def test_update_nonexistent(self, client, admin_headers):
        resp = client.put('/api/stories/ghost-id',
                          json={'title': 'Ghost'}, headers=admin_headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Delete story
# ---------------------------------------------------------------------------

class TestDeleteStory:
    def test_delete_success(self, client, world, admin_headers):
        resp = client.post('/api/stories', json={
            'world_id': world['world_id'],
            'title': 'Temp Story',
            'genre': 'mystery',
            'visibility': 'private'
        }, headers=admin_headers)
        sid = resp.get_json()['data']['story']['story_id']

        resp = client.delete(f'/api/stories/{sid}', headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data'] is None

    def test_delete_makes_story_unretrievable(self, client, world, admin_headers):
        resp = client.post('/api/stories', json={
            'world_id': world['world_id'],
            'title': 'Delete Me',
            'genre': 'conflict',
            'visibility': 'private'
        }, headers=admin_headers)
        sid = resp.get_json()['data']['story']['story_id']

        client.delete(f'/api/stories/{sid}', headers=admin_headers)
        resp = client.get(f'/api/stories/{sid}', headers=admin_headers)
        assert resp.status_code == 404

    def test_delete_requires_auth(self, client, story):
        resp = client.delete(f'/api/stories/{story["story_id"]}')
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Stories by world
# ---------------------------------------------------------------------------

class TestWorldStories:
    def test_list_stories_in_world(self, client, world, story, admin_headers):
        resp = client.get(f'/api/worlds/{world["world_id"]}/stories',
                          headers=admin_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        story_ids = [s['story_id'] for s in body.get('data', body if isinstance(body, list) else [])]
        assert story['story_id'] in story_ids

    def test_list_stories_nonexistent_world(self, client, admin_headers):
        resp = client.get('/api/worlds/no-such-world/stories', headers=admin_headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Link entities / clear links
# ---------------------------------------------------------------------------

class TestStoryEntityLinks:
    def test_link_entities_requires_auth(self, client, story):
        resp = client.post(f'/api/stories/{story["story_id"]}/link-entities',
                           json={'entity_ids': []})
        assert resp.status_code == 401

    def test_clear_links_requires_auth(self, client, story):
        resp = client.post(f'/api/stories/{story["story_id"]}/clear-links')
        assert resp.status_code == 401

    def test_clear_links_success(self, client, story, admin_headers):
        resp = client.post(f'/api/stories/{story["story_id"]}/clear-links',
                           headers=admin_headers)
        assert resp.status_code == 200
