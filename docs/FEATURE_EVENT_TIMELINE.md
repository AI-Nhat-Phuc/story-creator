# Feature: Event Timeline Canvas

## Tổng quan

Thêm một section mới vào Dashboard hiển thị **timeline sự kiện** của một world dưới dạng canvas tương tác. Người dùng có thể:
- Chọn world qua dropdown
- Xem các sự kiện được trích xuất từ các câu chuyện
- Các sự kiện cùng năm nhóm lại thành cụm
- Click vào sự kiện để chuyển đến story tương ứng
- Xem mối liên kết giữa các sự kiện (nhân vật, địa điểm chung)

---

## Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────┐
│               Dashboard Page                     │
│  ┌──────────────────────────────────────────┐    │
│  │  Stats Cards (existing)                   │    │
│  └──────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────┐    │
│  │  Info Table (existing)                    │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
│  ═══════════ Toggle Bar (click to expand) ═══════ │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │  Event Timeline Section (lazy-loaded)     │    │
│  │  ┌─────────────────────────────────────┐  │    │
│  │  │  Header: [World Dropdown ▼] [⟷/⟺]  │  │    │
│  │  └─────────────────────────────────────┘  │    │
│  │  ┌─────────────────────────────────────┐  │    │
│  │  │  Canvas: Event Nodes + Connections   │  │    │
│  │  │                                      │  │    │
│  │  │  Year 1    Year 2    Year 3          │  │    │
│  │  │  ┌────┐   ┌────┐   ┌────┐           │  │    │
│  │  │  │ ●  │   │ ●  │   │ ●  │           │  │    │
│  │  │  │ ●  │───│    │───│ ●  │           │  │    │
│  │  │  └────┘   └────┘   └────┘           │  │    │
│  │  └─────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

## Data Flow

```
Stories (content) ──► GPT Analysis ──► Events + Connections
                                           │
                                           ▼
                      Storage (events table in DB)
                                           │
                                           ▼
                      API: GET /api/worlds/:id/events
                                           │
                                           ▼
                      Frontend: EventTimeline Canvas
```

---

## I. Backend (API)

### 1. Event Model (`api/core/models/event.py`)

```python
class Event:
    event_id: str           # UUID
    story_id: str           # Câu chuyện chứa sự kiện
    world_id: str           # World
    title: str              # Tên sự kiện ngắn gọn
    description: str        # Mô tả ngắn (1-2 câu)
    year: int               # Năm xảy ra trong world timeline
    era: str                # Kỷ nguyên (optional)
    characters: list[str]   # Entity IDs liên quan
    locations: list[str]    # Location IDs liên quan
    connections: list[dict] # [{target_event_id, relation_type, relation_label}]
    story_position: int     # Vị trí (paragraph/sentence index) trong story content
    metadata: dict          # abstract_image_seed, color, etc.
```

### 2. GPT Prompt - Phân tích sự kiện (`api/ai/prompts.py`)

Thêm prompt template mới:

```python
EXTRACT_EVENTS_SYSTEM = (
    "You are a story analyst. Extract key events from story content. "
    "Identify when events happen, who is involved, where they take place, "
    "and how events connect to each other. Always respond in Vietnamese."
)

EXTRACT_EVENTS_TEMPLATE = """
Phân tích câu chuyện sau và trích xuất các sự kiện chính.

Tiêu đề: {story_title}
Thể loại: {story_genre}
Nội dung:
{story_content}

Thông tin thế giới:
- Nhân vật đã biết: {known_characters}
- Địa điểm đã biết: {known_locations}

Trả về JSON với format:
{{
    "events": [
        {{
            "title": "Tên sự kiện ngắn gọn",
            "description": "Mô tả ngắn 1-2 câu",
            "year": <số nguyên, năm xảy ra trong world timeline>,
            "era": "Kỷ nguyên (nếu có)",
            "characters": ["tên nhân vật 1", "tên nhân vật 2"],
            "locations": ["tên địa điểm"],
            "story_position": <vị trí paragraph trong nội dung, bắt đầu từ 0>,
            "abstract_image_seed": "từ khóa mô tả hình ảnh trừu tượng cho sự kiện"
        }}
    ],
    "connections": [
        {{
            "from_event_index": 0,
            "to_event_index": 1,
            "relation_type": "character|location|causation|temporal",
            "relation_label": "Mô tả ngắn mối liên kết"
        }}
    ]
}}
"""
```

### 3. GPT Service - Extract Events (`api/services/event_service.py`)

```python
class EventService:
    def __init__(self, gpt_integration, storage):
        self.gpt = gpt_integration
        self.storage = storage

    def extract_events_from_story(self, story_id, force=False, callback_success, callback_error):
        """Dùng GPT phân tích story content → events + connections.
        1. Tính sha256(story.content)
        2. Check cache: storage.get_analysis_cache(story_id, hash)
        3. Cache hit + force=False → dùng cached result
        4. Cache miss hoặc force=True → gọi GPT → lưu vào cache
        """

    def get_world_events(self, world_id) -> list:
        """Lấy tất cả events của một world (từ tất cả stories)"""

    def get_cross_story_connections(self, world_id) -> list:
        """Tìm connections giữa events từ các stories khác nhau
        dựa trên shared characters/locations"""

    def build_timeline(self, world_id) -> dict:
        """Xây dựng timeline object cho frontend:
        { years: [{year, era, events: [...]}], connections: [...] }"""

    def clear_story_cache(self, story_id):
        """Xóa analysis cache của 1 story"""
```

### 4. API Routes (`api/interfaces/routes/event_routes.py`)

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/worlds/:world_id/events` | Lấy timeline events của world |
| `POST` | `/api/worlds/:world_id/events/extract` | GPT trích xuất events từ tất cả stories |
| `POST` | `/api/stories/:story_id/events/extract` | GPT trích xuất events từ 1 story |
| `GET` | `/api/gpt/results/:task_id` | Kiểm tra kết quả task (existing) |
| `PUT` | `/api/events/:event_id` | Cập nhật event (sửa tay) |
| `DELETE` | `/api/events/:event_id` | Xóa event |
| `POST` | `/api/events/:event_id/connections` | Thêm connection giữa events |

### 5. Storage (`api/storage/nosql_storage.py`)

Thêm table `events` + `event_analysis_cache` vào TinyDB:
- `save_event(event_dict)`
- `get_event(event_id)`
- `list_events_by_world(world_id)`
- `list_events_by_story(story_id)`
- `update_event(event_id, data)`
- `delete_event(event_id)`
- `save_analysis_cache(story_id, content_hash, gpt_response, model)`
- `get_analysis_cache(story_id, content_hash)` → cache hit/miss
- `delete_analysis_cache(story_id)` → xóa cache khi force re-analyze

---

## II. Frontend (React)

### 1. Components mới

```
src/
├── components/
│   └── timeline/
│       ├── EventTimelineSection.jsx    # Section wrapper (lazy load, toggle)
│       ├── TimelineCanvas.jsx          # Canvas chính vẽ nodes
│       ├── EventNode.jsx               # Component cho 1 event node
│       ├── YearCluster.jsx             # Nhóm events cùng năm
│       ├── ConnectionLine.jsx          # Đường nối giữa events
│       └── TimelineControls.jsx        # Controls (hướng, zoom, etc.)
├── containers/
│   └── EventTimelineContainer.jsx      # Data fetching + logic
└── services/
    └── api.js                          # Thêm eventsAPI
```

### 2. EventTimelineSection (`components/timeline/EventTimelineSection.jsx`)

- **Lazy load**: Dùng `IntersectionObserver` hoặc scroll event để load khi user scroll tới
- **Toggle bar**: Thanh ngang ở dưới stats section, click để mở/đóng timeline
- **Header**: Dropdown chọn world + nút chuyển hướng (ngang ↔ dọc)
- **Default world**: Lưu `lastViewedWorldId` vào `localStorage`

### 3. TimelineCanvas (`components/timeline/TimelineCanvas.jsx`)

- Dùng **HTML5 Canvas** hoặc **SVG** (khuyến nghị SVG cho interactivity)
- Hoặc dùng thư viện: **React Flow**, **D3.js**, hoặc custom SVG
- Features:
  - Pan & zoom (kéo và phóng to canvas)
  - Các year cluster sắp xếp theo trục ngang (hoặc dọc)
  - Event nodes: hình tròn với gradient/pattern trừu tượng
  - Connection lines: đường cong SVG giữa các events
  - Click event → navigate to `/stories/:storyId?event=:eventId`

### 4. EventNode (`components/timeline/EventNode.jsx`)

```
  ┌──────────┐
  │  ◉  ← abstract gradient circle (generated from seed)
  │          │
  │ "Mô tả" │ ← short description
  └──────────┘
```

- Hình tròn với gradient/pattern được generate từ `abstract_image_seed`
- Tooltip hiện thêm chi tiết khi hover
- Click → navigate to story

### 5. API Client (`src/services/api.js`)

```javascript
export const eventsAPI = {
  getWorldTimeline: (worldId) => api.get(`/worlds/${worldId}/events`),
  extractFromWorld: (worldId) => api.post(`/worlds/${worldId}/events/extract`),
  extractFromStory: (storyId) => api.post(`/stories/${storyId}/events/extract`),
  updateEvent: (eventId, data) => api.put(`/events/${eventId}`, data),
  deleteEvent: (eventId) => api.delete(`/events/${eventId}`),
  addConnection: (eventId, data) => api.post(`/events/${eventId}/connections`, data),
}
```

### 6. Cookie/LocalStorage

```javascript
// Lưu world đã xem gần nhất
localStorage.setItem('lastViewedWorldId', worldId)
localStorage.getItem('lastViewedWorldId')

// Lưu trạng thái timeline (mở/đóng, hướng)
localStorage.setItem('timelinePrefs', JSON.stringify({
  expanded: true,
  direction: 'horizontal' // or 'vertical'
}))
```

---

## III. Tương tác & UX

### Click Event → Jump to Story
- Navigate to: `/stories/:storyId?event=:eventId&position=:paragraphIndex`
- StoryDetailPage đọc query params, scroll đến paragraph tương ứng
- Highlight paragraph chứa sự kiện

### Connection Types
| Type | Mô tả | Màu |
|------|--------|-----|
| `character` | Nhân vật chung | 🔵 Blue |
| `location` | Địa điểm chung | 🟢 Green |
| `causation` | Nhân quả | 🔴 Red |
| `temporal` | Thời gian liên tiếp | 🟡 Yellow |

### Hướng Timeline
- **Horizontal** (mặc định): Năm từ trái → phải, events xếp dọc trong mỗi year cluster
- **Vertical**: Năm từ trên → dưới, events xếp ngang trong mỗi year cluster

---

## IV. Thư viện đề xuất

| Thư viện | Mục đích | Ghi chú |
|----------|----------|---------|
| **React Flow** | Canvas tương tác nodes + edges | Mạnh mẽ nhất cho use case này |
| **D3.js** | Vẽ SVG phức tạp | Flexible nhưng nhiều code |
| **@xyflow/react** | React Flow v12 | Recommend |
| Không thư viện | Custom SVG + CSS | Nhẹ nhưng tốn effort |

**Khuyến nghị**: Dùng **React Flow (@xyflow/react)** — hỗ trợ sẵn nodes, edges, pan, zoom, minimap.

---

## V. Todo List

### Phase 1: Backend - Data Model & Storage
- [x] **1.1** Tạo Event model (`api/core/models/event.py`) với `to_dict()`, `from_dict()`
- [x] **1.2** Cập nhật `api/core/models/__init__.py` export Event
- [x] **1.3** Thêm event CRUD methods vào `api/storage/nosql_storage.py`
- [x] **1.4** Thêm event CRUD methods vào `api/storage/base_storage.py` (abstract)
- [x] **1.4b** Thêm `event_analysis_cache` table + methods (`save_analysis_cache`, `get_analysis_cache`, `delete_analysis_cache`)
- [x] **1.5** Viết unit test cho Event model & storage

### Phase 2: Backend - GPT Event Extraction
- [x] **2.1** Thêm prompt templates vào `api/ai/prompts.py` (EXTRACT_EVENTS_SYSTEM, EXTRACT_EVENTS_TEMPLATE)
- [x] **2.2** Tạo `api/services/event_service.py` (EventService class)
- [x] **2.3** Implement `extract_events_from_story()` — check cache (sha256 hash) → cache hit: dùng kết quả cũ / cache miss: gọi GPT → lưu events + lưu cache
- [x] **2.4** Implement `build_timeline()` — aggregate events theo world, group by year
- [x] **2.5** Implement `get_cross_story_connections()` — tìm connections cross-story dựa trên shared entities/locations

### Phase 3: Backend - API Routes
- [x] **3.1** Tạo `api/interfaces/routes/event_routes.py` (Blueprint)
- [x] **3.2** Implement `GET /api/worlds/:id/events` — trả về timeline data
- [x] **3.3** Implement `POST /api/worlds/:id/events/extract` — trigger GPT extraction cho all stories
- [x] **3.4** Implement `POST /api/stories/:id/events/extract` — trigger GPT extraction cho 1 story (hỗ trợ `?force=true` bỏ qua cache)
- [x] **3.4b** Implement `DELETE /api/stories/:id/events/cache` — xóa GPT analysis cache
- [x] **3.5** Implement `PUT /api/events/:id` — update event
- [x] **3.6** Implement `DELETE /api/events/:id` — delete event
- [x] **3.7** Register blueprint trong `api/interfaces/api_backend.py`
- [x] **3.8** Register blueprint trong `api/interfaces/routes/__init__.py`

### Phase 4: Frontend - API & Infrastructure
- [x] **4.1** Thêm `eventsAPI` vào `src/services/api.js`
- [x] **4.2** Cài đặt React Flow: `npm install @xyflow/react`
- [x] **4.3** Tạo `src/components/timeline/` folder

### Phase 5: Frontend - Timeline Components
- [x] **5.1** Tạo `EventTimelineSection.jsx` — wrapper với lazy load (IntersectionObserver) + toggle bar
- [x] **5.2** Tạo `EventTimelineContainer.jsx` — data fetching, state management
- [x] **5.3** Tạo `TimelineCanvas.jsx` — React Flow canvas với custom nodes/edges
- [x] **5.4** Tạo `EventNode.jsx` — custom React Flow node (circle + description)
- [x] **5.5** Tạo `YearCluster.jsx` — group node cho events cùng năm
- [x] **5.6** Tạo `ConnectionLine.jsx` — custom edge với màu theo relation type
- [x] **5.7** Tạo `TimelineControls.jsx` — toggle hướng (ngang/dọc), zoom controls

### Phase 6: Frontend - Dashboard Integration
- [x] **6.1** Tích hợp `EventTimelineSection` vào `Dashboard.jsx`
- [x] **6.2** Implement dropdown chọn world (fetch worlds list, default = lastViewedWorldId)
- [x] **6.3** Implement localStorage lưu lastViewedWorldId + timeline preferences
- [x] **6.4** Implement toggle bar ẩn/hiện section ở cuối Dashboard
- [x] **6.5** Implement lazy loading — chỉ fetch data khi section visible

### Phase 7: Frontend - Navigation & Interaction
- [x] **7.1** Click event node → navigate to `/stories/:storyId?event=:eventId&position=:pos`
- [x] **7.2** Cập nhật `StoryDetailPage.jsx` — đọc query params, scroll & highlight event paragraph
- [x] **7.3** Thêm nút "Trích xuất sự kiện" (GPT) trong timeline section header
- [x] **7.4** Hiển thị loading state khi GPT đang phân tích
- [x] **7.5** Tooltip hover trên event nodes hiện thêm chi tiết

### Phase 8: Polish & Testing
- [x] **8.1** Style timeline với TailwindCSS + DaisyUI theme
- [x] **8.2** Responsive design (mobile: force vertical mode)
- [x] **8.3** Error handling & empty states (no events, no stories, GPT unavailable)
- [x] **8.4** Test end-to-end: tạo world → tạo stories → extract events → view timeline
- [x] **8.5** Cập nhật docs (API_DOCUMENTATION.md, REACT_ARCHITECTURE.md)

---

## VI. API Response Format

### `GET /api/worlds/:world_id/events`

```json
{
  "world_id": "uuid",
  "world_name": "Vương quốc Eldoria",
  "timeline": {
    "direction": "horizontal",
    "years": [
      {
        "year": 1,
        "era": "Kỷ nguyên Ánh sáng",
        "events": [
          {
            "event_id": "uuid",
            "story_id": "uuid",
            "story_title": "Cuộc phiêu lưu đầu tiên",
            "title": "Khám phá hang động cổ",
            "description": "Nhóm phiêu lưu phát hiện hang động chứa bản đồ cổ xưa",
            "characters": [
              {"entity_id": "uuid", "name": "Aria"}
            ],
            "locations": [
              {"location_id": "uuid", "name": "Hang động phía Bắc"}
            ],
            "story_position": 2,
            "abstract_image_seed": "cave_ancient_map_discovery"
          }
        ]
      }
    ],
    "connections": [
      {
        "from_event_id": "uuid",
        "to_event_id": "uuid",
        "relation_type": "character",
        "relation_label": "Aria tham gia cả hai sự kiện"
      }
    ]
  }
}
```

### `POST /api/worlds/:world_id/events/extract`

```json
// Request: empty body (extracts from all stories in world)

// Response:
{
  "task_id": "uuid",
  "status": "pending",
  "message": "Đang phân tích 5 câu chuyện..."
}

// Poll GET /api/gpt/results/:task_id for completion
```

---

## VII. Ghi chú kỹ thuật

### Abstract Image Generation
- Dùng `abstract_image_seed` để tạo gradient/pattern CSS unique cho mỗi event
- Ví dụ: hash seed → chọn 2-3 màu gradient → radial gradient trong circle

```javascript
function generateAbstractStyle(seed) {
  const hash = hashString(seed)
  const hue1 = hash % 360
  const hue2 = (hash * 7) % 360
  return {
    background: `radial-gradient(circle, hsl(${hue1}, 70%, 60%), hsl(${hue2}, 60%, 40%))`
  }
}
```

### Cross-Story Connection Detection
Khi extract events từ nhiều stories, EventService tự động:
1. Thu thập tất cả events của world
2. So sánh `characters[]` và `locations[]` giữa các events
3. Tạo connections cho events chia sẻ entities/locations
4. Connections type = `character` nếu shared character, `location` nếu shared location

### GPT Analysis Caching (Cost Reduction)
Kết quả GPT phân tích sự kiện được **cache vào database** để tránh gọi GPT lặp lại:

**Storage table**: `event_analysis_cache`
```python
{
    "cache_id": "uuid",
    "story_id": "uuid",              # Story đã phân tích
    "story_content_hash": "sha256",  # Hash của story content tại thời điểm phân tích
    "raw_gpt_response": {...},       # JSON gốc từ GPT (events + connections)
    "extracted_events_count": 5,
    "analyzed_at": "ISO timestamp",
    "model_used": "gpt-4o-mini"
}
```

**Flow khi extract events**:
1. Tính `sha256(story.content)`
2. Tìm trong `event_analysis_cache` theo `story_id` + `story_content_hash`
3. **Cache hit** → dùng kết quả đã lưu, không gọi GPT → chi phí = 0
4. **Cache miss** (story mới hoặc content đã thay đổi) → gọi GPT → lưu kết quả vào cache
5. Nếu user force re-analyze → query param `?force=true` → bỏ qua cache, gọi GPT mới

**API**:
- `POST /api/stories/:id/events/extract` → mặc định dùng cache
- `POST /api/stories/:id/events/extract?force=true` → bỏ qua cache, gọi GPT mới
- `DELETE /api/stories/:id/events/cache` → xóa cache của story (optional)

**Lợi ích**:
- Story không thay đổi → không tốn tiền GPT
- Chỉ re-analyze khi content thực sự thay đổi (hash khác)
- User có thể force re-analyze nếu muốn kết quả mới
- Cache lưu raw response → có thể re-process mà không gọi GPT

### Performance Considerations
- Timeline data cached ở frontend (React state / context)
- GPT results cached ở backend DB (tránh gọi lại GPT cho cùng content)
- Lazy fetch: chỉ gọi API khi section mở + world được chọn
- Canvas chỉ render visible nodes (React Flow đã hỗ trợ virtualization)
- GPT extraction là async task — poll kết quả qua existing `/api/gpt/results/:task_id`

---

## VIII. Dependencies cần thêm

### Frontend
```bash
npm install @xyflow/react
```

### Backend
Không cần thêm dependency mới (dùng OpenAI + TinyDB đã có).

---

## IX. Thứ tự ưu tiên triển khai

1. **Phase 1 + 2** (Backend data + GPT) — Nền tảng dữ liệu
2. **Phase 3** (API routes) — Endpoint cho frontend
3. **Phase 4 + 5** (Frontend components) — UI
4. **Phase 6** (Dashboard integration) — Tích hợp
5. **Phase 7** (Navigation) — Tương tác
6. **Phase 8** (Polish) — Hoàn thiện
