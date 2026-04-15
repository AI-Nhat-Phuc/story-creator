"""Migration: assign Story.order from legacy time_index / created_at.

Spec clauses:
  BR-13 — migration is idempotent
  BR-14 — migration drops metadata.world_time
  BR-15 — order is integer sort key starting at 1

Logic per world:
  1. Load all stories in the world.
  2. If every story already has `order`, skip (idempotent).
  3. Otherwise sort by:
       - stories WITH `time_index` > 0 first, by time_index ASC
       - then stories without time_index (or time_index == 0) by created_at ASC
  4. Assign order = 1..N in sorted order.
  5. Strip `metadata.world_time` from each story.
"""

from typing import Any, Dict, List


def _sort_for_migration(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort stories so migration produces deterministic order 1..N."""
    def key(s: Dict[str, Any]):
        ti = s.get('time_index')
        has_ti = ti is not None and ti > 0
        return (
            0 if has_ti else 1,           # stories with time_index > 0 first
            ti if has_ti else 0,          # then by time_index ASC
            s.get('created_at') or '',    # final tie-break by created_at
        )
    return sorted(stories, key=key)


def _strip_world_time(story: Dict[str, Any]) -> bool:
    """Remove metadata.world_time. Returns True if something was removed."""
    md = story.get('metadata')
    if isinstance(md, dict) and 'world_time' in md:
        del md['world_time']
        return True
    return False


def _all_worlds(storage):
    """Yield every world, bypassing visibility filters (admin context)."""
    if hasattr(storage, 'worlds'):
        return list(storage.worlds.find({}))
    if hasattr(storage, 'list_worlds'):
        return storage.list_worlds()
    return []


def _all_stories_in_world(storage, world_id):
    """Yield every story for a world, bypassing visibility filters."""
    if hasattr(storage, 'stories'):
        return list(storage.stories.find({'world_id': world_id}))
    return storage.list_stories(world_id=world_id)


def migrate(storage) -> Dict[str, int]:
    """Run the migration across all worlds. Idempotent."""
    stats = {
        'worlds_visited': 0,
        'stories_assigned_order': 0,
        'stories_world_time_stripped': 0,
    }

    for world in _all_worlds(storage):
        world_id = world.get('world_id')
        if not world_id:
            continue
        stats['worlds_visited'] += 1

        stories = _all_stories_in_world(storage, world_id)

        # BR-13 idempotent: if every story already has order, just strip
        # world_time (cheap) and move on.
        if stories and all(s.get('order') is not None for s in stories):
            for s in stories:
                if _strip_world_time(s):
                    storage.save_story(s)
                    stats['stories_world_time_stripped'] += 1
            continue

        ordered = _sort_for_migration(stories)
        for idx, s in enumerate(ordered, start=1):
            changed = False
            if s.get('order') is None:
                s['order'] = idx
                changed = True
                stats['stories_assigned_order'] += 1
            if _strip_world_time(s):
                changed = True
                stats['stories_world_time_stripped'] += 1
            if changed:
                storage.save_story(s)

    return stats


if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from storage import MongoStorage

    mongo_uri = os.environ.get('MONGODB_URI')
    if not mongo_uri:
        print('ERROR: MONGODB_URI environment variable required.')
        sys.exit(1)

    storage = MongoStorage(mongodb_uri=mongo_uri)
    result = migrate(storage)
    print(f'Migration complete: {result}')
