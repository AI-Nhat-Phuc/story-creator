"""Authentication middleware and decorators for protecting routes."""

from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

# Global auth service instance (injected from api_backend.py)
_auth_service = None


def init_auth_middleware(auth_service):
    """Initialize auth middleware with auth service instance."""
    global _auth_service
    _auth_service = auth_service


def token_required(f):
    """
    Decorator to protect routes with JWT authentication.

    Usage:
        @app.route('/api/protected')
        @token_required
        def protected_route():
            # Access current user via g.current_user
            pass

    The decorator:
    1. Extracts Authorization header
    2. Validates JWT token
    3. Loads user from token
    4. Stores user in Flask g object
    5. Returns 401 if invalid/missing token
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import g

        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Missing or invalid Authorization header'
            }), 401

        token = auth_header[7:]  # Remove 'Bearer ' prefix

        # Verify token and get user
        if not _auth_service:
            logger.error("Auth service not initialized")
            return jsonify({
                'success': False,
                'message': 'Server configuration error'
            }), 500

        try:
            user = _auth_service.get_user_from_token(token)

            if not user:
                # Token might be valid but user not in DB (Vercel ephemeral /tmp/)
                # Fall back to token payload for basic identity
                payload = _auth_service.verify_token(token)
                if payload and payload.get('user_id'):
                    from core.models import User
                    user = User(
                        username=payload.get('username', 'unknown'),
                        email=payload.get('email', ''),
                        password_hash='',
                        role=payload.get('role', 'user'),
                        user_id=payload.get('user_id')
                    )
                    logger.info(f"Using token payload fallback for user: {payload.get('username')}")
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Token không hợp lệ hoặc đã hết hạn'
                    }), 401
        except Exception as e:
            logger.error(f"Error during token verification: {e}")
            return jsonify({
                'success': False,
                'message': 'Token không hợp lệ hoặc đã hết hạn'
            }), 401

        # Store user in Flask g for access in route
        g.current_user = user

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorator to protect routes requiring admin role.

    Must be used after @token_required decorator.

    Usage:
        @app.route('/api/admin/users')
        @token_required
        @admin_required
        def admin_only_route():
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import g

        # Check if current_user exists (should be set by token_required)
        if not hasattr(g, 'current_user'):
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401

        # Check if user has admin role
        if g.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Yêu cầu quyền admin'
            }), 403

        return f(*args, **kwargs)

    return decorated


def optional_auth(f):
    """
    Decorator that allows both authenticated and unauthenticated access.

    If token is present and valid, sets g.current_user.
    If token is missing or invalid, continues without authentication.
    On Vercel (ephemeral DB), falls back to token payload for user identity.

    Usage:
        @app.route('/api/public-or-private')
        @optional_auth
        def flexible_route():
            if hasattr(g, 'current_user'):
                # User is authenticated
                pass
            else:
                # User is anonymous
                pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import g

        # Try to extract token
        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Bearer ') and _auth_service:
            token = auth_header[7:]
            try:
                user = _auth_service.get_user_from_token(token)

                if user:
                    g.current_user = user
                else:
                    # Token is valid but user not in DB (e.g. Vercel ephemeral /tmp/)
                    # Fall back to token payload for basic identity
                    payload = _auth_service.verify_token(token)
                    if payload and payload.get('user_id'):
                        from core.models import User
                        g.current_user = User(
                            username=payload.get('username', 'unknown'),
                            email=payload.get('email', ''),
                            password_hash='',
                            role=payload.get('role', 'user'),
                            user_id=payload.get('user_id')
                        )
                        logger.info(f"Using token payload fallback for user: {payload.get('username')}")
            except Exception as e:
                logger.warning(f"Error during optional auth: {e}")
                # Continue without authentication

        return f(*args, **kwargs)

    return decorated


def permission_required(*permissions):
    """
    Decorator to protect routes requiring specific permissions.

    Must be used after @token_required decorator.

    Usage:
        from core.permissions import Permission

        @app.route('/api/admin/content')
        @token_required
        @permission_required(Permission.MANAGE_ALL_CONTENT)
        def manage_content():
            pass

        @app.route('/api/gpt/unlimited')
        @token_required
        @permission_required(Permission.USE_GPT, Permission.USE_GPT_UNLIMITED)
        def unlimited_gpt():
            pass

    Args:
        *permissions: Permission enum values to check (user needs ALL permissions)
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask import g
            from core.permissions import has_permission

            # Check if current_user exists (should be set by token_required)
            if not hasattr(g, 'current_user'):
                return jsonify({
                    'success': False,
                    'message': 'Unauthorized'
                }), 401

            user_role = g.current_user.role

            # Check if user has ALL required permissions
            missing_permissions = []
            for perm in permissions:
                if not has_permission(user_role, perm):
                    missing_permissions.append(perm.value)

            if missing_permissions:
                return jsonify({
                    'success': False,
                    'message': 'Không đủ quyền truy cập',
                    'required_permissions': missing_permissions
                }), 403

            return f(*args, **kwargs)

        return decorated
    return decorator


def role_required(*roles):
    """
    Decorator to protect routes requiring specific roles.

    Must be used after @token_required decorator.

    Usage:
        from core.permissions import Role

        @app.route('/api/moderator/reports')
        @token_required
        @role_required(Role.ADMIN, Role.MODERATOR)
        def view_reports():
            pass

    Args:
        *roles: Role enum values to check (user needs ONE of the roles)
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask import g
            from core.permissions import Role

            # Check if current_user exists
            if not hasattr(g, 'current_user'):
                return jsonify({
                    'success': False,
                    'message': 'Unauthorized'
                }), 401

            user_role = g.current_user.role

            # Check if user has ONE of the required roles
            allowed_roles = [r.value for r in roles]
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': f'Yêu cầu vai trò: {", ".join(allowed_roles)}',
                    'current_role': user_role
                }), 403

            return f(*args, **kwargs)

        return decorated
    return decorator


def moderator_required(f):
    """
    Decorator to protect routes requiring moderator or admin role.

    Shorthand for @role_required(Role.ADMIN, Role.MODERATOR).

    Usage:
        @app.route('/api/moderate/content')
        @token_required
        @moderator_required
        def moderate():
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import g

        if not hasattr(g, 'current_user'):
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401

        user_role = g.current_user.role
        if user_role not in ['admin', 'moderator']:
            return jsonify({
                'success': False,
                'message': 'Yêu cầu quyền moderator hoặc admin'
            }), 403

        return f(*args, **kwargs)

    return decorated
