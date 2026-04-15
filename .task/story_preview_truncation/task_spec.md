# SPEC — Story Preview + Novel Reader Experience

> **Status**: DRAFT
> **Phase**: SPEC
> **Date**: 2026-04-14
> **Complexity**: 7/10

---

## Behavior

Tái cấu trúc trải nghiệm đọc story/novel với các thay đổi liên quan:

### 1. Schema — `time_index` → `order`

- Thêm field `order: int` trên Story model (sort key thuần)
- Bỏ hoàn toàn phép tính calendar year từ `time_index`
- Loại bỏ `metadata.world_time` (dẫn xuất từ calendar) — không còn cần
- Giữ `chapter_number` cho label hiển thị ("Chương X") mà user có thể custom
- Migration data cũ: `time_index` → `order` (stories có `time_index > 0` xếp trước theo time_index, còn lại theo `created_at`, assign `order` liên tục từ 1)

### 2. Story detail page truncation

- Trang `/stories/:storyId` chỉ hiện **10 dòng đầu** của `content`
- Nếu dài hơn 10 dòng → fade overlay + nút **"Xem thêm"** dẫn đến `/stories/:storyId/read`
- Nếu `highlightPosition >= 0` (query param): vẫn render full (để scroll đúng), không show button

### 3. Story Reader (mới)

- Route: `/stories/:storyId/read`
- Giao diện tối giản, hiển thị đầy đủ content + metadata tối thiểu
- Navigation: **Chương trước** / **Chương tiếp theo** (theo `order` ASC trong cùng world, chỉ stories user có quyền xem)
- Button "Về world novel" dẫn đến `/worlds/:worldId/novel` scroll đến story này

### 4. World Novel Reader overhaul

- Route: `/worlds/:worldId/novel` (đã có, overhaul)
- Thay danh sách chapter → **hiển thị content tất cả stories theo order**
- **Infinite scroll pagination:**
  - Load 2 chapters đầu (theo `order` ASC) khi mở trang
  - Nếu total dòng của 2 chapters ≤ 100 → load thêm 2 chapters kế tiếp khi scroll gần cuối
  - Nếu total > 100 → batch 100 dòng mỗi lần (có thể cắt giữa chapter); khi scroll gần cuối → load tiếp 100 dòng
- Giữ phần quản lý metadata novel (title/description) và drag-reorder chapters (cho editors)

### 5. World detail — button "Xem dạng novel"

- Trên trang `/worlds/:worldId`, thêm nút dẫn đến `/worlds/:worldId/novel`

### 6. Timeline view thay thế

- `WorldTimeline.jsx` hiện dùng `time_index` → đổi thành **alternating vertical timeline** (stories xen kẽ trái/phải) theo `order`
- Bỏ phần calendar year display

---

## API Contract

### Changed: Story schema

```jsonc
// Old
{
  "time_index": 45,
  "metadata": { "world_time": { "era": "...", "year": 48, ... } }
}

// New
{
  "order": 3,
  "chapter_number": 3,
  "metadata": {}  // không có world_time
}
```

### New: Novel content (paginated)

```text
GET /api/worlds/:world_id/novel/content?cursor=<opaque>&line_budget=100

200: {
  "blocks": [
    { "story_id": "...", "title": "...", "order": 1,
      "content": "<partial text>", "start_line": 0, "end_line": 100,
      "total_lines": 240, "is_complete": false }
  ],
  "next_cursor": "<opaque|null>",
  "has_more": true
}
```

- Cursor encodes `{last_story_order, last_line_offset}`
- `line_budget` default 100; first call may return up to 2 full chapters if combined ≤ 100 lines
- Cắt chapter giữa chừng hợp lệ khi batch vượt 100 dòng

### New: Story neighbors

```text
GET /api/stories/:story_id/neighbors

200: {
  "prev": { "story_id": "...", "title": "...", "order": 2 } | null,
  "next": { "story_id": "...", "title": "...", "order": 4 } | null
}
```

### Changed: Create/update story

- `time_index` → `order` (backend accept cả 2 trong grace period, auto map `time_index` → `order`)
- Bỏ `_set_world_time` helper và calendar year calculation
- Khi tạo story mới mà không truyền `order`: auto-assign = `max(order for stories in world) + 1`

---

## Business Rules

### Ordering & sort

1. Novel reader & neighbors sort stories theo `order ASC` trong cùng `world_id`
2. Stories cùng `order` (tie) → sort phụ theo `created_at ASC`
3. `chapter_number` chỉ để hiển thị label — không dùng để sort

### Pagination (novel content)

4. Initial load: 2 chapters đầu (theo `order` ASC)
5. Nếu 2 chapters đó có tổng dòng ≤ 100 → response chứa cả 2 full, `has_more = true` nếu còn stories
6. Nếu > 100 → chỉ trả đủ lines để cover ≤ 100 (có thể dừng giữa chapter), set `is_complete = false` cho chapter bị cắt
7. Scroll trigger: khi user scroll đến 80% viewport → fetch next cursor
8. Mỗi batch sau: tối đa 100 dòng, ưu tiên finish chapter đang dở, rồi đến chapter kế

### Preview truncation (story detail)

9. Plain text: split `content.split('\n')`, trim trailing empty, count > 10 → truncate
10. HTML/markdown: CSS `line-clamp: 10`, detect `scrollHeight > clientHeight`
11. `highlightPosition >= 0` → skip truncate, no button
12. Không có `world_id` / `world` chưa load → skip truncate, no button

### Migration

13. Migration script (idempotent):
    - Với mỗi world: lấy all stories, sort theo `(time_index if time_index > 0 else +∞, created_at ASC)`
    - Assign `order = 1, 2, 3, ...` theo kết quả sort
    - Xóa `metadata.world_time` nếu có
    - Keep `chapter_number` y nguyên (nếu có)
14. Migration chạy 1 lần khi deploy; data mới không còn `time_index` field

### Auto order on create

15. Khi tạo story mới không truyền `order` → `order = max_order_in_world + 1`
16. Nếu user sửa `order` → giữ nguyên, không auto-resolve conflict (rule 2 xử lý tie)

---

## Edge Cases

- World không có story nào → novel reader hiện empty state "Chưa có chương nào"
- Story đầu tiên / cuối cùng trong world → prev hoặc next = null, button disabled
- Story không thuộc world nào (`world_id = null`) → không cho vào story reader (redirect hoặc error)
- User không có quyền xem 1 story trong giữa sequence → skip, prev/next nhảy qua
- Story có content rỗng → trong novel reader hiện "[Chương trống]" placeholder, trong preview không show button
- Migration chạy 2 lần → idempotent (check nếu `order` đã set thì skip story đó)
- Content rất dài (1 chapter > 1000 dòng) → batch 100 dòng cắt OK, UI không bị crash

---

## Out of Scope

- Bookmarks / reading progress tracking
- Search trong novel content
- Comments / annotations
- Offline reading / caching
- Export full novel PDF (chỉ từng story như cũ)
- i18n strings (hard-code Vietnamese)
- Breadcrumb navigation trong reader
- Font/theme controls
- Deprecate `chapter_number` — giữ nguyên cho back-compat
