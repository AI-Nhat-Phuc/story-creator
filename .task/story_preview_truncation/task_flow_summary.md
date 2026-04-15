# Flow Summary — story preview truncation

> **Status**: PENDING APPROVAL
> **Files**: `api/interfaces/routes/story_routes.py`, `api/interfaces/routes/world_routes.py`
> **Date**: 2026-04-15

---

## File 1 — `api/interfaces/routes/story_routes.py`

### Current Flow (`create_story`, line 67-197)

**Input**: validated `CreateStorySchema` payload (title, world_id, content, format,
visibility, genre, selected_characters, time_index, ...).

**Execution Steps**:
1. Resolve world; 404 if missing.
2. Permission check (`can_view`).
3. Quota check if `visibility == 'public'`.
4. Pull `time_index` from payload (default 0).
5. Resolve linked entities.
6. Generate story via `story_generator.generate(...)`.
7. Override `owner_id`, `visibility`, `format`, `content`.
8. **Call `_set_world_time(story, world, time_index)`** — writes
   `story.metadata['world_time']` with calendar year math.
9. Generate `time_cone` using `time_index`.
10. Persist story, time_cone, world.
11. Increment public_stories counter if public.

**Output**: `created_response({story_id, story, time_cone})`.

### Current Flow (`patch_story`, line 335-403)

**Input**: validated `UpdateStorySchema`, path `story_id`.

**Execution Steps**:
1. Load story; 404 if missing.
2. Permission check (edit OR world co-author).
3. Copy `title`, `content`, `format` if present.
4. Copy `chapter_number` if present.
5. If `time_index` present → write `story_data['time_index']` + call
   `_set_world_time` via `_Proxy`.
6. Stamp `updated_at`, save, flush.

**Output**: `success_response({story_id, updated_at}, "Story saved")`.

### Observed Issues (NOT fixing unless asked)

- WARNING: `update_story` (PUT) ignores `time_index` / `chapter_number` /
  `order` entirely. Only `patch_story` handles those — inconsistent.
- WARNING: `_set_world_time` mutates `story.metadata` in-place; the `_Proxy`
  wrapper in `patch_story` is a smell.
- WARNING: `time_cone` is still generated per-story even though the spec
  retires `time_index` in favor of `order`.

### Planned Changes

**Will add/modify**:
- **Auto-assign `order`**: in `create_story`, compute
  `max(order) + 1` across stories in the same world (only when user did not
  pass `order`). Maps `time_index` → `order` if `order` is absent but
  `time_index` is provided (back-compat per BR-16).
- **Drop `_set_world_time` call in `create_story`** (Spec §1 — world_time is
  no longer auto-initialized).
- **Simplify `patch_story` `time_index` branch**: no more `_Proxy`,
  no more `_set_world_time`; `time_index` updates just store the raw field
  (back-compat) AND also update `order` if `order` is unset.
- **Add `order` handling**: both `create_story` and `patch_story` must accept
  and persist `story.order`.
- **New route `GET /api/stories/<story_id>/neighbors`** → delegates to
  `NovelService.get_neighbors(world_id, story_id)`; returns
  `{prev: {...}, next: {...}}` keyed by (`order` ASC, `created_at` ASC).
- Keep `time_cone` generation as-is (out of scope).

**Will NOT change**:
- Quota logic.
- Permission checks.
- `list_stories`, `get_story_detail`, `delete_story`, `link_entities`,
  `clear_links`.
- `_set_world_time` helper (leave in place, just stop calling it in
  `create_story`; `patch_story` removes its call).

---

## File 2 — `api/interfaces/routes/world_routes.py`

### Current Flow (`get_novel`, line 726-787)

**Input**: path `world_id`.

**Execution Steps**:
1. Load world; 404 if missing.
2. Pull `novel.chapter_order` from world.
3. If `chapter_order` set → use it as story ID ordering.
   Else → sort stories by `chapter_number` ASC.
4. For each story, compute word count; build `{story_id, chapter_number,
   title, word_count, updated_at}`.
5. Return `{title, description, chapters, total_word_count, ...}`.

**Output**: `success_response({title, description, chapters, ...})`.

### Observed Issues

- WARNING: Ordering uses `chapter_order` / `chapter_number`, not the new
  `order` field. Spec BR-1 says Novel must sort by `order ASC`.
- WARNING: Endpoint returns metadata only — no actual chapter content. Spec
  BR-4..BR-8 require streaming content in line-budget batches.

### Planned Changes

**Will add/modify**:
- **New route `GET /api/worlds/<world_id>/novel/content`**
  (query params: `cursor`, `line_budget=100`). Delegates to
  `NovelService.get_content_batch(world_id, cursor, line_budget)`.
  Returns `{blocks: [{story_id, title, order, content, start_line, end_line,
  total_lines, is_complete}], has_more, next_cursor}`.
  - Cursor is opaque base64url of `{order, line}`.
  - BR-4: first 2 chapters seeded if content fits.
  - BR-6: if content exceeds `line_budget`, split mid-chapter with
    `is_complete=false`.
  - BR-8: each batch ≤ `line_budget` lines.
- `get_novel` (existing): **unchanged** (still useful as metadata endpoint
  for the chapter list UI).

**Will NOT change**:
- `upsert_novel`, `reorder_chapters`.
- `_get_or_create_novel` helper.
- All other world routes.

---

## New Files (do not need flow summary — greenfield)

- `api/services/novel_service.py`
  - `get_ordered_stories(storage, world_id, user_id) -> list[dict]` —
    sort by `(order ASC, created_at ASC)`.
  - `get_neighbors(storage, world_id, story_id, user_id) -> dict` —
    returns `{prev, next}`.
  - `get_content_batch(storage, world_id, user_id, cursor, line_budget)
    -> dict` — pagination with mid-chapter split.
  - `assign_next_order(storage, world_id) -> int` — `max(order) + 1`.
  - `_encode_cursor({order, line}) -> str`, `_decode_cursor(str) -> dict`.

- `api/migrations/migrate_time_index_to_order.py`
  - `migrate(storage)` — idempotent. For each world, if any story lacks
    `order`, sort stories by `(has_time_index DESC, time_index ASC,
    created_at ASC)` and assign `order = 1..N`. Strip
    `metadata.world_time` on every story.

---

## Test Impact

Expected to flip RED → GREEN after these edits:
- `test_order_schema.py::TestAutoAssignOrder` (5 tests)
- `test_order_schema.py::TestOrderMigration` (4 tests)
- `test_novel_reader.py::TestNovelContentEndpoint` (7 tests)
- `test_novel_reader.py::TestStoryNeighbors` (6 tests)
