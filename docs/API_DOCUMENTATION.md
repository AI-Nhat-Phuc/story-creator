# Story Creator API Documentation

## Swagger UI

After starting the API backend, access Swagger UI at:

**http://localhost:5000/api/docs**

## Quick Start

```bash
# Install dependencies
pip install -r api/requirements.txt

# Start API server
npm run dev

# Or backend only
.venv/Scripts/python.exe api/main.py -i api

# Access Swagger UI
http://localhost:5000/api/docs
```

---

## Standardized Response Format

All endpoints return a consistent JSON envelope (Phase 2 refactoring):

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

### Paginated Response (list endpoints)
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 42,
    "total_pages": 3
  }
}
```

### Created Response (201)
```json
{
  "success": true,
  "data": { ... },
  "message": "Resource created successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "resource_not_found",
    "message": "World not found: uuid-123",
    "details": {
      "resource_type": "World",
      "resource_id": "uuid-123"
    }
  }
}
```

### Error Codes

| HTTP | `code` | Description |
|------|--------|-------------|
| 400 | `validation_error` | Request body/params failed validation |
| 400 | `business_rule_violation` | Business constraint violated |
| 401 | `authentication_error` | Missing or invalid JWT token |
| 403 | `permission_denied` | Authenticated but not authorized |
| 404 | `resource_not_found` | Entity does not exist |
| 409 | `conflict` | Duplicate resource (e.g., username taken) |
| 429 | `quota_exceeded` | User quota limit reached |
| 502 | `external_service_error` | GPT/Facebook API error |
| 500 | `internal_error` | Unexpected server error |

---

## Authentication

JWT-based with `Authorization: Bearer <token>` header.

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | — | Register new user |
| POST | `/api/auth/login` | — | Login, receive JWT |
| GET | `/api/auth/verify` | Required | Verify token validity |
| GET | `/api/auth/me` | Required | Current user info |
| POST | `/api/auth/change-password` | Required | Change password |
| POST | `/api/auth/oauth/google` | — | Google OAuth login |
| POST | `/api/auth/oauth/facebook` | — | Facebook OAuth login |

### Auth Decorators

- `@token_required` — route requires valid JWT
- `@optional_auth` — route works with or without JWT (public/private data split)
- `@admin_required` — admin role only
- `@moderator_required` — moderator or admin role

### Register

**POST** `/api/auth/register`
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "Secure@123"
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": { "user_id": "...", "username": "johndoe", "role": "user" },
  "token": "eyJ..."
}
```

### Login

**POST** `/api/auth/login`
```json
{ "username": "johndoe", "password": "Secure@123" }
```
**Response (200):**
```json
{
  "success": true,
  "user": { "user_id": "...", "username": "johndoe", "role": "user" },
  "token": "eyJ..."
}
```

---

## Worlds

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/worlds` | Optional | List worlds (paginated) |
| POST | `/api/worlds` | Required | Create world |
| GET | `/api/worlds/{world_id}` | Optional | World details |
| PUT | `/api/worlds/{world_id}` | Required | Update world |
| DELETE | `/api/worlds/{world_id}` | Required | Delete world |
| GET | `/api/worlds/{world_id}/stories` | Optional | Stories in world |
| GET | `/api/worlds/{world_id}/characters` | — | Characters in world |
| GET | `/api/worlds/{world_id}/locations` | — | Locations in world |
| PUT | `/api/worlds/{world_id}/entities/{entity_id}` | Required | Update entity |
| DELETE | `/api/worlds/{world_id}/entities/{entity_id}` | — | Delete entity |
| DELETE | `/api/worlds/{world_id}/locations/{location_id}` | — | Delete location |
| GET | `/api/worlds/{world_id}/relationships` | — | Relationship SVG |
| POST | `/api/worlds/{world_id}/auto-link-stories` | Optional | Auto-link stories |
| POST | `/api/worlds/{world_id}/share` | Required | Share with users |
| POST | `/api/worlds/{world_id}/unshare` | Required | Remove user access |

### Create World

**POST** `/api/worlds`
```json
{
  "name": "Vương quốc Eldoria",
  "world_type": "fantasy",
  "description": "Một vương quốc cổ đại với 3 vị vua...",
  "visibility": "private",
  "gpt_entities": null
}
```

Query params for `GET /api/worlds`: `page` (default 1), `per_page` (default 20, max 100)

**Response (201):**
```json
{
  "success": true,
  "data": {
    "world_id": "uuid-123",
    "name": "Vương quốc Eldoria",
    "world_type": "fantasy",
    "entities": ["entity-id-1"],
    "locations": ["location-id-1"],
    "visibility": "private",
    "owner_id": "user-id"
  },
  "message": "World created successfully"
}
```

---

## Stories

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/stories` | Optional | List stories (paginated) |
| POST | `/api/stories` | Required | Create story |
| GET | `/api/stories/{story_id}` | Optional | Story details |
| PUT | `/api/stories/{story_id}` | Required | Update story |
| DELETE | `/api/stories/{story_id}` | Required | Delete story |
| POST | `/api/stories/{story_id}/link-entities` | — | Link characters/locations |
| POST | `/api/stories/{story_id}/clear-links` | — | Clear all entity links |

### Create Story

**POST** `/api/stories`
```json
{
  "world_id": "uuid-123",
  "title": "Cuộc phiêu lưu của John",
  "description": "John khám phá khu rừng bí ẩn...",
  "genre": "adventure",
  "visibility": "private",
  "time_index": 10,
  "selected_characters": ["entity-id-1", "entity-id-2"]
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "story": { "story_id": "story-uuid", "title": "...", ... },
    "time_cone": { "time_cone_id": "tc-uuid", ... }
  },
  "message": "Story created successfully"
}
```

---

## GPT Integration

All GPT operations are **asynchronous**. They return a `task_id` immediately. Poll `/api/gpt/results/{task_id}` until `status` is `completed` or `error`.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/gpt/analyze` | Required | Analyze description (world or story) |
| POST | `/api/gpt/generate-description` | Required | Generate world/story description |
| POST | `/api/gpt/batch-analyze-stories` | Required | Batch analyze (max 3 stories) |
| GET | `/api/gpt/results/{task_id}` | — | Poll task result |
| GET | `/api/gpt/tasks` | — | List pending tasks |

### Analyze

**POST** `/api/gpt/analyze`
```json
{
  "story_description": "Cuộc phiêu lưu của anh hùng Minh...",
  "story_title": "Hành trình vĩ đại",
  "story_genre": "adventure"
}
```

**Response (200):**
```json
{ "task_id": "task-uuid-456" }
```

**Poll `GET /api/gpt/results/task-uuid-456`:**
```json
{
  "status": "completed",
  "result": {
    "entities": [{ "name": "Minh", "entity_type": "hero", "description": "..." }],
    "locations": [{ "name": "Khu rừng", "description": "..." }]
  }
}
```

Task status values: `pending` → `processing` → `completed` | `error`

---

## Events / Timeline

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/worlds/{world_id}/events` | — | World timeline |
| POST | `/api/worlds/{world_id}/events/extract` | — | Extract events (async, `?force=true`) |
| POST | `/api/stories/{story_id}/events/extract` | — | Extract story events (async) |
| DELETE | `/api/stories/{story_id}/events/cache` | — | Clear event cache |
| PUT | `/api/events/{event_id}` | — | Update event |
| DELETE | `/api/events/{event_id}` | — | Delete event |
| POST | `/api/events/{event_id}/connections` | — | Add connection between events |

---

## Facebook

All Facebook endpoints require `@token_required` + `facebook_access` permission in user metadata (granted by admin).

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/facebook/token/exchange` | Exchange short → long-lived token |
| GET | `/api/facebook/pages` | List managed pages |
| GET | `/api/facebook/me` | Facebook user info |
| GET | `/api/facebook/pages/{page_id}/posts` | Page posts |
| POST | `/api/facebook/pages/{page_id}/posts` | Create post |
| GET | `/api/facebook/posts/{post_id}` | Post details |
| GET | `/api/facebook/posts/{post_id}/comments` | Post comments |
| GET | `/api/facebook/pages/{page_id}/search` | Search posts by keyword |
| POST | `/api/facebook/generate-content` | GPT-generate post content (async) |

Facebook Graph API errors are returned as `502 external_service_error`.

---

## Admin

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/admin/users` | Admin | List users (filter by role/search) |
| GET | `/api/admin/users/{user_id}` | Moderator+ | User details |
| PUT | `/api/admin/users/{user_id}/role` | Admin | Change user role |
| POST | `/api/admin/users/{user_id}/ban` | Moderator+ | Ban/unban user |
| PUT | `/api/admin/users/{user_id}/facebook-access` | Admin | Toggle Facebook access |
| GET | `/api/admin/roles` | Moderator+ | Role definitions & permissions |
| GET | `/api/admin/stats` | Moderator+ | Admin statistics |

Roles: `guest` → `user` → `premium` → `moderator` → `admin`

---

## Statistics & Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/stats` | Optional | System statistics + user quota |
| GET | `/api/health` | — | Health check |

---

## Request Validation

POST/PUT endpoints validate request bodies using **Marshmallow schemas**. Validation errors return `400 validation_error`:

```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": {
      "title": ["Length must be between 1 and 200."],
      "visibility": ["Must be one of: draft, private, public."]
    }
  }
}
```

Schemas defined in `api/schemas/`:
- `world_schemas.py` — `CreateWorldSchema`, `UpdateWorldSchema`, `ListWorldsQuerySchema`, `CreateEntitySchema`
- `story_schemas.py` — `CreateStorySchema`, `UpdateStorySchema`, `ListStoriesQuerySchema`
- `auth_schemas.py` — `RegisterSchema`, `LoginSchema`, `ChangePasswordSchema`, `UpdateProfileSchema`

---

## Testing

### curl

```bash
# Health check
curl http://localhost:5000/api/health

# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"Test@1234"}'

# Create world (replace TOKEN)
curl -X POST http://localhost:5000/api/worlds \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test World","world_type":"fantasy","description":"A test world"}'

# List worlds (paginated)
curl "http://localhost:5000/api/worlds?page=1&per_page=10"
```

### Swagger UI

1. Open http://localhost:5000/api/docs
2. Click "Authorize" and enter `Bearer <token>`
3. Click any endpoint → "Try it out" → fill params → "Execute"

### Import to Postman

1. Open Postman → Import → Link
2. Paste: `http://localhost:5000/apispec.json`

---

## CORS

- **Allowed Origins**: `http://localhost:3000`, `http://127.0.0.1:3000`
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Content-Type, Authorization

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Swagger UI blank | `pip install flasgger` then restart |
| CORS errors | Ensure frontend runs on port 3000 |
| GPT returns 502 | Check `.env` has `OPENAI_API_KEY`; run `python api/test_api_key.py` |
| Facebook returns 403 | User needs `facebook_access` permission — set via admin panel |
| 401 on protected route | Include `Authorization: Bearer <token>` header |
