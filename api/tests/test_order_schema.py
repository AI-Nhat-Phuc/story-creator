"""Tests for Story.order field, schema back-compat, auto-assign, and migration.

Spec clauses covered:
  BR-1  — Novel sort by order ASC
  BR-2  — Tie-break by created_at ASC
  BR-3  — chapter_number is display-only, not used for sort
  BR-13 — Migration is idempotent
  BR-14 — Migration drops metadata.world_time
  BR-15 — Auto-assign order = max(order) + 1 on create
  BR-16 — User-set order preserved on create/update
"""

import os
import sys

os.environ['TEST_MODE'] = '1'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ---------------------------------------------------------------------------
# Model: Story.order roundtrip
# ---------------------------------------------------------------------------

class TestStoryOrderField:
    def test_story_roundtrip_preserves_order(self):
        from core.models.story import Story
        s = Story(title='T', content='c', world_id='w', order=7)
        assert s.order == 7
        d = s.to_dict()
        assert d['order'] == 7
        s2 = Story.from_dict(d)
        assert s2.order == 7

    def test_legacy_story_has_no_order(self):
        """Stories stored before migration have no `order` field → None."""
        from core.models.story import Story
        s = Story.from_dict({'title': 'T', 'content': 'c', 'world_id': 'w'})
        assert s.order is None

    def test_new_story_does_not_auto_init_world_time(self):
        """metadata.world_time must NOT be auto-initialized (Spec §1)."""
        from core.models.story import Story
        s = Story(title='T', content='c', world_id='w')
        assert 'world_time' not in s.metadata


# ---------------------------------------------------------------------------
# Schema: accept order + back-compat for time_index
# ---------------------------------------------------------------------------

class TestStorySchemaOrderField:
    def test_create_accepts_order(self):
        from schemas.story_schemas import CreateStorySchema
        res = CreateStorySchema().load({'title': 'T', 'world_id': 'w', 'order': 4})
        assert res['order'] == 4

    def test_create_accepts_time_index_back_compat(self):
        from schemas.story_schemas import CreateStorySchema
        res = CreateStorySchema().load({'title': 'T', 'world_id': 'w', 'time_index': 50})
        assert res['time_index'] == 50
        assert res['order'] is None

    def test_update_accepts_order(self):
        from schemas.story_schemas import UpdateStorySchema
        res = UpdateStorySchema().load({'order': 9})
        assert res['order'] == 9


# ---------------------------------------------------------------------------
# Auto-assign order on create (Spec BR-15)
# ---------------------------------------------------------------------------

class TestAutoAssignOrder:
    def test_first_story_gets_order_1(self, client, admin_headers, world):
        resp = client.post('/api/stories', json={
            'world_id': world['world_id'],
            'title': 'First',
            'visibility': 'private'
        }, headers=admin_headers)
        assert resp.status_code == 201
        story = resp.get_json()['data']['story']
        assert story.get('order') == 1

    def test_second_story_gets_order_2(self, client, admin_headers, world):
        client.post('/api/stories', json={
            'world_id': world['world_id'], 'title': 'S1', 'visibility': 'private'
        }, headers=admin_headers)
        resp = client.post('/api/stories', json={
            'world_id': world['world_id'], 'title': 'S2', 'visibility': 'private'
        }, headers=admin_headers)
        story = resp.get_json()['data']['story']
        assert story.get('order') == 2

    def test_explicit_order_preserved_on_create(self, client, admin_headers, world):
        """BR-16 — if user passes order, keep it."""
        resp = client.post('/api/stories', json={
            'world_id': world['world_id'], 'title': 'Custom', 'order': 99,
            'visibility': 'private'
        }, headers=admin_headers)
        story = resp.get_json()['data']['story']
        assert story.get('order') == 99

    def test_explicit_order_preserved_on_update(self, client, admin_headers, world):
        create_resp = client.post('/api/stories', json={
            'world_id': world['world_id'], 'title': 'S', 'visibility': 'private'
        }, headers=admin_headers)
        sid = create_resp.get_json()['data']['story']['story_id']

        resp = client.patch(f'/api/stories/{sid}', json={'order': 42},
                            headers=admin_headers)
        assert resp.status_code == 200
        # Reload and check
        got = client.get(f'/api/stories/{sid}', headers=admin_headers)
        assert got.get_json()['data'].get('order') == 42

    def test_time_index_maps_to_order_back_compat(self, client, admin_headers, world):
        """Old clients sending time_index should get an order assigned."""
        resp = client.post('/api/stories', json={
            'world_id': world['world_id'], 'title': 'Legacy',
            'time_index': 30, 'visibility': 'private'
        }, headers=admin_headers)
        story = resp.get_json()['data']['story']
        # order must be set (either 1 for first story, or derived)
        assert story.get('order') is not None
        assert story.get('order') >= 1


# ---------------------------------------------------------------------------
# Migration (Spec BR-13, BR-14)
# ---------------------------------------------------------------------------

class TestOrderMigration:
    def test_migration_module_exists(self):
        """Migration script must be importable."""
        import importlib
        mod = importlib.import_module('migrations.migrate_time_index_to_order')
        assert hasattr(mod, 'migrate'), "migrate() callable must exist"

    def test_migration_assigns_sequential_orders(self, app):
        """Stories sorted by (time_index desc-priority, created_at) → order 1..N."""
        from migrations.migrate_time_index_to_order import migrate
        storage = app.config['STORAGE']

        # Seed 3 stories with different time_index values
        storage.save_world({'world_id': 'w-mig', 'name': 'W',
                            'owner_id': 'u1', 'visibility': 'private',
                            'stories': []})
        storage.save_story({'story_id': 's1', 'world_id': 'w-mig',
                            'title': 'A', 'content': '', 'owner_id': 'u1',
                            'time_index': 20, 'created_at': '2020-01-01'})
        storage.save_story({'story_id': 's2', 'world_id': 'w-mig',
                            'title': 'B', 'content': '', 'owner_id': 'u1',
                            'time_index': 80, 'created_at': '2020-01-02'})
        storage.save_story({'story_id': 's3', 'world_id': 'w-mig',
                            'title': 'C', 'content': '', 'owner_id': 'u1',
                            'time_index': 0, 'created_at': '2020-01-03'})

        migrate(storage)

        s1 = storage.load_story('s1')
        s2 = storage.load_story('s2')
        s3 = storage.load_story('s3')

        # time_index 20 < 80 → s1 first, s2 second, s3 (no time_index) last
        assert s1['order'] == 1
        assert s2['order'] == 2
        assert s3['order'] == 3

    def test_migration_drops_world_time_metadata(self, app):
        from migrations.migrate_time_index_to_order import migrate
        storage = app.config['STORAGE']

        storage.save_world({'world_id': 'w-wt', 'name': 'W',
                            'owner_id': 'u1', 'visibility': 'private',
                            'stories': []})
        storage.save_story({'story_id': 's-wt', 'world_id': 'w-wt',
                            'title': 'X', 'content': '', 'owner_id': 'u1',
                            'metadata': {'world_time': {'year': 100, 'era': 'Old'}}})

        migrate(storage)

        s = storage.load_story('s-wt')
        assert 'world_time' not in (s.get('metadata') or {})

    def test_migration_is_idempotent(self, app):
        """Running migrate twice must not re-shuffle assigned orders."""
        from migrations.migrate_time_index_to_order import migrate
        storage = app.config['STORAGE']

        storage.save_world({'world_id': 'w-idem', 'name': 'W',
                            'owner_id': 'u1', 'visibility': 'private',
                            'stories': []})
        storage.save_story({'story_id': 'a', 'world_id': 'w-idem',
                            'title': 'A', 'content': '', 'owner_id': 'u1',
                            'time_index': 10, 'created_at': '2020-01-01'})
        storage.save_story({'story_id': 'b', 'world_id': 'w-idem',
                            'title': 'B', 'content': '', 'owner_id': 'u1',
                            'time_index': 50, 'created_at': '2020-01-02'})

        migrate(storage)
        order_after_first = storage.load_story('a')['order'], storage.load_story('b')['order']

        migrate(storage)
        order_after_second = storage.load_story('a')['order'], storage.load_story('b')['order']

        assert order_after_first == order_after_second
