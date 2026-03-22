"""Global error handlers for Flask application."""

from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register global error handlers for the Flask application.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Catch-all handler for unhandled exceptions."""
        # Import here to avoid circular imports
        from core.exceptions import APIException

        # If it's our custom exception, let the specific handler deal with it
        if isinstance(e, APIException):
            return handle_api_exception(e)

        # Log unexpected errors
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

        # Return generic 500 error
        return jsonify({
            'success': False,
            'error': {
                'code': 'internal_error',
                'message': 'An unexpected error occurred. Please try again later.'
            }
        }), 500

    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 Not Found errors."""
        return jsonify({
            'success': False,
            'error': {
                'code': 'not_found',
                'message': 'The requested endpoint does not exist.'
            }
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """Handle 405 Method Not Allowed errors."""
        return jsonify({
            'success': False,
            'error': {
                'code': 'method_not_allowed',
                'message': 'The HTTP method is not allowed for this endpoint.'
            }
        }), 405

    @app.errorhandler(500)
    def handle_internal_error(e):
        """Handle 500 Internal Server Error."""
        logger.error(f"Internal server error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'internal_error',
                'message': 'An internal server error occurred. Please try again later.'
            }
        }), 500

    # Register handler for our custom API exceptions
    from core.exceptions import APIException

    @app.errorhandler(APIException)
    def handle_api_exception(e):
        """Handle custom API exceptions."""
        response = {
            'success': False,
            'error': {
                'code': e.error_code,
                'message': e.message
            }
        }

        # Include details if present
        if e.details:
            response['error']['details'] = e.details

        # Log errors (but not client errors like validation)
        if e.status_code >= 500:
            logger.error(f"API Exception: {e.message}", exc_info=True)
        elif e.status_code >= 400:
            logger.warning(f"Client error: {e.message}")

        return jsonify(response), e.status_code

    logger.info("✅ Global error handlers registered")
