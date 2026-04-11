# Flow Summary — backend security hardening

> **Status**: PENDING
> **File**: `api/services/auth_service.py`
> **Date**: 2026-04-11
> **SUB**: 1 (JWT secret fail-fast)

---

## Current Flow

### `AuthService.__init__(storage, secret_key=None)`

#### Input
- `storage`: storage backend (MongoStorage or mongomock)
- `secret_key`: optional explicit secret; normally left as None

#### Execution Steps (current)

1. Save `self.storage = storage`
2. Resolve secret key:
   ```python
   self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
   ```
3. Set `self.algorithm = 'HS256'`, `self.token_expiry_hours = 24`
4. If resolved secret equals the hardcoded default, log a WARNING but continue.

#### Output
- An `AuthService` instance with `self.secret_key`, `self.algorithm`, `self.token_expiry_hours`.
- Always succeeds; never raises.

### Observed Issues

- **Issue 1 (THIS TASK — SUB-1)**: Hardcoded fallback `'dev-secret-key-change-in-production'` means any deployment that forgets to set `JWT_SECRET_KEY` silently signs tokens with a publicly known secret. Attackers can forge admin tokens.
- **Issue 2 (not fixed here)**: `token_expiry_hours = 24` is generous — rotation would be stricter, but that is a separate task.
- **Issue 3 (not fixed here)**: `hash_password` uses PBKDF2 with 100k iterations — modern guidance prefers 600k+ or Argon2, but that is a separate task with migration implications.

The OAuth-related code (`find_or_create_oauth_user`, lines 270-340) is NOT part of this file's SUB-1 change — it lives in the service but the Google tokeninfo audience check is in `auth_routes.py` (the HTTP boundary). `auth_service.py` is only touched for the `__init__` hardening.

---

## Planned Changes

**Will add/modify:**

Replace the 3-line secret-key resolution in `__init__` with a fail-fast block:

```python
# Resolve JWT signing secret with environment-aware safety rails.
env_secret = os.environ.get('JWT_SECRET_KEY')
if secret_key:
    self.secret_key = secret_key
elif env_secret:
    self.secret_key = env_secret
elif os.environ.get('FLASK_ENV') == 'development':
    # Dev convenience: generate a random per-process key so local runs
    # work without configuration. Tokens do not survive restarts.
    self.secret_key = os.urandom(32).hex()
    logger.warning(
        "JWT_SECRET_KEY not set — generated ephemeral dev key. "
        "Sessions will not persist across restarts."
    )
else:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable is required in non-development "
        "environments. Set JWT_SECRET_KEY to a strong random value before "
        "starting the API."
    )
self.algorithm = 'HS256'
self.token_expiry_hours = 24
```

- Removes the string literal `'dev-secret-key-change-in-production'` entirely from the file.
- Removes the subsequent `if self.secret_key == 'dev-secret-key-change-in-production': logger.warning(...)` block.

**Will NOT change:**
- `hash_password`, `verify_password` — unchanged (PBKDF2 100k iterations concern is out of scope per spec).
- `generate_token`, `verify_token` — unchanged; still use `self.secret_key` and `self.algorithm`.
- `register_user`, `login`, `get_user_from_token`, `change_password` — unchanged.
- `find_or_create_oauth_user` — unchanged; the OAuth audience check lives in `auth_routes.py`, not here.
- `token_expiry_hours`, `algorithm` — unchanged.
- No new public methods on `AuthService`.

**Backward compatibility:**
- Prod env already has `JWT_SECRET_KEY` set (pre-flight check #1) → init succeeds, behavior unchanged from user perspective.
- Local dev without the env var: now logs a warning and generates a random key instead of using the hardcoded default. Tokens created in previous local dev sessions (signed with the old hardcoded default) become invalid — user must re-login locally. Acceptable dev friction.

**Test coverage wired:**
- `test_auth_service_no_hardcoded_fallback_in_source` — will pass after this edit
- `test_missing_secret_in_production_raises` — will pass after this edit
- `test_missing_secret_in_dev_generates_random_key` — will pass after this edit
