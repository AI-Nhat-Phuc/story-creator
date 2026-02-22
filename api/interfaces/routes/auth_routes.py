"""Authentication routes for user registration, login, and token verification."""

from flask import Blueprint, request, jsonify, redirect
from authlib.integrations.flask_client import OAuth
import logging
import os

logger = logging.getLogger(__name__)

# Blueprint will be initialized in __init__.py with dependencies
auth_bp = Blueprint('auth', __name__)

# Dependencies injected from api_backend.py
storage = None
auth_service = None


def init_auth_routes(storage_instance, auth_service_instance):
    """Initialize auth routes with dependencies."""
    global storage, auth_service
    storage = storage_instance
    auth_service = auth_service_instance


@auth_bp.route('/api/auth/register', methods=['POST'])
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
              description: Password (min 6 characters)
            role:
              type: string
              description: User role (optional, defaults to 'user')
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            user:
              type: object
            token:
              type: string
      400:
        description: Invalid input or user already exists
    """
    data = request.get_json()

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'user')

    # Register user
    success, message, user = auth_service.register_user(
        username=username,
        email=email,
        password=password,
        role=role
    )

    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 400

    # Generate token for immediate login
    token = auth_service.generate_token(user)

    return jsonify({
        'success': True,
        'message': message,
        'user': user.to_safe_dict(),
        'token': token
    }), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
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
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            user:
              type: object
            token:
              type: string
      401:
        description: Invalid credentials
    """
    data = request.get_json()

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({
            'success': False,
            'message': 'Username và password là bắt buộc'
        }), 400

    # Attempt login
    success, message, token, user = auth_service.login(username, password)

    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 401

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
        schema:
          type: object
          properties:
            success:
              type: boolean
            user:
              type: object
      401:
        description: Invalid or expired token
    """
    # Extract token from Authorization header
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return jsonify({
            'success': False,
            'message': 'Missing or invalid Authorization header'
        }), 401

    token = auth_header[7:]  # Remove 'Bearer ' prefix

    # Verify token and get user
    user = auth_service.get_user_from_token(token)

    if not user:
        return jsonify({
            'success': False,
            'message': 'Token không hợp lệ hoặc đã hết hạn'
        }), 401

    return jsonify({
        'success': True,
        'user': user.to_safe_dict()
    })


@auth_bp.route('/api/auth/change-password', methods=['POST'])
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
            - old_password
            - new_password
          properties:
            old_password:
              type: string
            new_password:
              type: string
    responses:
      200:
        description: Password changed successfully
      401:
        description: Unauthorized or invalid old password
    """
    # Extract token
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 401

    token = auth_header[7:]
    user = auth_service.get_user_from_token(token)

    if not user:
        return jsonify({
            'success': False,
            'message': 'Token không hợp lệ'
        }), 401

    # Get passwords
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    # Change password
    success, message = auth_service.change_password(
        user.user_id,
        old_password,
        new_password
    )

    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 400

    return jsonify({
        'success': True,
        'message': message
    })


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
    # Extract token
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 401

    token = auth_header[7:]
    user = auth_service.get_user_from_token(token)

    if not user:
        return jsonify({
            'success': False,
            'message': 'Token không hợp lệ'
        }), 401

    return jsonify({
        'success': True,
        'user': user.to_safe_dict()
    })


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
    import requests

    data = request.get_json()
    google_token = data.get('token', '')

    if not google_token:
        return jsonify({
            'success': False,
            'message': 'Missing Google token'
        }), 400

    # Verify Google token
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {google_token}'},
            timeout=10
        )

        if response.status_code != 200:
            return jsonify({
                'success': False,
                'message': 'Invalid Google token'
            }), 400

        user_info = response.json()

        # Find or create user
        success, message, user = auth_service.find_or_create_oauth_user(
            provider='google',
            provider_user_id=user_info.get('sub'),
            email=user_info.get('email', ''),
            name=user_info.get('name', ''),
            avatar_url=user_info.get('picture', '')
        )

        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 400

        # Generate JWT token
        token = auth_service.generate_token(user)

        return jsonify({
            'success': True,
            'message': message,
            'user': user.to_safe_dict(),
            'token': token
        })

    except Exception as e:
        logger.error(f"Error verifying Google token: {e}")
        return jsonify({
            'success': False,
            'message': 'Lỗi xác thực Google'
        }), 500


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
    import requests

    data = request.get_json()
    fb_token = data.get('token', '')

    if not fb_token:
        return jsonify({
            'success': False,
            'message': 'Missing Facebook token'
        }), 400

    # Verify Facebook token
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
            return jsonify({
                'success': False,
                'message': 'Invalid Facebook token'
            }), 400

        user_info = response.json()

        # Find or create user
        success, message, user = auth_service.find_or_create_oauth_user(
            provider='facebook',
            provider_user_id=user_info.get('id'),
            email=user_info.get('email', ''),
            name=user_info.get('name', ''),
            avatar_url=user_info.get('picture', {}).get('data', {}).get('url', '')
        )

        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 400

        # Generate JWT token
        token = auth_service.generate_token(user)

        return jsonify({
            'success': True,
            'message': message,
            'user': user.to_safe_dict(),
            'token': token
        })

    except Exception as e:
        logger.error(f"Error verifying Facebook token: {e}")
        return jsonify({
            'success': False,
            'message': 'Lỗi xác thực Facebook'
        }), 500


