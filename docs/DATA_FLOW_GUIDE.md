# Data Flow Guide — Data · Backend · Frontend

Hướng dẫn tổng quan cách **MongoDB (data)**, **Flask API (backend)**, và **React/Vite (frontend)** phối hợp với nhau trong Story Creator.

---

## 1. Kiến trúc tổng thể

```
┌─────────────────┐   HTTP (JSON)    ┌─────────────────┐   pymongo    ┌─────────────────┐
│  React Frontend │ ───────────────▶ │  Flask Backend  │ ───────────▶ │  MongoDB Atlas  │
│ (Next.js, :3000)│ ◀─────────────── │  (Flask, :5000) │ ◀─────────── │  (or mongomock) │
└─────────────────┘                  └─────────────────┘              └─────────────────┘
       │                                      │                              │
       │ services/api.js                      │ interfaces/routes/*          │ collections:
       │ (Axios client)                       │ services/*                   │  worlds,
       │                                      │ schemas/* (validation)       │  stories,
       │                                      │ storage/mongo_storage.py     │  entities,
       │                                      │                              │  locations,
       │                                      │                              │  events, ...
```

Dev URL: React `http://localhost:3000`, API Swagger `http://localhost:5000/api/docs`.
Prod: Vercel serves the Next.js build output + rewrites `/api/*` → `api/app.py` serverless.

---

## 2. Data layer — MongoDB

### Collections

| Collection | Model | Key fields |
|---|---|---|
| `worlds` | `World` | `world_id`, `name`, `description`, `visibility`, `owner_id`, `shared_with`, `novel`, `entities[]`, `locations[]`, `stories[]` |
| `stories` | `Story` | `story_id`, `world_id`, `title`, `content`, `order`, `chapter_number`, `entities[]`, `locations[]` |
| `entities` | `Entity` | `entity_id`, `world_id`, `name`, `entity_type`, `attributes` |
| `locations` | `Location` | `location_id`, `world_id`, `name`, `coordinates` |
| `events`, `event_analysis_cache`, `time_cones`, `users`, `gpt_tasks` | … | … |

### Truy cập dữ liệu
- **Lazy connection**: `MongoStorage._connect()` chỉ mở kết nối lần đầu sử dụng — tối ưu Vercel cold start.
- **Projection & pagination**: `list_worlds_summary` / `list_stories_summary` loại bỏ các trường nặng (`description`, `metadata`, `novel`, `content`) và phân trang ở tầng DB bằng `skip`/`limit`.
- **Permission filter**: `_build_permission_query(user_id)` sinh ra `$or` query gồm `public` + `owner_id` + `shared_with` — mọi endpoint list/read đều chạy qua filter này.
- **Upsert atomically**: `save_*` dùng `replace_one({'id': ...}, data, upsert=True)`.
- **Local dev fallback**: khi `MONGODB_URI` trống, dùng `mongomock` (in-memory) — không cần cluster.

---

## 3. Backend — Flask API

Thư mục: `api/`

```
api/
├── app.py                    # Vercel serverless entrypoint
├── main.py                   # Local dev entrypoint
├── core/
│   ├── models/               # World, Story, Entity, Location, User, Event
│   └── exceptions.py         # Typed API exceptions (→ JSON error response)
├── interfaces/
│   ├── api_backend.py        # Flask app factory + blueprint registration
│   ├── auth_middleware.py    # @token_required, @optional_auth, @admin_required
│   ├── error_handlers.py     # Global exception → JSON mapper
│   └── routes/               # Blueprint files (world_routes, story_routes, ...)
├── schemas/                  # Marshmallow request/query validation schemas
├── services/                 # Business logic layer (CRITICAL)
├── storage/                  # MongoStorage + BaseStorage abstract
└── utils/
    ├── responses.py          # success_response, created_response, paginated_response
    └── validation.py         # @validate_request, @validate_query_params decorators
```

### Request lifecycle

```
Client request
  │
  ▼
@optional_auth / @token_required     ← decodes JWT → g.current_user
  │
  ▼
@validate_request / @validate_query_params(Schema)   ← Marshmallow validation
  │                                                   → request.validated_data
  ▼
Route handler (interfaces/routes/*.py)   ← thin; delegates to service layer
  │
  ▼
Service layer (services/*.py)            ← all business logic lives here
  │
  ▼
Storage layer (storage/mongo_storage.py) ← DB I/O, lazy-connected
  │
  ▼
utils/responses.py                       ← standardized JSON envelope
```

### Quy tắc bắt buộc

1. **Import bare names** bên trong `api/`:
   ```python
   from core.models import World, Entity, Story
   from storage import MongoStorage
   from services import GPTService
   ```
2. **Dùng typed exceptions**, không `jsonify({'error': ...})`:
   ```python
   raise ResourceNotFoundError('World', world_id)
   raise PermissionDeniedError('edit', 'world')
   ```
3. **Dùng response utilities**:
   ```python
   return success_response(data)
   return created_response(obj, "Created")
   return paginated_response(items, page, per_page, total)
   ```
4. **Validate trước khi dùng**:
   ```python
   @validate_request(CreateWorldSchema)
   def create_world():
       data = request.validated_data
   ```
5. **Business logic trong services/**, không trong routes.

### Endpoint pattern cho list — "summary" thay vì full document

Endpoints liệt kê dùng phương thức `*_summary()` để loại các trường nặng và phân trang ở DB:

```python
# GET /api/worlds
items, total = storage.list_worlds_summary(user_id=user_id, page=page, per_page=per_page)
return paginated_response(items, page, per_page, total)

# GET /api/worlds/<id>/stories
items, total = storage.list_stories_summary(world_id, user_id, page, per_page)
return paginated_response(items, page, per_page, total)
```

Detail endpoints (`GET /api/worlds/<id>`) vẫn trả về document đầy đủ qua `storage.load_world(id)`.

---

## 4. Frontend — Next.js + React

Thư mục: `src/`

```
src/
├── services/api.js           # Centralized Axios client (worldsAPI, storiesAPI, ...)
├── contexts/                 # AuthContext, GptTaskContext, ThemeContext
├── containers/               # Data-fetching smart components
│   ├── WorldDetailContainer.jsx
│   ├── StoryEditorContainer.jsx
│   └── ...
├── components/               # Presentational components
│   ├── storyEditor/          # EditorHeader, LeftPanel, NovelEditor, StoryTimeSelector
│   ├── storyDetail/
│   ├── worldDetail/
│   └── ...
├── pages/                    # Route pages (WorldsPage, Dashboard, StoryEditorPage, ...)
├── i18n/locales/             # vi.json, en.json — all user-facing text
└── App.jsx                   # React Router
```

### Quy tắc

1. **Gọi API chỉ qua `services/api.js`**:
   ```jsx
   import { worldsAPI, storiesAPI } from '../services/api'
   const { data } = await worldsAPI.list({ page: 1, per_page: 20 })
   ```
   Không dùng `fetch` hoặc `axios` trực tiếp trong components/pages.
2. **Container/Presenter pattern**: container fetch dữ liệu + quản lý state, view component chỉ nhận props và render.
3. **i18n bắt buộc** cho text người dùng: dùng `useTranslation()` + keys trong `i18n/locales/{vi,en}.json`.
4. **Auto-save & resilience**: `AuthContext` không logout khi lỗi mạng tạm thời; `StoryEditorContainer` debounce auto-save.

### Proxy & deployment

- Dev: Vite proxy chuyển `/api/*` → `http://localhost:5000`.
- Prod: `vercel.json` rewrite `/api/*` → `api/app.py` serverless.

---

## 5. Ví dụ end-to-end — Liệt kê worlds

1. **User** mở `/worlds` trong React app.
2. **WorldsPage** gọi container `useWorlds(page, per_page)`.
3. Container call `worldsAPI.list({ page, per_page })` từ `services/api.js`.
4. Axios gửi `GET /api/worlds?page=1&per_page=20` (có `Authorization: Bearer <jwt>`).
5. Flask chạy: `@optional_auth` → decode JWT → `@validate_query_params(ListWorldsQuerySchema)` → route handler.
6. Handler gọi `storage.list_worlds_summary(user_id, page, per_page)`.
7. MongoStorage: `_build_permission_query(user_id)` → `count_documents` + `find(query, projection).sort(...).skip(...).limit(...)` → trả `(items, total)`.
8. Handler wrap kết quả với `paginated_response(items, page, per_page, total)` → JSON envelope `{ data, pagination: { page, per_page, total, pages } }`.
9. Frontend nhận response, render danh sách (không có field nặng như `description`/`novel`).
10. Khi user click vào 1 world → `GET /api/worlds/<id>` trả full document qua `load_world`.

---

## 6. Authentication & Permissions

- **JWT** signed với `JWT_SECRET`; access token lưu trong `localStorage` frontend, gửi qua `Authorization: Bearer`.
- **OAuth**: Google (`@react-oauth/google`) và Facebook (`@greatsumini/react-facebook-login`) → `AuthService.login_google/facebook()` → tạo/lookup user → cấp JWT.
- **Permission model**: `visibility` ∈ {`draft`, `private`, `public`}; `owner_id`; `shared_with: [user_id]`; `co_authors: [user_id]`.
- **Helpers**: `PermissionService.can_view / can_edit / can_delete / can_share / is_world_coauthor`.
- **Roles**: `admin`, `editor`, `viewer` (trên level user); quyền resource dựa vào owner/shared/co-author.

---

## 7. Env vars cần thiết

| Variable | Dùng cho | Bắt buộc |
|---|---|---|
| `MONGODB_URI` | MongoDB Atlas | Prod (dev fallback: mongomock) |
| `JWT_SECRET` | Ký JWT | Yes |
| `OPENAI_API_KEY` | GPT-4o-mini features | Chỉ khi bật GPT |
| `GOOGLE_CLIENT_ID` | Google OAuth | Khi dùng |
| `FACEBOOK_APP_ID` | Facebook OAuth | Khi dùng |
| `APP_ENV` / `VERCEL_ENV` | Tách prod/nonprod DB | Khuyến nghị |

---

## 8. Tài liệu liên quan

- `docs/STORAGE_GUIDE.md` — chi tiết tầng storage
- `docs/API_DOCUMENTATION.md` — liệt kê endpoints
- `docs/MODELS_GUIDE.md` — domain models
- `docs/PRIVACY_SYSTEM.md` — visibility & sharing
- `docs/REACT_ARCHITECTURE.md` — cấu trúc frontend
- `docs/DEVELOPMENT_GUIDE.md` — quy ước dev
- `CLAUDE.md` — rules bắt buộc khi làm việc với AI assistant
