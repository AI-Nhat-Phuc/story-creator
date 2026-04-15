"""Tests for novel content endpoint and story neighbors.

Spec clauses covered:
  BR-1,2 — ordered by (order ASC, created_at ASC)
  BR-4  — Initial load returns 2 chapters
  BR-5  — If total lines ≤ 100, both chapters returned fully
  BR-6  — If > 100, batch stops mid-chapter; is_complete=false
  BR-8  — Each subsequent batch ≤ 100 lines
  API   — GET /api/worlds/:id/novel/content?cursor&line_budget
  API   — GET /api/stories/:id/neighbors returns prev/next
"""

import os
import sys

os.environ['TEST_MODE'] = '1'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def _create_story_with_order(client, admin_headers, world_id, title, content, order):
    """Create a story and PATCH it with an explicit order."""
    resp = client.post('/api/stories', json={
        'world_id': world_id, 'title': title, 'content': content,
        'format': 'plain', 'visibility': 'private', 'order': order
    }, headers=admin_headers)
    assert resp.status_code == 201, f"create failed: {resp.data}"
    return resp.get_json()['data']['story']['story_id']


# ---------------------------------------------------------------------------
# GET /api/worlds/:id/novel/content
# ---------------------------------------------------------------------------

class TestNovelContentEndpoint:
    def test_endpoint_exists(self, client, admin_headers, world):
        resp = client.get(f'/api/worlds/{world["world_id"]}/novel/content',
                          headers=admin_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.data}"

    def test_empty_world_returns_no_blocks(self, client, admin_headers, world):
        resp = client.get(f'/api/worlds/{world["world_id"]}/novel/content',
                          headers=admin_headers)
        data = resp.get_json()['data']
        assert data['blocks'] == []
        assert data['has_more'] is False
        assert data['next_cursor'] is None

    def test_initial_load_returns_two_chapters_when_short(
        self, client, admin_headers, world
    ):
        """BR-4, BR-5 — 2 chapters, total ≤ 100 lines → both full."""
        wid = world['world_id']
        _create_story_with_order(client, admin_headers, wid, 'A', 'a1\na2\na3', 1)
        _create_story_with_order(client, admin_headers, wid, 'B', 'b1\nb2', 2)

        resp = client.get(f'/api/worlds/{wid}/novel/content', headers=admin_headers)
        data = resp.get_json()['data']
        assert len(data['blocks']) == 2
        assert data['blocks'][0]['title'] == 'A'
        assert data['blocks'][0]['order'] == 1
        assert data['blocks'][0]['is_complete'] is True
        assert data['blocks'][1]['title'] == 'B'
        assert data['blocks'][1]['is_complete'] is True

    def test_blocks_sorted_by_order_ascending(self, client, admin_headers, world):
        """BR-1 — blocks ordered by `order` ASC."""
        wid = world['world_id']
        _create_story_with_order(client, admin_headers, wid, 'C', 'c', 3)
        _create_story_with_order(client, admin_headers, wid, 'A', 'a', 1)
        _create_story_with_order(client, admin_headers, wid, 'B', 'b', 2)

        resp = client.get(f'/api/worlds/{wid}/novel/content', headers=admin_headers)
        data = resp.get_json()['data']
        orders = [b['order'] for b in data['blocks']]
        assert orders == sorted(orders), f"blocks not ordered: {orders}"
        titles = [b['title'] for b in data['blocks']]
        assert titles[:3] == ['A', 'B', 'C']

    def test_long_content_is_split_at_line_budget(
        self, client, admin_headers, world
    ):
        """BR-6 — if > line_budget, chapter is split; is_complete=false for partial."""
        wid = world['world_id']
        long_content = '\n'.join(f'line{i}' for i in range(150))
        _create_story_with_order(client, admin_headers, wid, 'Long', long_content, 1)

        resp = client.get(
            f'/api/worlds/{wid}/novel/content?line_budget=100',
            headers=admin_headers
        )
        data = resp.get_json()['data']
        assert len(data['blocks']) == 1
        block = data['blocks'][0]
        assert block['is_complete'] is False
        assert block['total_lines'] == 150
        assert block['start_line'] == 0
        assert block['end_line'] <= 100
        assert data['has_more'] is True
        assert data['next_cursor'] is not None

    def test_cursor_continues_from_previous_batch(
        self, client, admin_headers, world
    ):
        """BR-8 — cursor resumes; subsequent batch ≤ 100 lines."""
        wid = world['world_id']
        long_content = '\n'.join(f'line{i}' for i in range(150))
        _create_story_with_order(client, admin_headers, wid, 'Long', long_content, 1)

        r1 = client.get(
            f'/api/worlds/{wid}/novel/content?line_budget=100',
            headers=admin_headers
        )
        cursor = r1.get_json()['data']['next_cursor']
        assert cursor is not None

        r2 = client.get(
            f'/api/worlds/{wid}/novel/content?line_budget=100&cursor={cursor}',
            headers=admin_headers
        )
        d2 = r2.get_json()['data']
        assert len(d2['blocks']) == 1
        b = d2['blocks'][0]
        assert b['is_complete'] is True
        assert b['start_line'] > 0
        assert b['end_line'] == 150

    def test_tie_break_by_created_at(self, client, admin_headers, world):
        """BR-2 — same order → created_at ASC."""
        wid = world['world_id']
        # Create in reverse created_at order; both have order=1 (allowed tie)
        _create_story_with_order(client, admin_headers, wid, 'Second', 's', 1)
        _create_story_with_order(client, admin_headers, wid, 'First', 'f', 1)

        resp = client.get(f'/api/worlds/{wid}/novel/content', headers=admin_headers)
        titles = [b['title'] for b in resp.get_json()['data']['blocks']]
        # "Second" was created first in wall-clock time, so comes first despite the name
        assert titles == ['Second', 'First']


# ---------------------------------------------------------------------------
# GET /api/stories/:id/neighbors
# ---------------------------------------------------------------------------

class TestStoryNeighbors:
    def test_endpoint_exists(self, client, admin_headers, world):
        sid = _create_story_with_order(
            client, admin_headers, world['world_id'], 'Solo', 'x', 1
        )
        resp = client.get(f'/api/stories/{sid}/neighbors', headers=admin_headers)
        assert resp.status_code == 200

    def test_single_story_has_no_neighbors(self, client, admin_headers, world):
        sid = _create_story_with_order(
            client, admin_headers, world['world_id'], 'Solo', 'x', 1
        )
        resp = client.get(f'/api/stories/{sid}/neighbors', headers=admin_headers)
        data = resp.get_json()['data']
        assert data['prev'] is None
        assert data['next'] is None

    def test_middle_story_has_both_neighbors(self, client, admin_headers, world):
        wid = world['world_id']
        s1 = _create_story_with_order(client, admin_headers, wid, 'A', 'a', 1)
        s2 = _create_story_with_order(client, admin_headers, wid, 'B', 'b', 2)
        s3 = _create_story_with_order(client, admin_headers, wid, 'C', 'c', 3)

        resp = client.get(f'/api/stories/{s2}/neighbors', headers=admin_headers)
        data = resp.get_json()['data']
        assert data['prev']['story_id'] == s1
        assert data['prev']['title'] == 'A'
        assert data['next']['story_id'] == s3
        assert data['next']['title'] == 'C'

    def test_first_story_has_no_prev(self, client, admin_headers, world):
        wid = world['world_id']
        s1 = _create_story_with_order(client, admin_headers, wid, 'A', 'a', 1)
        _create_story_with_order(client, admin_headers, wid, 'B', 'b', 2)

        resp = client.get(f'/api/stories/{s1}/neighbors', headers=admin_headers)
        data = resp.get_json()['data']
        assert data['prev'] is None
        assert data['next'] is not None

    def test_last_story_has_no_next(self, client, admin_headers, world):
        wid = world['world_id']
        _create_story_with_order(client, admin_headers, wid, 'A', 'a', 1)
        s2 = _create_story_with_order(client, admin_headers, wid, 'B', 'b', 2)

        resp = client.get(f'/api/stories/{s2}/neighbors', headers=admin_headers)
        data = resp.get_json()['data']
        assert data['prev'] is not None
        assert data['next'] is None

    def test_returns_404_for_missing_story(self, client, admin_headers):
        resp = client.get('/api/stories/does-not-exist/neighbors',
                          headers=admin_headers)
        assert resp.status_code == 404
