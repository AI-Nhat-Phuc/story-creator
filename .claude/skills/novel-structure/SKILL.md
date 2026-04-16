---
name: novel-structure
description: Use this skill when editing code related to the Novel feature (per-world book with ordered chapters), chapter ordering, the `order` / `chapter_number` fields on Story, word counts, or story reader navigation. Triggers when editing api/core/models/story.py, api/core/models/world.py (novel dict), api/interfaces/routes/world_routes.py (novel endpoints), api/interfaces/routes/story_routes.py (neighbors/reorder), and frontend NovelContainer / NovelView / ChapterList / StoryReaderPage.
---

# novel-structure — Novel & Chapter Ordering

The "novel" is a per-world ordered sequence of stories-as-chapters. This skill captures the field semantics, API shape, and frontend layout.

## Data model

### Story fields (relevant subset)

- `order: int` — sort key for chapter/story ordering within a world. **Replaces `time_index`** for all list/reader sort logic. Ties broken by `created_at` ascending
- `chapter_number: str | None` — human-facing label ("Chapter 1", "Prologue", "Phần 2"). Display-only; never used for sorting
- `word_count: int` — pre-calculated on save. Frontend MUST read this field and never recompute from content (content may be HTML/markdown/plain)
- `updated_at: str` — ISO timestamp, refreshed on every `PUT /api/stories/:id`

### World.novel dict

```python
{
  "title": str,
  "description": str,
  "chapter_order": [story_id, ...]   # ordered list; stories not in the list = "Ungrouped"
}
```

Permission: owner + co_author can reorder/edit. Others see read-only.

## API surface

- `GET  /api/worlds/:id/novel` — returns `{title, description, chapter_order, owner_id, co_authors, chapters: [...]}`. **Must include `owner_id` and `co_authors`** so the frontend can compute edit permission without a second fetch
- `PUT  /api/worlds/:id/novel` — update `title`/`description` (owner only)
- `PATCH /api/worlds/:id/novel/chapters` — body `{order: [story_id, ...]}`. Owner + co_author. Silently drops story_ids that don't belong to this world (no 400 — prevents permission leak)
- `GET  /api/worlds/:id/novel/content?cursor=...&line_budget=100` — paginated content for the reader. Initial page returns 2 chapters, subsequent pages 100 lines each (may cut mid-chapter). Cursor-based
- `GET  /api/stories/:id/neighbors` — returns `{prev: story | null, next: story | null}` by `order` within the same world

## Sort/order rules

- All story lists within a world sort by `order ASC, created_at ASC`
- Reorder API writes new contiguous integer `order` values (1, 2, 3...) in request order
- Stories not listed in the PATCH keep their existing `order` (appear after listed ones)
- Migration: `time_index > 0` → copy to `order`; else assign by `created_at`; then drop `time_index`

## Frontend structure

- `NovelPage` → `NovelContainer` (state + API calls) → `NovelView` (pure)
- `ChapterList` with draggable `ChapterRow` — drag disabled for viewers
- Drag-drop fires `PATCH /novel/chapters` immediately on drop (optimistic update + rollback on error)
- Empty state when `chapter_order` is empty
- `StoryReaderPage` uses `/neighbors` for prev/next buttons — navigation stays within the world

## Common gotchas (from `fix_novel_feature_bugs`)

- **Permission UI relies on `owner_id` + `co_authors` in the `/novel` response** — if you change the serializer, these must stay included
- **Word count is always `story.word_count`**, never `story.content.split()` on the frontend. Content may be HTML-escaped markup and the frontend cannot parse reliably
- **`updated_at` must refresh on `PUT /api/stories/:id`** — otherwise chapter lists show stale timestamps
- **Reorder validation is silent**: invalid story_ids are skipped, never returned as errors (prevents leak of which stories exist across worlds)
- **Draft resume from `/api/stories/my-draft`** returns `{story: {...}}` (nested). Frontend must read `res.data.story`, not `res.data`

## When adding a new chapter action

- Always update `order` via the reorder endpoint, never by direct story PUT
- When displaying word count anywhere, use `story.word_count` field
- Permission check: `story.owner_id === userId || world.co_authors.includes(userId)`
- Refresh `updated_at` on any PUT that modifies chapter content
