# Spec: Fix Novel Feature Bugs

**Feature**: fix novel feature bugs
**Slug**: fix_novel_feature_bugs
**Complexity**: 4/10 — bug fixes only, no new schema or endpoints

---

## Behavior

### S1 — novel.owner_permissions
`GET /api/worlds/:world_id/novel` phải trả về `owner_id` (string) và `co_authors` (array of
strings) trong response body. Frontend dùng hai trường này để tính `canEdit` (isOwner) và
`canReorder` (isOwner || isCoAuthor). Nếu thiếu, nút Edit và drag-drop chapter không bao giờ
hiện dù user là owner.

### S2 — novel.word_count_container
`NovelContainer` tính `totalWordCount` bằng cách cộng `word_count` (int) đã được tính sẵn phía
backend cho từng chapter. Không được gọi `countWords(ch.content)` vì `ch.content` không tồn
tại trong dữ liệu chapter (API chỉ trả `word_count`, không trả raw content).

### S3 — novel.word_count_list
`ChapterList` hiển thị số từ của mỗi chapter bằng cách đọc `ch.word_count` (int) trực tiếp.
Không được gọi `countWords(ch.content)` vì cùng lý do như S2.

### S4 — story.updated_at_put
`PUT /api/stories/:story_id` phải cập nhật `story_data['updated_at']` thành
`datetime.now().isoformat()` trước khi lưu. Response phải chứa `updated_at` mới. Nếu không
cập nhật, ChapterList hiển thị ngày chỉnh sửa cũ ngay cả sau khi user đã save thành công.

### S5 — story.draft_resume
`GET /api/stories/my-draft` trả về `{ "data": { "story": {...} | null } }`. Frontend
`checkForDraft` phải đọc draft qua `res.data?.story` (không phải `res.data`). Nếu có draft,
navigate đến `/stories/:draft.story_id/edit`. Nếu không có draft, tiếp tục tạo story mới.

### S6 — novel.reorder_validation
`PATCH /api/worlds/:world_id/novel/chapters` chỉ được phép set `chapter_number` trên các
story có `story_id` nằm trong `world_data['stories']`. Các `story_id` không thuộc world phải
bị bỏ qua silently — không raise error, không modify story đó. `chapter_order` vẫn được lưu
với toàn bộ list (bao gồm id không hợp lệ bị bỏ qua).

---

## API Contract

### GET /api/worlds/:world_id/novel
**Response (200)**:
```json
{
  "success": true,
  "data": {
    "title": "string",
    "description": "string",
    "owner_id": "string",
    "co_authors": ["string"],
    "chapters": [
      {
        "story_id": "string",
        "chapter_number": 1,
        "title": "string",
        "word_count": 0,
        "updated_at": "ISO-8601"
      }
    ],
    "total_word_count": 0
  }
}
```
Trước fix: thiếu `owner_id` và `co_authors`.

### PUT /api/stories/:story_id
**Response (200)**:
```json
{
  "success": true,
  "data": { "updated_at": "ISO-8601 (refreshed)", "...": "full story fields" }
}
```
Trước fix: `updated_at` không được refresh.

### GET /api/stories/my-draft
**Response (200)**:
```json
{
  "success": true,
  "data": { "story": { "story_id": "string", "...": "..." } }
}
```
Trước fix (frontend): code đọc `res.data?.story_id` thay vì `res.data?.story?.story_id`.

### PATCH /api/worlds/:world_id/novel/chapters
**Validation**: mỗi `story_id` trong `order` phải nằm trong `world_data['stories']`. Nếu không
thuộc world, bỏ qua (silent skip) — không raise 4xx.

---

## Business Rules

1. BR1: Chapter word count được tính phía backend; frontend chỉ dùng `word_count` đã trả về.
2. BR2: Permission edit novel chỉ dành cho owner. Permission reorder dành cho owner + co_author.
3. BR3: `updated_at` phải được refresh mỗi khi story thay đổi qua PUT hoặc PATCH.
4. BR4: `reorder_chapters` không được mutate stories của world khác dù caller là co_author hợp lệ.

---

## Edge Cases

- EC1: `chapter_order` rỗng `[]` → `reorder_chapters` không làm gì, trả `chapters: []`.
- EC2: Tất cả `story_id` trong `order` đều không thuộc world → `updated_chapters: []`.
- EC3: Không có draft → `res.data.story === null` → `checkForDraft` falls through, tạo mới.
- EC4: Novel chưa khởi tạo (`world_data['novel'] == null`) → `get_novel` vẫn trả `owner_id`
  và `co_authors` lấy từ `world_data`.

---

## Out of Scope

- Xóa `chapter_number` (set null) qua API.
- Race condition trong `doSave` khi tạo story mới đồng thời.
- `Placeholder` extension configuration trong `NovelEditor.jsx`.
- Validation duplicate story_ids trong `reorder_chapters`.
