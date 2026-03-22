# Flask API Refactoring — Implementation Record

**Project**: Story Creator (`api/`)
**Status**: All 5 phases complete
**Stack**: Flask 3.0+, Marshmallow, Flask-Limiter, TinyDB

---

## Overview

This document records the full refactoring of the Story Creator Flask API from ad-hoc patterns to a consistent, production-grade architecture. The work was done incrementally across 5 phases — each phase builds on the previous and can be reviewed independently.

### Core principles applied throughout

- **Exceptions over returns** — routes never call `jsonify({'error': ...})`, they raise typed exceptions that the global handler converts to JSON
- **Schemas for all inputs** — every POST/PUT endpoint validates through a Marshmallow schema before any business logic runs
- **Standardized responses** — all success responses use utility functions (`success_response`, `created_response`, etc.) with a consistent envelope
- **Auth on every mutating endpoint** — all DELETE/PUT/POST endpoints that modify data require `@token_required`

---

## Phase 1 — Foundation Layer

**Goal**: Create the shared infrastructure that all other phases depend on.

### New files

#### `api/core/exceptions.py` — Typed exception hierarchy

```python
APIException              # base (never raised directly)
├── ValidationError       # 400 — schema or business validation failed
├── ResourceNotFoundError # 404 — record doesn't exist
├── PermissionDeniedError # 403 — authenticated but not authorized
├── AuthenticationError   # 401 — missing or invalid token
├── QuotaExceededError    # 429 — user hit a usage limit
├── ConflictError         # 409 — duplicate resource
├── BusinessRuleError     # 400 — domain rule violated
└── ExternalServiceError  # 502 — GPT / Facebook API failure
```

Usage:
```python
# Before
if not world:
    return jsonify({'error': 'World not found'}), 404

# After
if not world:
    raise ResourceNotFoundError('World', world_id)
```

#### `api/interfaces/error_handlers.py` — Global error handler

Registered once in `api_backend.py`. Catches all `APIException` subclasses and converts them to a standardized JSON envelope. 5xx errors are also logged automatically.

Error response format:

```json
{
  "success": false,
  "error": {
    "code": "resource_not_found",
    "message": "World not found: abc-123",
    "details": { "resource_type": "World", "resource_id": "abc-123" }
  }
}
```

#### `api/utils/responses.py` — Response utilities

```python
success_response(data, message=None, status=200)   # generic 200
created_response(data, message=None)               # 201
deleted_response(message)                          # 200 after delete
paginated_response(items, page, per_page, total)   # list endpoints
accepted_response(data, message=None)              # 202 async tasks
```

Usage:
```python
# Before (inconsistent across routes)
return jsonify({'success': True, 'world': world_data}), 201
return jsonify([world1, world2])

# After
return created_response(world_data, "World created successfully")
return paginated_response(worlds, page, per_page, total)
```

#### `api/utils/validation.py` — Validation decorators

```python
@validate_request(SchemaClass)       # validates request.json
@validate_query_params(SchemaClass)  # validates request.args
```

Both store the validated result in `request.validated_data`.

Usage:
```python
# Before (20+ lines of manual validation per endpoint)
def create_world():
    data = request.json
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    if data.get('world_type') not in ['fantasy', 'sci-fi', ...]:
        return jsonify({'error': 'Invalid world type'}), 400

# After (3 lines)
@validate_request(CreateWorldSchema)
def create_world():
    data = request.validated_data  # already validated
```

#### `api/schemas/` — Marshmallow schemas

| File | Schemas |
| ---- | ------- |
| `world_schemas.py` | `CreateWorldSchema`, `UpdateWorldSchema`, `ListWorldsQuerySchema`, `CreateEntitySchema`, `UpdateEntitySchema` |
| `story_schemas.py` | `CreateStorySchema`, `UpdateStorySchema`, `ListStoriesQuerySchema`, `LinkEntitiesSchema`, `AddStoryEventSchema` |
| `auth_schemas.py` | `RegisterSchema`, `LoginSchema`, `ChangePasswordSchema` |
| `event_schemas.py` | `UpdateEventSchema`, `AddEventConnectionSchema` |
| `admin_schemas.py` | `ChangeUserRoleSchema`, `BanUserSchema`, `ListUsersQuerySchema` |

### Modified files

**`api/interfaces/auth_middleware.py`**: All decorators now raise exceptions instead of returning JSON directly.
- `@token_required` → raises `AuthenticationError`
- `@admin_required` → raises `PermissionDeniedError`
- `@moderator_required` → raises `PermissionDeniedError`

**`api/interfaces/api_backend.py`**: Registered error handlers and middleware at startup.

**`api/requirements.txt`**: Added `marshmallow>=3.20.1`, `flask-limiter>=3.5.0`.

---

## Phase 2 — Route Refactoring

**Goal**: Apply Phase 1 patterns to every route file.

### Changes per file

**`world_routes.py`** (14 endpoints)
- `@validate_request(CreateWorldSchema)` on `create_world`
- `@validate_request(UpdateWorldSchema)` on `update_world`
- `@validate_query_params(ListWorldsQuerySchema)` on `list_worlds`
- All `return jsonify({'error': ...})` → `raise` typed exceptions
- All success returns → `success_response()`, `created_response()`, `deleted_response()`
- Extracted `_create_entities_from_gpt()`, `_create_random_entities()` helpers
- Deleted `world_routes_refactored_example.py` (was Phase 1 reference, now obsolete)

**`story_routes.py`**
- `@validate_request(CreateStorySchema)` on `create_story`
- `@validate_request(UpdateStorySchema)` on `update_story`
- `@validate_query_params(ListStoriesQuerySchema)` on `list_stories`
- Added `time_index` and `selected_characters` fields to `CreateStorySchema`
- Extracted `_resolve_linked_entities()`, `_set_world_time()` helpers

**`auth_routes.py`**

- `@validate_request(RegisterSchema)` on `register` → raises `ConflictError` on duplicate
- `@validate_request(LoginSchema)` on `login` → raises `AuthenticationError` on bad credentials
- OAuth routes → raise `ExternalServiceError` on API failures
- Extracted `_get_user_from_auth_header()` (removes 3 duplicated token-check blocks)
- Success responses keep `{success, user, token}` format (no `data` wrapper) for frontend compatibility

**`gpt_routes.py`**

- `return jsonify(...), 503` → `raise ExternalServiceError('GPT', ...)`
- Missing required fields → `raise APIValidationError`
- Missing task → `raise ResourceNotFoundError`
- Batch size exceeded → `raise BusinessRuleError`

**`event_routes.py`**

- All 404 patterns → `raise ResourceNotFoundError`
- GPT unavailable → `raise ExternalServiceError`
- Success responses → `success_response()`, `deleted_response()`

**`facebook_routes.py`**

- `_check_facebook_access()` (returned `jsonify` 403) → `_require_facebook_access()` (raises `PermissionDeniedError`)
- `_check_fb_result()` raises `ExternalServiceError` on Facebook API errors

**`admin_routes.py`**

- Removed all blanket `try/except Exception as e: return jsonify({'success': False, ...}), 500`
- All 404/400/403 → typed exceptions

**`stats_routes.py`**

- `return jsonify(result)` → `return success_response(result)`

---

## Phase 3 — DRY Decorators

**Goal**: Eliminate repeated boilerplate patterns across routes.

Two new decorators added to `api/utils/validation.py`:

### `@extract_pagination(items_loader)`

Replaces the 7-line pagination block repeated in every list endpoint:

```python
# Before (in every list route)
params = request.validated_data
page = params.get('page', 1)
per_page = params.get('per_page', 20)
total = len(all_items)
start = (page - 1) * per_page
items = all_items[start:start + per_page]
return paginated_response(items, page, per_page, total)

# After
@validate_query_params(ListWorldsQuerySchema)
@extract_pagination(lambda: storage.list_worlds(user_id=g.current_user.user_id if hasattr(g, 'current_user') else None))
def list_worlds():
    pass  # response built by decorator
```

Applied to: `list_worlds` (world_routes), `list_stories` (story_routes).

### `@require_ownership(loader, resource_name, id_param, allow_shared=False)`

Centralizes resource loading + ownership check. Raises `ResourceNotFoundError` (404) if not found, `PermissionDeniedError` (403) if not owner/admin. Stores the loaded resource in `request.resource`.

```python
@token_required
@require_ownership(lambda wid: storage.load_world(wid), 'World', 'world_id')
def delete_world(world_id):
    world = request.resource  # already loaded and verified
    storage.delete_world(world_id)
    return deleted_response('World deleted')
```

Note: Not retrofitted onto existing routes where `PermissionService.can_edit/delete` is intentionally owner-only with no admin bypass. Available for new endpoints.

---

## Phase 4 — Production Features

**Goal**: Add structured logging and rate limiting.

### `api/interfaces/logging_middleware.py`

Registered via `register_logging_middleware(app)` in `api_backend.__init__`.

- `before_request`: records `g._request_start = time.monotonic()`
- `after_request`: logs `METHOD /path → STATUS (Xms)`
  - `INFO` for 2xx/3xx
  - `WARNING` for 4xx
  - `ERROR` for 5xx

### `api/interfaces/rate_limiter.py`

Registered via `create_limiter(app)`. Returns a no-op stub if `flask-limiter` is not installed (graceful degradation).

| Endpoint group | Limit | Reason |
| -------------- | ----- | ------ |
| `POST /api/auth/register` | 5 / min / IP | Brute-force protection |
| `POST /api/auth/login` | 5 / min / IP | Brute-force protection |
| `POST /api/gpt/*` | 10 / min / IP | API cost control |
| All other `/api/*` | 100 / min / IP | General DoS guard |

The limiter instance is passed into `create_auth_bp()` and `create_gpt_bp()` so per-route limits can be applied with `@_auth_limit` / `@_gpt_limit` inside the factory closures.

---

## Phase 5 — Security & Validation Audit

**Goal**: Fix all gaps discovered during a post-Phase-4 audit of every endpoint.

### Missing `@token_required` — 6 endpoints fixed

| Endpoint | File |
| -------- | ---- |
| `DELETE /api/worlds/<id>/entities/<entity_id>` | world_routes |
| `DELETE /api/worlds/<id>/locations/<location_id>` | world_routes |
| `POST /api/stories/<id>/link-entities` | story_routes |
| `POST /api/stories/<id>/clear-links` | story_routes |
| `PUT /api/events/<id>` | event_routes |
| `POST /api/events/<id>/connections` | event_routes |

### Missing `@validate_request` — 6 endpoints fixed

| Endpoint | Schema |
| -------- | ------ |
| `PUT /api/worlds/<id>/entities/<entity_id>` | `UpdateEntitySchema` (pre-existing) |
| `POST /api/stories/<id>/link-entities` | New `LinkEntitiesSchema` |
| `PUT /api/events/<id>` | New `UpdateEventSchema` |
| `POST /api/events/<id>/connections` | New `AddEventConnectionSchema` |
| `PUT /api/admin/users/<id>/role` | New `ChangeUserRoleSchema` (removed manual role validation) |
| `POST /api/admin/users/<id>/ban` | New `BanUserSchema` |

### Other fixes

- `extract_world_events` + `extract_story_events`: `return jsonify(...)` → `return success_response(...)`
- `GET /api/admin/users`: added `page`/`per_page` via `ListUsersQuerySchema` + `paginated_response()`

### New schema files created

- `api/schemas/event_schemas.py`
- `api/schemas/admin_schemas.py`

---

## File Map

```text
api/
├── core/
│   └── exceptions.py          # Phase 1 — typed exception hierarchy
├── utils/
│   ├── responses.py           # Phase 1 — success/error response helpers
│   └── validation.py          # Phase 1+3 — @validate_request, @validate_query_params,
│                              #              @extract_pagination, @require_ownership
├── schemas/
│   ├── world_schemas.py       # Phase 1+2
│   ├── story_schemas.py       # Phase 1+2+5
│   ├── auth_schemas.py        # Phase 1+2
│   ├── event_schemas.py       # Phase 5 (new)
│   └── admin_schemas.py       # Phase 5 (new)
├── interfaces/
│   ├── error_handlers.py      # Phase 1 — global exception → JSON
│   ├── logging_middleware.py  # Phase 4 — request/response logging
│   ├── rate_limiter.py        # Phase 4 — Flask-Limiter wrapper
│   ├── auth_middleware.py     # Phase 1 — @token_required raises exceptions
│   ├── api_backend.py         # Phase 1+4 — registers all middleware
│   └── routes/
│       ├── world_routes.py    # Phase 2+3+5
│       ├── story_routes.py    # Phase 2+3+5
│       ├── auth_routes.py     # Phase 2
│       ├── gpt_routes.py      # Phase 2+4
│       ├── event_routes.py    # Phase 2+5
│       ├── admin_routes.py    # Phase 2+5
│       ├── facebook_routes.py # Phase 2
│       └── stats_routes.py    # Phase 2
```

---

## Installation

```bash
# Activate virtual environment (Windows)
source .venv/Scripts/activate        # bash
.venv\Scripts\Activate.ps1           # PowerShell

# Install dependencies
pip install -r api/requirements.txt

# Run backend
.venv/Scripts/python.exe api/main.py -i api
```

## Testing

```bash
.venv/Scripts/python.exe api/test.py
.venv/Scripts/python.exe api/test_nosql.py
.venv/Scripts/python.exe api/test_api.py
```

---

## Patterns Reference

### Raising errors

```python
raise ResourceNotFoundError('World', world_id)     # 404
raise PermissionDeniedError('edit', 'world')       # 403
raise AuthenticationError('Token expired')         # 401
raise ValidationError('Bad input', details={...})  # 400
raise QuotaExceededError('Limit reached', current_count=5, limit=3)  # 429
raise ConflictError('Username already exists')     # 409
raise BusinessRuleError('Cannot share public worlds')  # 400
raise ExternalServiceError('GPT', 'API unavailable')   # 502
```

### Returning responses

```python
return success_response(data)
return success_response(data, "Optional message")
return created_response(data, "Resource created")
return deleted_response("Resource deleted")
return paginated_response(items, page, per_page, total)
return accepted_response({'task_id': tid}, "Processing started")
```

### Validating input

```python
@world_bp.route('/api/worlds', methods=['POST'])
@token_required
@validate_request(CreateWorldSchema)
def create_world():
    data = request.validated_data  # dict, already validated

@world_bp.route('/api/worlds', methods=['GET'])
@optional_auth
@validate_query_params(ListWorldsQuerySchema)
def list_worlds():
    params = request.validated_data  # page, per_page, etc.
```

### Backward compatibility note

Auth success responses (`/api/auth/register`, `/api/auth/login`, OAuth) intentionally return `{success, user, token}` without a `data` wrapper. The frontend parses this format directly. All other endpoints use the standard `{success, data}` envelope.
