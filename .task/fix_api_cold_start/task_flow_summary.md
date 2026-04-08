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
