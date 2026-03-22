"""Rate limiting middleware using Flask-Limiter."""

import logging

logger = logging.getLogger(__name__)

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    _limiter_available = True
except ImportError:
    _limiter_available = False
    logger.warning("flask-limiter not installed — rate limiting disabled. Run: pip install flask-limiter")


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
