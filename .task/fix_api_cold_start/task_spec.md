# SPEC — Fix API Cold Start

> **Status**: DRAFT
> **Phase**: SPEC
> **Date**: 2026-04-08

---

## Behavior

The Flask API on Vercel suffers from cold start delays of 1.5–4+ seconds because
all heavy initialization (GPT client, admin seeding, Swagger) runs synchronously at
module import time. Additionally, TinyDB stores data in `/tmp/` on Vercel, which is
ephemeral — data is lost on every cold start. After a period of inactivity the
Vercel container is evicted, causing the next user request to wait through a full
cold start.

This feature reduces perceived cold start time and prevents container eviction by:

1. **Lazy GPT initialization**: `GPTIntegration` and its dependent services
   (`GPTService`, `EventService`) are not instantiated at startup. They are created
   on first use (i.e., when a GPT-related route is called).

2. **Lazy admin/test-account seeding**: `_ensure_default_admin()` and
   `_seed_test_account()` are removed from `APIBackend.__init__()` and replaced by a
   one-time-per-process flag. They run on the first non-health, non-docs request.

3. **Lazy Swagger initialization**: Flasgger spec is built only when `/api/docs` is
   first accessed, not during `APIBackend.__init__()`.

4. **Remove TinyDB — MongoDB only**: TinyDB (`NoSQLStorage`), JSON storage
   (`JSONStorage`), and all related fallback logic are removed from the codebase.
   MongoDB (`MongoStorage`) becomes the sole storage backend. The `MongoClient`
   connection is opened lazily on the first database operation (not in the
   constructor). `MONGODB_URI` is required; the app raises a clear startup error if
   it is missing.

5. **Frontend keep-alive ping**: The React app silently pings `GET /api/health` every
   5 minutes while the browser tab is active. This keeps the Vercel container warm
   between user sessions without requiring a paid cron job.

---

## API Contract

### Existing endpoint (unchanged behavior)

```text
GET /api/health
Response 200: { "status": "ok", "version": "...", "timestamp": "..." }
```

No new endpoints are introduced.

---

## Business Rules

1. GPT services (`GPTService`, `EventService`, `GPTIntegration`) MUST be initialized
   at most once per process. A thread-safe lazy-init guard must be used.

2. Admin seeding MUST run before any authenticated request is processed, but MUST NOT
   run during health check or Swagger requests to avoid delaying warm-up pings.

3. Admin seeding MUST run at most once per process (use a module-level boolean flag).

4. If GPT initialization fails (missing API key, import error), the API MUST continue
   to serve non-GPT routes exactly as it does today. GPT routes return 503.

5. `MongoStorage` MUST NOT open a network connection before the first DB call.
   Connection errors on first DB operation MUST surface as a clear 503 response —
   no silent fallback to TinyDB (TinyDB is removed).

6. `NoSQLStorage` (TinyDB), `JSONStorage`, and `tinydb` package references MUST be
   removed from: `api/storage/`, `api/interfaces/api_backend.py`,
   `api/utils/env_config.py`, and `api/requirements.txt`.

7. `MONGODB_URI` environment variable is now **required**. If absent at startup the
   app MUST log a clear error and raise `RuntimeError`.

8. The frontend keep-alive ping MUST be silent (no UI feedback, no error toasts on
   network failure). It MUST only run while the browser tab is visible
   (`document.visibilityState === "visible"`).

9. The keep-alive interval MUST be 5 minutes (300 000 ms). It MUST be cleared when
   the component unmounts or the app navigates away.

10. Keep-alive ping MUST use the existing `api.js` HTTP client (Axios), calling the
    existing health endpoint path (`/api/health`).

---

## Edge Cases

- **Concurrent first requests**: If two requests arrive simultaneously before GPT is
  initialized, only one initialization must occur. The second request must wait for
  the first to complete (use a lock or initialize-once pattern).

- **Health check during cold start**: The health endpoint must always respond
  immediately — it must never trigger admin seeding or GPT initialization.

- **Tab hidden**: Keep-alive interval must pause when tab is hidden
  (`visibilitychange` event) to avoid unnecessary pings from background tabs.

- **Ping failure**: If the health ping fails (network error, 5xx), the frontend must
  silently ignore it and retry on the next interval.

- **Missing MONGODB_URI**: App must fail fast at startup with a descriptive
  `RuntimeError` rather than silently writing to a temporary local file.

- **MongoDB connection failure on first request**: Return 503 with message
  `"Database unavailable"` — no crash, no fallback to TinyDB.

---

## Out of Scope

- Persistent in-memory caching (Redis, Memcached).
- Reducing Python dependency import times (packaging concern).
- Server-Side Rendering or edge functions for the frontend.
- Upgrading Vercel plan to use scheduled cron jobs.
- Pre-warming multiple Vercel regions simultaneously.
- Migrating existing TinyDB data to MongoDB (data migration is a separate task).
