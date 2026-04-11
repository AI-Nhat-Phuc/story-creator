# Flow Summary — backend security hardening

> **Status**: PENDING
> **File**: `api/interfaces/api_backend.py`
> **Date**: 2026-04-11
> **SUB**: 2 (admin/test seed gating) + 4 (security headers + VERCEL_URL regex)

---

## Current Flow

### `APIBackend.__init__(mongodb_uri, mongo_db_name)`

Current sequence:

1. Create Flask app, set `secret_key = os.urandom(24)`.
2. Build `allowed_origins = ['http://localhost:3000', 'http://127.0.0.1:3000']`.
3. Read `vercel_url = os.environ.get("VERCEL_URL")`; if set, append `f"https://{vercel_url}"` to `allowed_origins` **without any validation**.
4. `CORS(self.app, resources={...})`.
5. Register error handlers, logging middleware, rate limiter.
6. Init storage (`MongoStorage`), generators, auth service, middleware.
7. Register blueprints.
8. Register `@before_request _lazy_init()` hook that calls `backend._seed_once()` on any non-health/docs request.

### `_ensure_default_admin()` (lines 180-221)

1. List all users.
2. If no admin: create `User(username='admin', email='admin@storycreator.com', password_hash=hash('Admin@123'), role='admin')`, save.
3. `print("🔐 Tạo tài khoản admin mặc định: ... Password: Admin@123")` — prints the password to stdout.
4. Else: print admin count.

### `_seed_test_account()` (lines 223-257)

1. Read `test_password = "Test@123"`.
2. If testuser exists: verify stored hash matches; reset if not; return.
3. Else create new User, save.
4. `print("🧪 Test account seeded (nonprod only): Password: Test@123")`.

### `_seed_once()` (lines 278-286)

1. If `_admin_seeded` module flag True → return.
2. Set flag True.
3. Call `_ensure_default_admin()`.
4. If `VERCEL_ENV != 'production'`: call `_seed_test_account()`.

### Observed Issues

- **Issue A (SUB-2 Rule 3)**: `_ensure_default_admin` creates `Admin@123` unconditionally whenever no admin exists. A forgotten config on a new env produces a known-credential admin account. Spec requires `INITIAL_ADMIN_PASSWORD` env var and no seeding when it's absent.
- **Issue B (SUB-2 Rule 4)**: `_seed_test_account` auto-runs whenever `VERCEL_ENV != 'production'`, which is true for every local dev, every test harness, and every preview deploy. Spec requires an additional opt-in flag `SEED_TEST_USER == '1'`.
- **Issue C (SUB-2 Rule 3 audit trail)**: Both seeds `print()` the password to stdout; any log aggregator ingests it. Spec requires seeding without password output.
- **Issue D (SUB-4 security headers)**: No `@after_request` hook sets `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, or `Strict-Transport-Security`.
- **Issue E (SUB-4 CORS)**: `VERCEL_URL` is accepted as-is — if an attacker controls that env var (or a typo / compromise sets it), the resulting origin lands in the CORS allowlist unchecked. Spec requires regex `^[a-zA-Z0-9.-]+\.vercel\.app$`.

---

## Planned Changes

### Change 1 — `VERCEL_URL` regex validation (SUB-4)

Add `import re` to the imports. Replace the vercel_url block:

```python
vercel_url = os.environ.get("VERCEL_URL")
if vercel_url:
    if re.match(r'^[a-zA-Z0-9.-]+\.vercel\.app$', vercel_url):
        allowed_origins.append(f"https://{vercel_url}")
    else:
        import logging
        logging.getLogger(__name__).warning(
            "VERCEL_URL %r does not match expected pattern — skipping CORS entry",
            vercel_url,
        )
```

(Use a module-level `logger = logging.getLogger(__name__)` once at the top of the file and reference it here.)

### Change 2 — Security headers `@after_request` hook (SUB-4)

After `self._register_blueprints()` and before the existing `@self.app.before_request` hook, add:

```python
@self.app.after_request
def _add_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    # HSTS only on HTTPS (direct or via proxy)
    is_https = request.is_secure or request.headers.get('X-Forwarded-Proto', '').lower() == 'https'
    if is_https:
        response.headers.setdefault(
            'Strict-Transport-Security',
            'max-age=31536000; includeSubDomains',
        )
    return response
```

Uses `setdefault` so we never clobber a response that already set the header.

### Change 3 — `_ensure_default_admin` env-gated, silent seeding (SUB-2)

```python
def _ensure_default_admin(self):
    """Ensure a default admin exists, gated behind INITIAL_ADMIN_PASSWORD.

    Behavior:
    - If an admin already exists: no-op (logs count).
    - If no admin AND `INITIAL_ADMIN_PASSWORD` is unset: log a warning
      and do nothing. Operators must set the env var to seed an admin.
    - If no admin AND `INITIAL_ADMIN_PASSWORD` is set: seed an admin
      with that password, log seeding (without the password), done.
    """
    all_users = self.storage.list_users()
    admin_users = [u for u in all_users if u.get('role') == 'admin']

    if admin_users:
        logger.info("Found %d admin account(s); skipping seed", len(admin_users))
        return

    initial_pwd = os.environ.get('INITIAL_ADMIN_PASSWORD')
    if not initial_pwd:
        logger.warning(
            "No admin account exists and INITIAL_ADMIN_PASSWORD is unset — "
            "skipping admin seed. Set INITIAL_ADMIN_PASSWORD to auto-create "
            "the initial admin."
        )
        return

    from core.models import User
    password_hash = self.auth_service.hash_password(initial_pwd)
    admin_user = User(
        username="admin",
        email="admin@storycreator.com",
        password_hash=password_hash,
        role="admin",
    )
    self.storage.save_user(admin_user.to_dict())
    logger.info("Admin account seeded from INITIAL_ADMIN_PASSWORD env")
```

Removes all `print(...)` statements and the hardcoded `"Admin@123"` literal.

### Change 4 — `_seed_test_account` opt-in + silent (SUB-2)

The function body stays mostly the same but all `print(...)` calls are replaced with `logger.info(...)` without password output:

```python
def _seed_test_account(self):
    """Seed a hard-coded test account for local / nonprod development.

    Gated caller in _seed_once checks VERCEL_ENV != 'production' AND
    SEED_TEST_USER == '1'. Password is logged only as '<redacted>'.
    """
    from core.models import User
    test_password = "Test@123"
    existing = self.storage.find_user_by_username("testuser")

    if existing:
        if not self.auth_service.verify_password(test_password, existing.get('password_hash', '')):
            existing['password_hash'] = self.auth_service.hash_password(test_password)
            self.storage.save_user(existing)
            logger.info("Test account password reset (nonprod)")
        return

    password_hash = self.auth_service.hash_password(test_password)
    test_user = User(
        username="testuser",
        email="test@storycreator.local",
        password_hash=password_hash,
        role="user",
    )
    self.storage.save_user(test_user.to_dict())
    logger.info("Test account seeded (nonprod)")
```

### Change 5 — `_seed_once` opt-in gating (SUB-2)

```python
def _seed_once(self):
    global _admin_seeded
    if _admin_seeded:
        return
    _admin_seeded = True
    self._ensure_default_admin()
    if (
        os.environ.get("VERCEL_ENV") != "production"
        and os.environ.get("SEED_TEST_USER") == "1"
    ):
        self._seed_test_account()
```

### NOT changing

- Swagger config, logging middleware, error handlers, rate limiter init.
- `_ensure_gpt`, `_ensure_swagger`, `_register_blueprints`, `_kill_existing_server`, `run`, `_signal_handler`, `_flush_data`.
- The `@before_request _lazy_init` hook structure (still calls `_seed_once`).
- The before_request Swagger / health-check skips.

---

## Imports to add at module top

```python
import logging
import re

logger = logging.getLogger(__name__)
```

Will be added after the existing `import time` (line 28).

---

## Backward Compatibility

- **Prod** already has `INITIAL_ADMIN_PASSWORD` set (pre-flight check #3) and an existing admin account. The new `_ensure_default_admin` sees `admin_users` non-empty and returns with just an info log — unchanged observable behavior.
- **Prod** has a valid `VERCEL_URL` ending in `.vercel.app` → passes the regex unchanged.
- **Local dev** without `INITIAL_ADMIN_PASSWORD` → no admin auto-seeded. This is a migration-visible change (documented in commit message). Users can either set the env var or create an admin manually.
- **Local dev** without `SEED_TEST_USER=1` → testuser no longer auto-created on boot. Devs who rely on it set the env var.
- **Security headers** land on every response via `setdefault`, so they never clobber headers set by a more specific route. HSTS honors the existing Vercel/forwarded-https setup.

---

## Test coverage wired

- `TestAdminSeedGating.test_no_admin_seeded_without_env_var` → will pass
- `TestAdminSeedGating.test_admin_seeded_when_env_var_set` → will pass
- `TestAdminSeedGating.test_seed_does_not_print_password` → will pass
- `TestTestAccountSeedGating.test_test_account_not_seeded_by_default` → will pass
- `TestTestAccountSeedGating.test_test_account_seeded_with_flag` → will stay green
- `TestSecurityHeaders.test_x_content_type_options_nosniff` → will pass
- `TestSecurityHeaders.test_x_frame_options_sameorigin` → will pass
- `TestSecurityHeaders.test_referrer_policy` → will pass
- `TestSecurityHeaders.test_hsts_only_on_https` → will stay green
- `TestSecurityHeaders.test_hsts_set_when_forwarded_https` → will pass
- `TestCorsVercelUrlValidation.test_malformed_vercel_url_not_added_to_cors` → will pass
- `TestCorsVercelUrlValidation.test_valid_vercel_url_accepted` → will stay green

Expected count flip: 14 → ~4 failing after this file is committed.
