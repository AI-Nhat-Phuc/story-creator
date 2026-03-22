"""Request/response logging middleware for Flask."""

import logging
import time
from flask import g, request

logger = logging.getLogger('api.requests')


def register_logging_middleware(app):
    """Register before/after request hooks that log each API call.

    Logs:
    - Before: method, path, remote addr (DEBUG)
    - After:  method, path, status code, duration ms (INFO for 2xx/3xx, WARNING for 4xx, ERROR for 5xx)

    Args:
        app: Flask application instance
    """

    @app.before_request
    def _before_request():
        g._request_start = time.monotonic()

    @app.after_request
    def _after_request(response):
        duration_ms = round((time.monotonic() - g._request_start) * 1000, 1)
        status = response.status_code
        msg = f"{request.method} {request.path} → {status} ({duration_ms}ms)"

        if status >= 500:
            logger.error(msg)
        elif status >= 400:
            logger.warning(msg)
        else:
            logger.info(msg)

        return response
