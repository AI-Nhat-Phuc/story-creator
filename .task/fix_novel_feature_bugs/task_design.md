# Design: Fix Novel Feature Bugs

**Feature**: fix novel feature bugs
**Phase**: DESIGN

---

## Changed Files

| File | Change Type | Maps to Spec Clause |
|------|-------------|---------------------|
| `api/interfaces/routes/world_routes.py` | MODIFY (route logic) | S1, S6 |
| `api/interfaces/routes/story_routes.py` | MODIFY (route logic) | S4 |
| `frontend/src/containers/NovelContainer.jsx` | MODIFY (frontend logic) | S2 |
| `frontend/src/components/novel/ChapterList.jsx` | MODIFY (frontend logic) | S3 |
| `frontend/src/containers/StoryEditorContainer.jsx` | MODIFY (frontend logic) | S5 |

---

## Schema / Interface Changes

**Không có thay đổi schema hay model.**

Lý do: Tất cả 6 bugs đều là lỗi ở tầng route logic (backend) hoặc tầng UI logic (frontend).
Các schemas hiện tại (`UpdateStorySchema`, `ReorderChaptersSchema`, `UpdateNovelSchema`) đều
đã đúng và không cần sửa. Model `World` và `Story` đã có đủ các trường cần thiết.

---

## Model Changes

**Không có thay đổi model.**

`World.novel` đã lưu `chapter_order`, `title`, `description`. `World` đã có `owner_id` và
`co_authors` — chỉ cần expose chúng trong response của `get_novel` (S1).

`Story.chapter_number` đã tồn tại. `Story.updated_at` đã tồn tại — chỉ cần route PUT
cập nhật nó (S4).

---

## New Method Signatures

**Không có method mới.**

---

## Interface Changes (Route Response Shape)

### S1 — GET /api/worlds/:world_id/novel

Thay đổi response dict trong `get_novel`:

```python
# BEFORE
return success_response({
    'title': novel.get('title', world_data.get('name')),
    'description': novel.get('description', ''),
    'chapters': chapters,
    'total_word_count': total_word_count
})

# AFTER — thêm owner_id và co_authors
return success_response({
    'title': novel.get('title', world_data.get('name')),
    'description': novel.get('description', ''),
    'chapters': chapters,
    'total_word_count': total_word_count,
    'owner_id': world_data.get('owner_id'),
    'co_authors': world_data.get('co_authors', [])
})
```

### S4 — PUT /api/stories/:story_id

Thêm `updated_at` refresh trước `storage.save_story`:

```python
# AFTER
story_data['updated_at'] = datetime.now().isoformat()
storage.save_story(story_data)
```

### S6 — PATCH /api/worlds/:world_id/novel/chapters

Lọc `order` theo `world_data['stories']`:

```python
# AFTER
world_story_ids = set(world_data.get('stories', []))
for idx, story_id in enumerate(order, start=1):
    if story_id not in world_story_ids:
        continue  # silent skip
    story = storage.load_story(story_id)
    ...
```

---

## Frontend Logic Changes

### S2 — NovelContainer.jsx
```js
// BEFORE
chapters.reduce((sum, ch) => sum + countWords(ch.content), 0)

// AFTER
chapters.reduce((sum, ch) => sum + (ch.word_count || 0), 0)
```

### S3 — ChapterList.jsx
```js
// BEFORE
const words = countWords(ch.content)

// AFTER
const words = ch.word_count || 0
```

### S5 — StoryEditorContainer.jsx
```js
// BEFORE
const draft = res.data
if (draft?.story_id) { ... }

// AFTER
const draft = res.data?.story
if (draft?.story_id) { ... }
```
