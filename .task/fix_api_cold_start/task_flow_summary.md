# Flow Summary — api/interfaces/api_backend.py

> **Status**: PENDING APPROVAL
> **File**: api/interfaces/api_backend.py
> **Date**: 2026-04-08

---

## Current Flow

### Input

`APIBackend(db_path, mongo_db_name)` — called at module import by `api/app.py`.

### Execution Steps

1. Create `Flask(__name__)` + set secret key
2. Configure and apply `CORS`
3. **Call `Swagger(self.app, ...)` eagerly** ← 50–150 ms blocking
4. Register error handlers and logging middleware
5. Create rate limiter
6. Storage: try `MongoStorage(MONGODB_URI)` → fallback `NoSQLStorage(db_path)` → fallback `JSONStorage(data_dir)`
7. Instantiate generators: `WorldGenerator`, `StoryGenerator`, `StoryLinker`, `RelationshipDiagram`
8. **Try `GPTIntegration()` → `GPTService` → `EventService`** ← 200–500 ms blocking
9. Instantiate `AuthService` + `init_auth_middleware`
10. **Call `_ensure_default_admin()`** ← 100–200 ms (DB query + bcrypt hash)
11. **Conditionally call `_seed_test_account()`** ← 100–200 ms (DB query + bcrypt hash)
12. Instantiate `TaskStore`
13. Register signal handlers
14. Call `_register_blueprints()` — 9 blueprints

### Output

A fully-initialized `Flask` app, ready to serve. Total cold-start cost: ~1.5–4 s.

### Observed Issues

- Steps 3, 8, 10, 11 add 500–900 ms of unnecessary blocking work on every cold start.
- Step 6 imports `NoSQLStorage`/`JSONStorage` which no longer exist (deleted this task).
- `__init__` signature still carries TinyDB-era params (`data_dir`, `storage_type`, `db_path`).
- GPT blueprint receives `gpt`/`gpt_service` by value at registration — if `None` at init, the closures will hold stale `None` even after lazy init. Must pass `backend=self` to GPT/Event blueprints so routes call `backend._ensure_gpt()` at request time.

---

## Planned Changes

**Will add / modify:**

1. **Imports**: remove `NoSQLStorage, JSONStorage`; add `import threading`; add `from flask import request`
2. **Module-level sentinels** (after imports):
   ```python
   _gpt_initialized = False
   _gpt_lock = threading.Lock()
   _admin_seeded = False
   ```
3. **`__init__` signature**: remove `data_dir`, `storage_type`, `db_path`; add `mongodb_uri: str`
4. **Storage block**: single line — `self.storage = MongoStorage(mongodb_uri, db_name=mongo_db_name)`
5. **Swagger**: store config/template on `self._swagger_config` / `self._swagger_template`; set `self._swagger = None`; do NOT call `Swagger()`
6. **GPT block**: skip entirely — `self.gpt = None`, `self.gpt_service = None`, `self.event_service = EventService(None, self.storage)`, `self.has_gpt = False`
7. **Remove** `_ensure_default_admin()` and `_seed_test_account()` calls from `__init__`
8. **New `_ensure_gpt(self)`**: thread-safe double-checked locking; sets `self.gpt`, `self.gpt_service`, `self.event_service`, `self.has_gpt`
9. **New `_seed_once(self)`**: checks `_admin_seeded`; calls `_ensure_default_admin()` + conditional `_seed_test_account()`
10. **New `_ensure_swagger(self)`**: creates `Swagger(self.app, ...)` once on first `/api/docs` access
11. **`before_request` hook** registered in `__init__`: skips `/api/health`, `/api/docs`, `/flasgger`, `/apispec`; calls `self._seed_once()` for all other paths; calls `self._ensure_swagger()` for `/api/docs` and `/apispec`
12. **`_register_blueprints()`**: pass `backend=self` to `create_gpt_bp` and `create_event_bp` so they can call `backend._ensure_gpt()` at request time

**Will NOT change:**

- CORS setup
- Error handlers, logging middleware, rate limiter
- Generators instantiation
- `AuthService` + `init_auth_middleware`
- `TaskStore` instantiation
- Signal handlers
- `_ensure_default_admin()` and `_seed_test_account()` method bodies
- All non-GPT blueprints in `_register_blueprints()`
- `run()`, `_kill_existing_server()`, `_flush_data()`, `_signal_handler()`

---

## Flow Summary — api/interfaces/routes/gpt_routes.py

### Current Flow

**Input**: `create_gpt_bp(gpt, gpt_service, gpt_results, has_gpt, storage, flush_data, limiter)`
All parameters are captured by value in closures at blueprint creation time.

**Execution steps per request**:
1. Route handler reads `has_gpt` (closure bool) → raises 503 if `False`
2. Route handler reads `gpt` (closure object) → calls `gpt.client.chat.completions.create()`
3. Route handler reads `gpt_service` (closure object) → calls `gpt_service.analyze_*`

**Observed issue**: `has_gpt`, `gpt`, `gpt_service` are captured at registration. With lazy init they will always be `None`/`False`.

### Planned Changes

1. Add `backend` parameter to `create_gpt_bp` signature
2. Each GPT-using route calls `backend._ensure_gpt()` before checking `has_gpt`
3. Replace closure reads of `has_gpt`, `gpt`, `gpt_service` with `backend.has_gpt`, `backend.gpt`, `backend.gpt_service`

**Will NOT change**: route URLs, docstrings, business logic, threading patterns, `gpt_results` usage, `storage` usage, `flush_data` usage, limiter setup.

---

## Flow Summary — api/interfaces/routes/event_routes.py

### Current Flow

**Input**: `create_event_bp(storage, event_service, gpt_results, has_gpt)`
`event_service` and `has_gpt` captured by value at creation time.

**Execution steps per GPT-using request**:
1. Route checks `has_gpt` (closure bool) → raises 503 if `False`
2. Route calls `event_service.extract_events_from_world()` or `extract_events_from_story()`

**Observed issue**: Same as gpt_routes — `has_gpt` and `event_service` are stale if initialized lazily.

### Planned Changes

1. Add `backend` parameter to `create_event_bp` signature
2. GPT-using routes (`extract_world_events`, `extract_story_events`) call `backend._ensure_gpt()` before checking `has_gpt`
3. Replace `has_gpt` and `event_service` reads with `backend.has_gpt` and `backend.event_service`

**Will NOT change**: non-GPT routes (`get_world_timeline`, `update_event`, `delete_event`, `add_event_connection`, `clear_story_event_cache`), route URLs, business logic, docstrings.
