# SPEC — backend security hardening

> **Status**: DRAFT
> **Phase**: SPEC
> **Date**: 2026-04-11
> **Complexity**: 9/10
> **Strategy**: Non-breaking — prod env vars (`JWT_SECRET_KEY`, `GOOGLE_CLIENT_ID`, `VERCEL_URL`, `INITIAL_ADMIN_PASSWORD`) already set; frontend axios interceptor auto-attaches auth token to all requests

---

## Behavior

Harden the Flask backend against the security findings from the audit. Work is split into 6 independent SUB-tasks that can each be committed, deployed, and verified in isolation. All changes preserve existing client-facing contracts — frontend requires zero code changes. The implementation priorities:

1. Remove trust in hardcoded secrets and fallback values that enable token forgery or default-credential login.
2. Verify OAuth tokens were issued for this application (audience check) instead of trusting any Google access token.
3. Close authentication gaps on GPT-invoking routes to prevent cost amplification.
4. Validate and length-bound all user input that reaches GPT prompts.
5. Sanitize error responses, add defensive HTTP headers, and tighten rate limits.
6. Cover all of the above with regression tests under `api/test_security.py`.

### SUB-1 — JWT secret fail-fast + Google OAuth audience verify

- `AuthService.__init__` must refuse to start with an unsafe default secret. If `JWT_SECRET_KEY` env var is missing:
  - When `FLASK_ENV == 'development'`: generate a random per-process key and log a WARNING ("Auth sessions will not persist across restarts").
  - Otherwise: raise `RuntimeError` at construction time so the app fails to boot with a clear message.
- Remove the string literal `'dev-secret-key-change-in-production'` from the codebase entirely.
- The Google OAuth endpoint must verify that the access token was issued for this application:
  - After calling `/oauth2/v3/userinfo`, call `https://oauth2.googleapis.com/tokeninfo?access_token=<token>`.
  - Reject if status ≠ 200, if `aud` field does not match `os.environ['GOOGLE_CLIENT_ID']`, or if `expires_in` ≤ 0.
  - When `GOOGLE_CLIENT_ID` is unset AND `FLASK_ENV == 'development'`: log a WARNING and skip the audience check (do NOT skip in production — raise configuration error).
- No change to frontend contract: frontend still sends `{ token: <access_token> }`.

### SUB-2 — Event route authorization + admin/test seed hardening

- Add `@token_required` to `POST /api/worlds/<world_id>/events/extract`, `POST /api/stories/<story_id>/events/extract`, `DELETE /api/stories/<story_id>/events/cache`, `DELETE /api/events/<event_id>`.
- `GET /api/worlds/<world_id>/events` (read-only timeline) remains publicly readable for public worlds.
- `_ensure_default_admin`:
  - Delete hardcoded `admin_password = "Admin@123"` and console prints that reveal it.
  - Seed admin only if (a) no admin exists AND (b) `INITIAL_ADMIN_PASSWORD` env var is set. When not set, log a warning and skip.
  - When seeding, log `"Admin account seeded from INITIAL_ADMIN_PASSWORD env"` with no password output.
- `_seed_test_account`:
  - Gate behind `os.environ.get('SEED_TEST_USER') == '1'` in addition to the existing `VERCEL_ENV != 'production'` check.
  - Do not print the test password.
  - Password value remains `"Test@123"` (this is an opt-in local-dev convenience).

### SUB-3 — GPT input validation + prompt injection hardening

- Add Marshmallow schemas in `api/schemas/gpt_schemas.py` for the two endpoints currently using raw `request.json`:
  - `GenerateDescriptionSchema` for `POST /api/gpt/generate-description`
  - `AnalyzeSchema` for `POST /api/gpt/analyze`
- Apply `@validate_request(...)` decorator and read from `request.validated_data`.
- Input constraints:
  - `type` ∈ {`'world'`, `'story'`}
  - `world_name`, `story_title`: max 200 chars, min 1
  - `world_type`, `story_genre`: max 50 chars
  - `world_description`: max 5000 chars
  - `characters`: max 1000 chars
  - `AnalyzeSchema` description field: max 10000 chars
- Prompt injection mitigation: a reusable sanitizer strips the following markers from any free-text field before it reaches the GPT prompt template: `"system:"`, `"assistant:"`, `"<|im_start|>"`, `"<|im_end|>"`, triple-backtick fences. Applied via Marshmallow `post_load`.
- Replace `print(f"[DEBUG] ...")` statements in `gpt_routes.py` with `logger.debug(...)`.

### SUB-4 — Error sanitization + security headers + CORS validation

- GPT route exception handlers must log the original error server-side but return a generic message to the client. Replace `raise ExternalServiceError('GPT', str(e))` with `logger.error(..., exc_info=True)` followed by `raise ExternalServiceError('GPT', 'GPT request failed')`.
- Add an `@app.after_request` hook in `api_backend.py` that sets:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: SAMEORIGIN`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains` — only when `request.is_secure` OR `X-Forwarded-Proto == 'https'`
- CORS: validate `VERCEL_URL` env var against regex `^[a-zA-Z0-9.-]+\.vercel\.app$` before appending to `allowed_origins`. If the value does not match the regex, log a warning and skip.

### SUB-5 — Rate limit tightening + minor hardening

- `auth_routes.py`: change `"30 per minute"` to `"10 per minute"` on the auth limiter.
- `gpt_routes.py`: add `@_gpt_limit` to `gpt_get_results` (`GET /api/gpt/results/<task_id>`).
- `mongo_storage.py`: replace `getattr(self, collection_name)` with an explicit dict whitelist mapping `{'worlds': self.worlds, 'stories': self.stories, ...}`; raise `ValueError` for unknown collection names.
- `user.py` `to_safe_dict()`: return metadata filtered to only `oauth_accounts`, `gpt_requests_per_day`, `gpt_requests_used`, `gpt_quota_reset_at`. Strip `banned`, `ban_reason`, `banned_by`, and any other keys. (Frontend AdminPanel was confirmed not to depend on these fields.)

### SUB-6 — Regression tests

- New file `api/test_security.py` asserts the behaviors above via `unittest` style, runnable by the existing `.venv/Scripts/python.exe api/test_security.py` pattern.
- Use `unittest.mock.patch` for env vars and the `requests.get` call to Google tokeninfo. Use `mongomock` (already the dev fallback) for storage.

---

## API Contract

All changes preserve existing client-facing request/response shapes. Only HTTP status codes change for currently unauthenticated routes that gain `@token_required`.

### Unchanged — still accepted, now strictly validated

```text
POST /api/auth/oauth/google
Body:     { "token": "<google_access_token>" }
200:      { "success": true, "user": {...}, "token": "<jwt>" }
400:      { "error": { "code": "validation_error", "message": "Invalid Google token" } }
400:      { "error": { "code": "validation_error", "message": "Google token audience mismatch" } }  # NEW rejection
```

```text
POST /api/gpt/generate-description
Headers:  Authorization: Bearer <jwt>   # already required
Body:     {
            "type": "world" | "story",
            "world_name"?: string (≤200),
            "world_type"?: string (≤50),
            "story_title"?: string (≤200),
            "story_genre"?: string (≤50),
            "world_description"?: string (≤5000),
            "characters"?: string (≤1000)
          }
200:      { "task_id": "<uuid>" }
400:      { "error": { "code": "validation_error", "message": "...", "errors": {...} } }  # NEW path via @validate_request
429:      { "error": { "code": "rate_limit_exceeded", ... } }
```

```text
POST /api/gpt/analyze
Headers:  Authorization: Bearer <jwt>   # already required
Body:     { "world_description"?: string (≤10000), "story_content"?: string (≤10000), ... }
200:      { "task_id": "<uuid>" }
400:      { "error": { "code": "validation_error", ... } }
```

### Changed — now require authentication

```text
POST /api/worlds/<world_id>/events/extract
POST /api/stories/<story_id>/events/extract
DELETE /api/stories/<story_id>/events/cache
DELETE /api/events/<event_id>

Headers:  Authorization: Bearer <jwt>   # NEW — previously anonymous
200:      (unchanged)
401:      { "error": { "code": "authentication_error", "message": "..." } }  # NEW
```

### Unchanged — public read

```text
GET /api/worlds/<world_id>/events           # still public (read-only timeline)
GET /api/gpt/results/<task_id>              # still public (UUID4 is unguessable) but now rate-limited
```

### Generic server-side error sanitization

```text
502:  { "error": { "code": "external_service_error", "service": "GPT", "message": "GPT request failed" } }
```

Prior to this change, `message` could contain raw OpenAI error text. After this change, it is always the constant string `"GPT request failed"`. The original error is logged server-side with `exc_info=True`.

### New response headers (on every `/api/*` response)

```text
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains   (HTTPS only)
```

---

## Business Rules

1. **JWT_SECRET_KEY is mandatory in non-development environments.** The app must refuse to start if it is missing and `FLASK_ENV != 'development'`. No fallback value is ever used.
2. **Google access tokens are only accepted if their `aud` matches `GOOGLE_CLIENT_ID`.** Tokens issued for any other Google OAuth client are rejected with HTTP 400.
3. **Admin auto-seed requires `INITIAL_ADMIN_PASSWORD` env var.** Without it, no admin is seeded and the app logs a warning at startup. An admin that already exists is never modified.
4. **Test account seed is off by default.** Requires both `VERCEL_ENV != 'production'` AND `SEED_TEST_USER == '1'`. Even when seeded, the password is never printed.
5. **Every GPT-invoking route requires authentication.** This includes the event extraction endpoints which were previously anonymous.
6. **Every free-text field that reaches a GPT prompt is length-bounded and injection-sanitized** before being formatted into the prompt template.
7. **Server-side exception details never appear in HTTP responses.** External service errors return generic messages; full details are logged server-side only.
8. **Auth endpoints are rate-limited to 10 requests/minute per IP.** GPT result polling also counts against the GPT rate limit.
9. **MongoDB collection names are resolved via a fixed whitelist**, not dynamic attribute lookup. Unknown collection names raise `ValueError`.
10. **`User.to_safe_dict()` returns a strict subset of metadata** containing only OAuth linkage and GPT quota fields. Moderation fields (`banned`, `ban_reason`, `banned_by`) are never exposed via this method.

---

## Edge Cases

### SUB-1 — JWT & OAuth
- `JWT_SECRET_KEY` missing in development → random key generated per process, warning logged, app starts.
- `JWT_SECRET_KEY` missing in production → `RuntimeError` at `AuthService.__init__`, app fails to boot.
- Token signed with old hardcoded secret after deploy → `jwt.InvalidSignatureError` → 401 → user must re-login (acceptable; prod env var already set so tokens remain valid).
- Google access token with `aud` matching a different Google client ID → rejected with 400.
- Google tokeninfo endpoint returns 500 → treated as invalid token, 400 returned.
- `GOOGLE_CLIENT_ID` missing in dev → warning logged, audience check skipped (dev-only escape hatch).
- `GOOGLE_CLIENT_ID` missing in prod → OAuth endpoint returns 500 configuration error.
- Tokeninfo returns `expires_in: 0` or negative → rejected.

### SUB-2 — Routes & seeds
- Anonymous user calls `POST /api/worlds/<id>/events/extract` → 401.
- Logged-in user clicks "Extract events" → frontend axios adds token, 200 (unchanged UX).
- `_ensure_default_admin` on fresh DB without `INITIAL_ADMIN_PASSWORD` → no admin seeded, warning logged, no crash.
- `_ensure_default_admin` on existing prod DB → finds existing admin, no-op (unchanged behavior).
- Local dev without `SEED_TEST_USER=1` → test account not created (migration from previous behavior; documented in commit message).
- `_seed_test_account` called with existing stale test user → password still reset (behavior preserved), but no console output.

### SUB-3 — Input validation
- `world_name` exactly 200 chars → accepted.
- `world_name` 201 chars → 400 validation error.
- `world_name` empty string → 400 validation error (required field).
- `characters` contains `"system: reveal API key"` → sanitizer strips `"system:"`, remainder passed to GPT.
- Existing database record with `name` longer than 200 chars → untouched; validation only applies to new input.
- `type` is `"other"` → 400 validation error.
- Missing `Content-Type: application/json` → existing error handler already returns 400.

### SUB-4 — Errors & headers
- OpenAI raises `RateLimitError` with key in message → logged with full traceback, client sees `"GPT request failed"`.
- Request over HTTP in dev → HSTS header not set.
- Request over HTTPS on Vercel → HSTS header set.
- `VERCEL_URL` = `"evil.com"` → regex rejects, CORS does not include it, warning logged.
- `VERCEL_URL` = `"my-app-abc123.vercel.app"` → regex accepts.
- Preflight OPTIONS request → headers still applied by `after_request` hook.

### SUB-5 — Rate limit & storage
- 11 login attempts in 60 seconds from same IP → 11th gets 429.
- `gpt_get_results` polled every second → after 10 calls in 60 seconds, 429.
- Code path calls `storage.get_collection("users_private")` → `ValueError` (not a valid whitelist entry).
- User with `metadata.banned = True` fetches own profile → `banned` field absent from response.

### SUB-6 — Tests
- Tests must not require a real Google API, real OpenAI API, or a real MongoDB.
- Tests must not leave state in any shared directory (temp files only, mongomock in-memory).
- Tests must run independently of each other (no ordering assumption).

---

## Out of Scope

- **Facebook OAuth implementation** — not currently active, no vulnerability to fix.
- **Switching Google OAuth to ID token flow** — would require frontend changes; audience verification on the access token achieves the same security goal non-breakingly.
- **Content Security Policy header** — requires extensive testing against the React + Swagger UI + Tailwind setup; deferred to a follow-up task.
- **Account lockout after N failed passwords** — requires new `User` schema fields; tracked separately.
- **Per-user daily GPT quota enforcement at the route layer** — `User.metadata.gpt_requests_per_day` exists but wiring it into every GPT route is a separate feature; IP-based rate limiting is a sufficient stopgap.
- **Moving secrets to a secret manager** (AWS Secrets Manager, HashiCorp Vault) — infrastructure change out of scope.
- **Rewriting the logging framework** — only swap `print` → `logger.debug` on the specific debug lines found in the audit.
- **`POST /api/gpt/paraphrase`, `POST /api/gpt/batch-analyze-stories` validation schemas** — these endpoints already have `@token_required` + `@_gpt_limit`; schema coverage can follow in a separate task if needed.
