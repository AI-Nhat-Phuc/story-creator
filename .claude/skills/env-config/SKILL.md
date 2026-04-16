---
name: env-config
description: Use this skill when editing environment configuration, DB naming, prod/nonprod separation, test-account seeding, or the `APP_ENV` / `VERCEL_ENV` flags. Covers DB selection per environment, fail-fast rules for missing env vars, and opt-in test fixtures. Triggers when editing api/utils/env_config.py, api/app.py (DB name resolution), api/storage/mongo_storage.py (connection config), api/interfaces/api_backend.py (admin/test-user seeding), and .env / vercel.json.
---

# env-config — Environments, DB Naming, Seeding

Rules for environment-aware configuration across local dev, staging, and production.

## Environment flags

- `APP_ENV`  — primary env flag (`development` | `staging` | `production`). Unset / unknown → treat as `development` with a warning log
- `VERCEL_ENV` — Vercel-injected (`production` | `preview` | `development`). Used as a secondary gate (e.g., disable test-user seeding in production)
- `NODE_ENV`  — frontend only

## Database naming

All resolved by `get_mongo_db_name()` in `api/utils/env_config.py`:

| APP_ENV       | Mongo DB            | TinyDB path (dev only) |
|---------------|---------------------|------------------------|
| `production`  | `story_creator_prod`    | n/a (MongoDB required) |
| `staging`     | `story_creator_staging` | n/a                    |
| unset / dev   | `story_creator`         | `story_creator.db`     |

- `STORY_DB_PATH` env var overrides the TinyDB fallback path (legacy compat only — TinyDB is not used in prod)
- Invalid `APP_ENV` values → warn and fall back to development naming; never crash
- **No cross-env migration** — prod starts fresh; don't copy dev data into prod

## Required secrets (non-dev)

Fail fast on startup in non-dev environments when any of these are missing:

- `MONGODB_URI`
- `JWT_SECRET_KEY`
- `GOOGLE_CLIENT_ID` (if Google OAuth enabled)
- `FACEBOOK_APP_ID` (if FB OAuth enabled)
- `OPENAI_API_KEY` is NOT fail-fast — missing it degrades GPT routes to 503 but keeps the app running

In `development`, missing secrets log a WARNING and synthesize safe defaults (random JWT secret per process, mongomock for DB).

## Test-account seeding

Hardcoded test user is **opt-in** and **nonprod-only**:

- Seeded only when BOTH: `SEED_TEST_USER=1` AND `VERCEL_ENV != 'production'`
- Default credentials: `test@example.com` / `Test@123`
- Log message: `"test account seeded"` — NEVER log the password
- Seeding is lazy (runs on first request via `before_request` hook; see `backend-performance` skill)

## Frontend env

- `VITE_API_BASE_URL` — dev only, usually via Vite proxy. Prod uses `/api` (Vercel rewrite)
- Google/FB client IDs exposed via `VITE_GOOGLE_CLIENT_ID`, `VITE_FACEBOOK_APP_ID` (public by design)

## CORS origins

- `VERCEL_URL` added to CORS only if matches `^[a-z0-9\-]+\.vercel\.app$` — see `security-backend` skill
- Plus explicit allow list from `CORS_ORIGINS` env var (comma-separated)

## Checklist when touching env config

- [ ] New env var documented in README / CLAUDE.md
- [ ] Missing-value behavior explicit: fail-fast in prod or safe default in dev
- [ ] No secret leaks into logs, responses, or frontend bundles
- [ ] DB name resolution uses `get_mongo_db_name()` — don't inline env checks
- [ ] `APP_ENV=development` exercise still works with zero config (mongomock, random JWT)
