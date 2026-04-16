---
name: backend-performance
description: Use this skill when editing backend startup, initialization, MongoDB connection, GPT client init, admin seeding, Swagger setup, or any module-level work that runs on import. Ensures Vercel cold-start stays fast (target sub-2s for /api/health). Triggers when editing api/app.py, api/main.py, api/interfaces/api_backend.py, api/storage/mongo_storage.py, api/ai/gpt_client.py, api/utils/env_config.py, or adding new module-level initialization.
---

# backend-performance — Cold-Start & Lazy Init Conventions

The API is deployed to Vercel serverless. A new function instance can spin up at any time, and the client sees the latency. Keep import-time work near zero and defer everything to first-use.

## Rules

1. **No network I/O, no DB connect, no GPT init at import time.** Module top-level must be safe to import in <200ms.
2. **No GPT client construction at import time.** If `OPENAI_API_KEY` is missing, GPT routes return 503; non-GPT routes must stay up.
3. **MongoDB connection is deferred.** `MongoStorage.__init__` stores config only. `_connect()` runs on first DB operation, guarded by a thread-safe double-checked lock.
4. **`/api/health` must never trigger heavy init.** Admin seeding, Swagger build, GPT warm-up all skip when the request path is `/api/health` or `/api/docs`.
5. **Swagger spec is lazy.** Build only on the first request to `/api/docs`. Cache the built spec on the app.
6. **Admin seeding is lazy.** Use a `before_request` hook with a module-level `_seeded` flag (thread-safe). Skip health/docs paths.
7. **Keep-alive from the frontend.** `useKeepAlive` hook pings `/api/health` every 5 minutes while the tab is visible. Pause on `visibilitychange=hidden`, resume on visible.

## Lazy init pattern

```python
import threading

_lock = threading.Lock()
_initialized = False
_resource = None

def get_resource():
    global _initialized, _resource
    if _initialized:
        return _resource
    with _lock:
        if _initialized:
            return _resource
        _resource = _expensive_init()
        _initialized = True
    return _resource
```

Use this for: GPT client, Mongo connection, Swagger spec, admin seeding flag.

## MongoDB-only (no fallbacks)

- TinyDB, JSON files, and `mongomock`-as-prod have all been removed from production paths
- `MONGODB_URI` is required — fail-fast on startup if missing in non-dev
- `mongomock` is still allowed as a dev fallback (when `APP_ENV=development` and no URI set)
- `api/requirements.txt` must not include `tinydb`

## Frontend keep-alive

Lives in `frontend/src/hooks/useKeepAlive.js`, mounted once in `App.jsx`:

- `fetch('/api/health')` every 5 minutes
- Silent: no toast, no console.log on success
- Pauses when `document.visibilityState === 'hidden'`
- Resumes when tab becomes visible again
- Cleans up interval on unmount

## Checklist before adding a new module-level init

- [ ] Does this run at import time? If yes, can it be deferred?
- [ ] Does it do network I/O, DB connect, file read? Must be deferred
- [ ] Will `/api/health` still respond in <500ms after this change?
- [ ] Thread-safe for concurrent requests to a cold-started worker?
- [ ] Does GPT failure / missing `OPENAI_API_KEY` still allow non-GPT routes to work?
