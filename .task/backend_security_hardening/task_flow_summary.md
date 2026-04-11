# Flow Summary — backend security hardening

> **Status**: PENDING
> **File**: `api/interfaces/routes/auth_routes.py`
> **Date**: 2026-04-11
> **SUB**: 1 (Google OAuth audience verify) + 5 (auth rate limit)

---

## Current Flow

### `create_auth_bp(storage, auth_service, limiter=None)`

#### Input
- `storage`: storage backend
- `auth_service`: AuthService instance
- `limiter`: optional Flask-Limiter

#### Execution Steps (current)

1. Create `auth_bp = Blueprint('auth', __name__)`.
2. Resolve `_auth_limit`:
   ```python
   _auth_limit = limiter.limit("30 per minute") if limiter else (lambda f: f)
   ```
3. Register routes: `register`, `login`, `verify_token`, `change_password`, `get_current_user`, `update_profile`, `oauth_google`.
4. Return `auth_bp`.

### `oauth_google()` — current body

1. `data = request.get_json()`; read `google_token = data.get('token', '')`.
2. If empty → raise `APIValidationError('Missing Google token')`.
3. `requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={'Authorization': f'Bearer {google_token}'}, timeout=10)`.
4. If `response.status_code != 200` → raise `APIValidationError('Invalid Google token')`.
5. Parse `user_info = response.json()`.
6. Call `auth_service.find_or_create_oauth_user(provider='google', provider_user_id=user_info['sub'], email=..., name=..., avatar_url=...)`.
7. On success: generate JWT and return the user + token JSON.

### Observed Issues

- **Issue A (SUB-1 part 2)**: The handler accepts ANY Google access token from ANY Google OAuth client. If a Google token issued for an unrelated app is replayed, userinfo still returns a valid profile, and the attacker logs in as that profile's email. The audience of the token is never checked against `GOOGLE_CLIENT_ID`.
- **Issue B (SUB-5)**: `_auth_limit` is `"30 per minute"` — loose for brute-force protection. Spec calls for `"10 per minute"`.
- **Issue C (out of scope this task)**: `oauth_google` uses `request.get_json()` directly instead of `@validate_request(GoogleAuthSchema)`. Not fixed here — `GoogleAuthSchema` exists in `schemas/auth_schemas.py` but wiring it is deferred to a follow-up (would also change the field name from `token` → `credential`, which is a frontend-breaking contract change — explicitly out of scope per spec "frontend requires zero code changes").
- **Issue D (out of scope)**: Error path uses `jsonify(...)` directly in some places rather than `success_response` — spec explicitly preserves existing response shapes.

---

## Planned Changes

### Change 1 — Tighten auth rate limit (SUB-5)

Replace:
```python
_auth_limit = limiter.limit("30 per minute") if limiter else (lambda f: f)
```

With:
```python
# Tighter limit on auth endpoints: 10/min/IP (brute-force protection).
# Frontend login flow is one request per user action; 10/min is comfortable
# for real users while rejecting credential-stuffing bots.
_auth_limit = limiter.limit("10 per minute") if limiter else (lambda f: f)
```

And update the surrounding comment block to remove the "30/min allows automated e2e test suites" rationale (e2e suites can set a test env rate limit override via flask-limiter config if needed; not this file's concern).

### Change 2 — Google OAuth tokeninfo audience check (SUB-1 part 2)

Modify the `oauth_google()` body. New sequence:

1. Read `google_token` as today.
2. Read `os.environ.get('GOOGLE_CLIENT_ID')`. If unset:
   - If `FLASK_ENV == 'development'`: `logger.warning("GOOGLE_CLIENT_ID not set — skipping Google audience check (dev only)")` and skip to step 4.
   - Else: `raise ExternalServiceError('Google', 'GOOGLE_CLIENT_ID not configured')` (500 boundary — treat as configuration error).
3. Call `https://oauth2.googleapis.com/tokeninfo?access_token=<token>` with `timeout=10`. Validate:
   - `response.status_code == 200` → else `raise APIValidationError('Invalid Google token')`
   - `tokeninfo['aud'] == client_id` → else `raise APIValidationError('Google token audience mismatch')`
   - `int(tokeninfo.get('expires_in', 0)) > 0` → else `raise APIValidationError('Google token expired')`
4. Continue with the existing `/oauth2/v3/userinfo` call (unchanged), then `find_or_create_oauth_user` (unchanged), then generate JWT and return (unchanged).

**Import changes**: add `import os` at the top of the file.

**Exception handling**: the new tokeninfo call sits inside the same `try/except` block as the existing userinfo call. `APIValidationError` is re-raised; any other exception is caught by the generic `except Exception` → `ExternalServiceError('Google', 'Google authentication error', e)` (unchanged path).

### Change 3 — NONE for other routes in this file

- `register`, `login`, `verify_token`, `change_password`, `get_current_user`, `update_profile`, `_get_user_from_auth_header` are all **unchanged**.
- The `@validate_request(RegisterSchema)` decorator stays (already wired).
- The Vercel ephemeral-instance fallback in `_get_user_from_auth_header` stays (required for multi-instance deployment).

---

## Backward Compatibility

- **Prod** has `JWT_SECRET_KEY` and `GOOGLE_CLIENT_ID` set (pre-flight check #1 + #3). Real users signing in via the frontend will pass the audience check — the frontend uses the same `GOOGLE_CLIENT_ID` embedded in `VITE_GOOGLE_CLIENT_ID`, so access tokens are issued for that audience. Zero frontend change.
- **Dev** without `GOOGLE_CLIENT_ID`: warning logged, audience check skipped. Login still works. Documented as dev-only escape hatch.
- **Rate limit 30→10**: existing legitimate users never hit 10/min on auth endpoints (login is one request per user action). Automated test suites that were depending on 30/min need to either use separate IPs or a test-mode limiter override (tests already use `RATELIMIT_ENABLED=False` in `security_test_db` setup via `limiter.enabled = False`).

---

## Test coverage wired

- `TestGoogleOAuthAudience.test_matching_aud_succeeds` → will pass after this edit
- `TestGoogleOAuthAudience.test_mismatched_aud_rejected` → will pass
- `TestGoogleOAuthAudience.test_tokeninfo_non_200_rejected` → will pass
- `TestGoogleOAuthAudience.test_expired_token_rejected` → will pass
- `TestGoogleOAuthAudience.test_missing_client_id_in_dev_skips_check` → will pass
- `TestAuthRateLimit.test_11th_login_returns_429` → will pass
- `TestAuthRateLimit.test_limiter_configured_10_per_minute` → will pass
