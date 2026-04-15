"""Rate limiting middleware using Flask-Limiter."""

import logging
import os

logger = logging.getLogger(__name__)

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    _limiter_available = True
except ImportError:
    _limiter_available = False
    logger.warning("flask-limiter not installed — rate limiting disabled. Run: pip install flask-limiter")


def _is_disabled_via_env():
    """Return True if RATELIMIT_ENABLED env var is set to a falsy value.

    Used to disable rate limiting on Vercel preview deploys during E2E runs —
    GitHub Actions workers share a single egress IP which would otherwise trip
    the per-IP auth limit (10/min) within seconds. Set RATELIMIT_ENABLED=false
    on the Preview environment in the Vercel dashboard.
    """
    raw = os.getenv('RATELIMIT_ENABLED')
    if raw is None:
        return False
    return raw.strip().lower() in ('false', '0', 'no', 'off')


def create_limiter(app):
    """Create and configure Flask-Limiter, or return a no-op stub if unavailable.

    Limits applied:
    - /api/auth/*    : 5 requests / minute / IP  (brute-force protection)
    - /api/gpt/*     : 10 requests / minute / IP (cost control)
    - /api/*         : 100 requests / minute / IP (general DoS guard)

    Args:
        app: Flask application instance

    Returns:
        Limiter instance (or stub with .limit() that is a no-op decorator)
    """
    if not _limiter_available:
        return _NoOpLimiter()

    if _is_disabled_via_env():
        logger.info("Rate limiting DISABLED via RATELIMIT_ENABLED env var")
        return _NoOpLimiter()

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["100 per minute"],
        storage_uri="memory://",
    )

    # Attach the limiter to the app so blueprints can import it
    app.extensions['limiter'] = limiter

    logger.info("Rate limiting enabled (100/min default, 10/min GPT, 5/min auth)")
    return limiter


def get_limiter(app):
    """Retrieve the limiter attached to the app (for use in blueprints).

    Returns None if rate limiting is disabled.
    """
    return app.extensions.get('limiter')


class _NoOpLimiter:
    """Stub limiter when flask-limiter is not installed."""

    def limit(self, *args, **kwargs):
        def decorator(f):
            return f
        return decorator

    def exempt(self, f):
        return f
