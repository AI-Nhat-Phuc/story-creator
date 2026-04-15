# DESIGN — story preview truncation (novel reader experience)

> **Status**: DRAFT
> **Phase**: DESIGN
> **Date**: 2026-04-14

---

## Changed Files (DESIGN phase only — schemas + models)

| File | Change Type | Maps to Spec Clause |
| ---- | ----------- | ------------------- |
| `api/core/models/story.py` | MODIFY | Spec §1 (schema), Rule 13–16 (order field, auto-assign, drop world_time autogen) |
| `api/schemas/story_schemas.py` | MODIFY | Spec §1, API Contract (accept `order`, keep `time_index` back-compat) |
| `api/schemas/world_schemas.py` | MODIFY | API Contract (`NovelContentQuerySchema`) |

> Files touched in IMPLEMENT phase (NOT in this DESIGN): routes, services, frontend, migration script. Listed at bottom for reference only.

---

## Schema / Interface Changes

### `api/schemas/story_schemas.py`

```python
# CreateStorySchema — add 'order', keep 'time_index' for back-compat
class CreateStorySchema(Schema):
    # ... existing fields ...

    # NEW: explicit sort order. None → backend auto-assigns max+1.
    order = fields.Int(
        validate=validate.Range(min=1),
        load_default=None,
        allow_none=True
    )

    # KEPT (back-compat). Routes will translate into `order` if `order` not set.
    # To be deprecated after migration & frontend cutover.
    time_index = fields.Int(
        validate=validate.Range(min=0, max=100),
        load_default=0
    )

# UpdateStorySchema — same additions
class UpdateStorySchema(Schema):
    # ... existing fields ...

    order = fields.Int(
        validate=validate.Range(min=1)
    )

    # KEPT (back-compat)
    time_index = fields.Int(
        validate=validate.Range(min=0, max=100)
    )
```

### `api/schemas/world_schemas.py`

```python
# NEW
class NovelContentQuerySchema(Schema):
    """Query params for GET /api/worlds/<world_id>/novel/content."""
    cursor = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=200)
    )
    line_budget = fields.Int(
        validate=validate.Range(min=1, max=500),
        load_default=100
    )
```

No new schema needed for `GET /api/stories/<id>/neighbors` (no body, no query params).

---

## Model Changes

### `api/core/models/story.py`

```python
class Story:
    def __init__(
        self,
        title: str,
        content: str,
        world_id: str,
        story_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        chapter_number: Optional[int] = None,
        order: Optional[int] = None,                 # NEW
        metadata: Optional[Dict[str, Any]] = None,
        visibility: str = 'private',
        owner_id: Optional[str] = None,
        shared_with: Optional[List[str]] = None,
        format: str = 'plain'
    ):
        # ... existing assignments ...
        self.order = order                           # NEW
        self.metadata = metadata or {}
        # REMOVED: auto-init of metadata['world_time']
        # (Spec §1: bỏ hoàn toàn calendar year derivation)
        # ... rest unchanged ...

    def to_dict(self):
        return {
            # ... existing keys ...
            "order": self.order,                     # NEW
            # ... rest unchanged ...
        }

    @classmethod
    def from_dict(cls, data):
        story = cls(
            # ... existing ...
            order=data.get("order"),                 # NEW (also reads legacy stories
                                                     # — None for un-migrated)
            # ... rest ...
        )
        return story
```

**Key behavior changes in the model:**

1. New top-level `order` attribute (int or None)
2. `metadata['world_time']` no longer auto-initialized in `__init__`. Existing stored data may still contain it; `from_dict` will preserve it but model is no longer responsible for it. Will be removed by migration in IMPLEMENT.
3. Backward-compatible: `from_dict` of a pre-migration story (no `order`) → `order = None`. Routes / migration handle assignment.

---

## Method Signatures (planned for IMPLEMENT — NOT yet defined)

These will be added in the IMPLEMENT phase under `services/` and `interfaces/routes/`. Listed here as the design contract:

```python
# services/novel_service.py (NEW)
class NovelService:
    @staticmethod
    def get_ordered_stories(world_id: str, user_id: str) -> list[dict]:
        """Return stories in (order ASC, created_at ASC) for a world,
        filtered by visibility/permissions for `user_id`."""
        raise NotImplementedError

    @staticmethod
    def get_neighbors(story_id: str, user_id: str) -> dict:
        """Return {'prev': {...}|None, 'next': {...}|None}."""
        raise NotImplementedError

    @staticmethod
    def get_content_batch(world_id: str, user_id: str,
                          cursor: str | None, line_budget: int) -> dict:
        """Return paginated novel content blocks per Spec rules 4–8."""
        raise NotImplementedError

    @staticmethod
    def assign_next_order(world_id: str) -> int:
        """Return max(order)+1 for stories in world, or 1 if none."""
        raise NotImplementedError

# interfaces/routes/world_routes.py (MODIFY)
@world_bp.route('/api/worlds/<world_id>/novel/content', methods=['GET'])
@token_required
@validate_query_params(NovelContentQuerySchema)
def get_novel_content(world_id: str): ...

# interfaces/routes/story_routes.py (MODIFY)
@story_bp.route('/api/stories/<story_id>/neighbors', methods=['GET'])
@token_required
def get_story_neighbors(story_id: str): ...
```

---

## Cursor Encoding

Opaque cursor = base64url-encoded JSON `{"order": N, "line": M}`:
- `order` — order of last partially/fully sent chapter
- `line` — line offset within that chapter (0 = chapter not started; `total_lines` = chapter fully sent → next batch starts at next chapter)

Backward-compat: cursor field is opaque to clients; server may change format freely.

---

## Migration Plan (executed in IMPLEMENT, not now)

Will live at `api/migrations/migrate_time_index_to_order.py` (or similar):

```text
For each world:
  stories = list_stories(world_id)
  sorted_stories = sorted(
    stories,
    key=lambda s: (
      0 if s.get('time_index', 0) > 0 else 1,   # time-indexed first
      s.get('time_index', 0) or 0,              # then by time_index
      s.get('created_at', '')                   # tie-break / fallback for non-indexed
    )
  )
  for idx, s in enumerate(sorted_stories, start=1):
    if s.get('order') is None:                  # idempotent
      s['order'] = idx
    s.get('metadata', {}).pop('world_time', None)
    storage.save_story(s)
```

Idempotent: re-running skips stories that already have `order`.

---

## Out-of-DESIGN-phase work (for next phases)

| Phase | Files |
| ----- | ----- |
| TEST | `api/test_novel_content.py` (new), `api/test_story_neighbors.py` (new), `api/test_order_migration.py` (new) |
| IMPLEMENT — backend | `api/services/novel_service.py` (new), `api/interfaces/routes/world_routes.py`, `api/interfaces/routes/story_routes.py`, `api/migrations/migrate_time_index_to_order.py` (new) |
| IMPLEMENT — frontend | `frontend/src/services/api.js`, `frontend/src/components/storyDetail/StoryDetailView.jsx`, `frontend/src/containers/NovelContainer.jsx`, `frontend/src/components/novel/NovelView.jsx`, `frontend/src/components/storyEditor/StoryTimeSelector.jsx` (rename → StoryOrderSelector), `frontend/src/components/worldDetail/WorldTimeline.jsx` (rewrite as zigzag), `frontend/src/components/worldDetail/WorldDetailView.jsx` (add "Xem dạng novel" button), `frontend/src/pages/StoryReaderPage.jsx` (new), `frontend/src/containers/StoryReaderContainer.jsx` (new), `frontend/src/components/storyReader/StoryReaderView.jsx` (new), `frontend/src/App.jsx` (add route), `frontend/src/i18n/locales/{vi,en}.json` |
| REVIEW | All of the above through `/simplify` |
