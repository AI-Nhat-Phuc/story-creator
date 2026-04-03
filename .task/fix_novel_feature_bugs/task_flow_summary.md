# Flow Summary — fix novel feature bugs

> **Status**: APPROVED (retroactive)
> **File**: api/interfaces/routes/world_routes.py
> **Date**: 2026-04-03

---

## File: api/interfaces/routes/world_routes.py

### Scope: `get_novel` + `reorder_chapters`

---

### get_novel — Current Flow

**Input**: `world_id` (path param), `g.current_user.user_id` (from JWT)

**Execution Steps**:
1. Load `world_data` from storage; raise 404 if not found
2. Extract `novel = world_data.get('novel') or {}`
3. Build `chapter_order` list (from `novel['chapter_order']` or from stories with `chapter_number`)
4. Load all stories for world via `storage.list_stories(world_id, user_id)`
5. Build `stories_by_id` lookup dict
6. Iterate `chapter_order`, skip missing stories, compute word count, build `chapters` list
7. Return `success_response` with title, description, chapters, total_word_count

**Output**: 200 JSON with novel metadata + chapter list

**Observed Issues (already fixed)**:
- Response did NOT include `owner_id` and `co_authors` → frontend `canEdit`/`canReorder` always false

---

### get_novel — Planned Changes (already applied — S1)

**Added to response**:
```python
'owner_id': world_data.get('owner_id'),
'co_authors': world_data.get('co_authors', [])
```

**Not changed**: all other fields, auth logic, chapter iteration

---

### reorder_chapters — Current Flow

**Input**: `world_id` (path param), `order` (list of story_ids from request body)

**Execution Steps**:
1. Load `world_data`; raise 404 if not found
2. Check `is_world_coauthor`; raise 403 if not
3. Get `order` from `request.validated_data`
4. Build `world_story_ids = set(world_data.get('stories', []))`
5. Iterate `order` with `enumerate(start=1)`:
   - Skip if `story_id not in world_story_ids`
   - Load story; set `chapter_number = idx`; save story
6. Update `novel['chapter_order'] = order`; save world; flush
7. Return 200 with updated chapters list

**Output**: 200 JSON with list of `{story_id, chapter_number}` for updated stories

**Observed Issues (already fixed)**:
- Was iterating all story_ids without checking world membership → could mutate stories from other worlds

---

### reorder_chapters — Planned Changes (already applied — S6)

**Added before loop**:
```python
world_story_ids = set(world_data.get('stories', []))
```

**Added inside loop**:
```python
if story_id not in world_story_ids:
    continue
```

**Not changed**: permission check, chapter_order persistence, flush

---

## File: api/interfaces/routes/story_routes.py

### Scope: `update_story` (PUT)

---

### update_story — Current Flow

**Input**: `story_id` (path param), body with optional `title`, `content`, `format`, `visibility`

**Execution Steps**:
1. Load `story_data`; raise 404 if not found
2. Check `can_edit`; raise 403 if not
3. Handle visibility change (quota check, draft conflict)
4. Apply field updates for `title`, `content`, `format`
5. `storage.save_story(story_data)` + `flush_data()`
6. Return 200 with full `story_data`

**Output**: 200 JSON with full story dict

**Observed Issues (already fixed)**:
- `updated_at` was NOT refreshed before save → stale timestamp in ChapterList

---

### update_story — Planned Changes (already applied — S4)

**Added before save**:
```python
story_data['updated_at'] = datetime.now().isoformat()
```

**Not changed**: visibility logic, field iteration, response format

---

## Frontend Files (no flow summary required per SDD rules)

### NovelContainer.jsx (S2)
- Changed: `countWords(ch.content)` → `ch.word_count || 0`
- Removed: unused `countWords` import

### ChapterList.jsx (S3)
- Changed: `countWords(ch.content)` → `ch.word_count || 0`
- Removed: unused `countWords` import

### StoryEditorContainer.jsx (S5)
- Changed: `const draft = res.data` → `const draft = res.data?.story`
- No other changes
