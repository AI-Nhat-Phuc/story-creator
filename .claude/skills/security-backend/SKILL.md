---
name: security-backend
description: Use this skill when editing backend code related to auth, JWT, OAuth, GPT prompt construction, error responses, CORS, rate limits, or user data serialization. Ensures all backend changes follow the security hardening conventions for story-creator (no hardcoded secrets, no information disclosure, validated request bodies, safe user serialization). Triggers when editing api/services/auth_service.py, api/interfaces/routes/gpt_routes.py, api/interfaces/routes/event_routes.py, api/schemas/gpt_schemas.py, api/core/models/user.py, api/interfaces/error_handlers.py, api/interfaces/api_backend.py.
---

# security-backend — Backend Security Conventions

These rules were established by the backend security hardening pass. Follow them every time you touch auth, GPT routes, error handling, or user serialization.

## Secrets & config

- **JWT**: Read `JWT_SECRET_KEY` from env. If missing:
  - Dev (`APP_ENV=development` or unset) → generate a random per-process secret and log a WARNING
  - Non-dev → raise on startup (fail-fast). Never fall back to a hardcoded default
- **Google OAuth**: After verifying the JWT signature, hit `https://oauth2.googleapis.com/tokeninfo?id_token=...` and assert `aud == GOOGLE_CLIENT_ID`. Reject if `aud` is missing or mismatched
- **CORS**: `VERCEL_URL` must match the regex `^[a-z0-9\-]+\.vercel\.app$` before being added to `CORS_ORIGINS`. Reject malformed values with a warning log
- Never commit hardcoded secrets. Never print secrets (including test passwords) to stdout/logs

## Request validation

- Every POST/PUT route that accepts a JSON body MUST use `@validate_request(SomeSchema)` and read from `request.validated_data` — never `request.get_json()` directly
- All GPT routes require validation. Schemas live in `api/schemas/gpt_schemas.py`
- All GPT routes require authentication (`@token_required`), including endpoints used by background generators
- Event routes also require `@token_required` (previously unauthenticated)

## Prompt-injection sanitization

Before passing user content into a GPT prompt, sanitize it. Strip these markers (case-insensitive, as standalone tokens or inline):

- `system:`, `assistant:`, `user:` role prefixes at line start
- `<|im_start|>`, `<|im_end|>`, `<|system|>`, `<|assistant|>`
- Triple-backtick code fences that wrap role-impersonation attempts
- Trim excessive whitespace + cap length to schema's `max_length`

The sanitizer lives in the GPT service layer. Call it on every user-sourced field (prompt, character description, etc.) before prompt assembly.

## Error handling & information disclosure

- Log full exceptions server-side with `logger.exception(...)` or `exc_info=True`
- Return only generic messages to clients:
  - GPT failure → `"GPT request failed"` (502 via `ExternalServiceError`)
  - Internal exceptions → `"Internal server error"` (500)
- Never include stack traces, SQL, env vars, or internal paths in HTTP responses
- Use typed exceptions from `core.exceptions` (see CLAUDE.md). The global handler in `api/interfaces/error_handlers.py` maps them to clean JSON

## Security response headers

Set via `after_request` hook in `api/interfaces/api_backend.py`:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (HTTPS only — check `request.is_secure` or `X-Forwarded-Proto`)

## Rate limits

- Auth routes (login, register, OAuth): 10/min per IP
- GPT routes: decorate with `@_gpt_limit` (configured per-endpoint; generator endpoints stricter)
- Use Flask-Limiter with in-memory storage on Vercel (single worker)

## User serialization

- Never return `password_hash`, internal flags (`banned`, `ban_reason`), or raw OAuth tokens to clients
- `User.to_safe_dict()` is the only acceptable path to send user data to an API client
- It uses an explicit `_SAFE_METADATA_KEYS` whitelist — only OAuth-identity fields and GPT quota counters
- Never add fields by editing `to_safe_dict()` blindly; update `_SAFE_METADATA_KEYS` deliberately

## Storage access

- No `getattr(storage, collection_name)` with dynamic strings. Use an explicit dict mapping allowed collection names to attributes, raising for unknown names
- This prevents a URL param from reaching `storage._internal` or similar

## Tests

- Security-sensitive changes require tests in `api/test_security.py`
- Mock `requests.get` for Google tokeninfo
- Use `mongomock` (no real MongoDB), no real network I/O, no real GPT calls

## Quick checklist before shipping an auth/GPT change

- [ ] No hardcoded secrets; JWT/OAuth IDs read from env with fail-fast in prod
- [ ] `@token_required` present on every sensitive route
- [ ] `@validate_request(Schema)` on every body-accepting route
- [ ] User-sourced GPT input sanitized
- [ ] No stack traces or internal detail in HTTP responses (logged, not returned)
- [ ] `User.to_safe_dict()` used; `_SAFE_METADATA_KEYS` updated if new metadata added
- [ ] Tests added/updated in `api/test_security.py`
