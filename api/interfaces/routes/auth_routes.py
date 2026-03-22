"""Authentication routes for user registration, login, and token verification."""

from flask import Blueprint, request, jsonify
import requests
import logging
from core.exceptions import (
    ValidationError as APIValidationError,
    AuthenticationError,
    ExternalServiceError,
    ConflictError
)
from utils.validation import validate_request
from schemas.auth_schemas import RegisterSchema, LoginSchema, ChangePasswordSchema

logger = logging.getLogger(__name__)


def create_auth_bp(storage, auth_service, limiter=None):
    """Create authentication blueprint with injected dependencies.

    Args:
        storage: Storage instance for user data persistence
        auth_service: AuthService instance for authentication operations
        limiter: Optional Flask-Limiter instance for rate limiting

    Returns:
        Blueprint: Configured Flask blueprint for auth routes
    """
    auth_bp = Blueprint('auth', __name__)

    # Tighter limit on auth endpoints (brute-force protection)
    _auth_limit = limiter.limit("5 per minute") if limiter else (lambda f: f)

    @auth_bp.route('/api/auth/register', methods=['POST'])
    @_auth_limit
    @validate_request(RegisterSchema)
    def register():
        """Register a new user.
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - username
                - email
                - password
              properties:
                username:
                  type: string
                  description: Unique username (min 3 characters)
                email:
                  type: string
                  description: User email address
                password:
                  type: string
                  description: Password (min 8 characters)
                role:
                  type: string
                  description: User role (optional, defaults to 'user')
        responses:
          201:
            description: User registered successfully
          400:
            description: Invalid input or user already exists
        """
        data = request.validated_data

        success, message, user = auth_service.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'user')
        )

        if not success:
            raise ConflictError(message)

        token = auth_service.generate_token(user)

        return jsonify({
            'success': True,
            'message': message,
            'user': user.to_safe_dict(),
            'token': token
        }), 201

    @auth_bp.route('/api/auth/login', methods=['POST'])
    @_auth_limit
    @validate_request(LoginSchema)
    def login():
        """Login with username and password.
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - username
                - password
              properties:
                username:
                  type: string
                password:
                  type: string
        responses:
          200:
            description: Login successful
          401:
            description: Invalid credentials
        """
        data = request.validated_data

        success, message, token, user = auth_service.login(
            data['username'], data['password']
        )

        if not success:
            raise AuthenticationError(message)

        return jsonify({
            'success': True,
            'message': message,
            'user': user.to_safe_dict(),
            'token': token
        })

    @auth_bp.route('/api/auth/verify', methods=['GET'])
    def verify_token():
        """Verify a JWT token and return user info.
        ---
        tags:
          - Authentication
        parameters:
          - in: header
            name: Authorization
            type: string
            required: true
            description: Bearer token
        responses:
          200:
            description: Token is valid
          401:
            description: Invalid or expired token
        """
        user = _get_user_from_auth_header(request, auth_service)
        return jsonify({'success': True, 'user': user.to_safe_dict()})

    @auth_bp.route('/api/auth/change-password', methods=['POST'])
    @validate_request(ChangePasswordSchema)
    def change_password():
        """Change user password (requires valid token).
        ---
        tags:
          - Authentication
        parameters:
          - in: header
            name: Authorization
            type: string
            required: true
            description: Bearer token
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - current_password
                - new_password
              properties:
                current_password:
                  type: string
                new_password:
                  type: string
        responses:
          200:
            description: Password changed successfully
          401:
            description: Unauthorized or invalid old password
        """
        user = _get_user_from_auth_header(request, auth_service)

        data = request.validated_data
        success, message = auth_service.change_password(
            user.user_id,
            data['current_password'],
            data['new_password']
        )

        if not success:
            raise APIValidationError(message)

        return jsonify({'success': True, 'message': message})

    @auth_bp.route('/api/auth/me', methods=['GET'])
    def get_current_user():
        """Get current authenticated user info.
        ---
        tags:
          - Authentication
        parameters:
          - in: header
            name: Authorization
            type: string
            required: true
            description: Bearer token
        responses:
          200:
            description: Current user info
          401:
            description: Unauthorized
        """
        user = _get_user_from_auth_header(request, auth_service)
        return jsonify({'success': True, 'user': user.to_safe_dict()})

    # ==================== OAuth Routes ====================

    @auth_bp.route('/api/auth/oauth/google', methods=['POST'])
    def oauth_google():
        """Login with Google OAuth token.
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - token
              properties:
                token:
                  type: string
                  description: Google ID token from frontend
        responses:
          200:
            description: Login successful
          400:
            description: Invalid token
        """
        data = request.get_json()
        google_token = data.get('token', '') if data else ''

        if not google_token:
            raise APIValidationError('Missing Google token')

        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {google_token}'},
                timeout=10
            )

            if response.status_code != 200:
                raise APIValidationError('Invalid Google token')

            user_info = response.json()

            success, message, user = auth_service.find_or_create_oauth_user(
                provider='google',
                provider_user_id=user_info.get('sub'),
                email=user_info.get('email', ''),
                name=user_info.get('name', ''),
                avatar_url=user_info.get('picture', '')
            )

            if not success:
                raise APIValidationError(message)

            token = auth_service.generate_token(user)

            return jsonify({
                'success': True,
                'message': message,
                'user': user.to_safe_dict(),
                'token': token
            })

        except APIValidationError:
            raise
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            raise ExternalServiceError('Google', 'Google authentication error', e)

    @auth_bp.route('/api/auth/oauth/facebook', methods=['POST'])
    def oauth_facebook():
        """Login with Facebook OAuth token.
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - token
              properties:
                token:
                  type: string
                  description: Facebook access token from frontend
        responses:
          200:
            description: Login successful
          400:
            description: Invalid token
        """
        data = request.get_json()
        fb_token = data.get('token', '') if data else ''

        if not fb_token:
            raise APIValidationError('Missing Facebook token')

        try:
            response = requests.get(
                'https://graph.facebook.com/me',
                params={
                    'fields': 'id,name,email,picture',
                    'access_token': fb_token
                },
                timeout=10
            )

            if response.status_code != 200:
                raise APIValidationError('Invalid Facebook token')

            user_info = response.json()

            success, message, user = auth_service.find_or_create_oauth_user(
                provider='facebook',
                provider_user_id=user_info.get('id'),
                email=user_info.get('email', ''),
                name=user_info.get('name', ''),
                avatar_url=user_info.get('picture', {}).get('data', {}).get('url', '')
            )

            if not success:
                raise APIValidationError(message)

            token = auth_service.generate_token(user)

            return jsonify({
                'success': True,
                'message': message,
                'user': user.to_safe_dict(),
                'token': token
            })

        except APIValidationError:
            raise
        except Exception as e:
            logger.error(f"Error verifying Facebook token: {e}")
            raise ExternalServiceError('Facebook', 'Facebook authentication error', e)

    return auth_bp


# Helper function

def _get_user_from_auth_header(request, auth_service):
    """Extract and validate user from Authorization header.

    Raises AuthenticationError if token is missing or invalid.
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise AuthenticationError('Missing or invalid Authorization header')

    token = auth_header[7:]
    user = auth_service.get_user_from_token(token)

    if not user:
        raise AuthenticationError('Token is invalid or expired')

    return user
