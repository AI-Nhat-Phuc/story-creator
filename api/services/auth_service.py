"""Authentication and authorization service using JWT tokens."""

import hashlib
import hmac
import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from core.models import User

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication and authorization with JWT tokens."""

    def __init__(self, storage, secret_key: Optional[str] = None):
        """
        Initialize AuthService.

        Args:
            storage: NoSQLStorage instance
            secret_key: Secret key for JWT signing (defaults to env var or random)
        """
        self.storage = storage
        self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.token_expiry_hours = 24  # Tokens expire after 24 hours

        if self.secret_key == 'dev-secret-key-change-in-production':
            logger.warning("Using default JWT secret key! Set JWT_SECRET_KEY in production.")

    def hash_password(self, password: str) -> str:
        """
        Hash a password using PBKDF2-HMAC-SHA256.

        Args:
            password: Plain text password

        Returns:
            Hashed password in format: salt$hash
        """
        # Generate random salt (16 bytes)
        salt = os.urandom(16).hex()

        # Hash password with salt using PBKDF2
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k iterations
        ).hex()

        return f"{salt}${pwd_hash}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            password: Plain text password to verify
            password_hash: Stored password hash (salt$hash format)

        Returns:
            True if password matches, False otherwise
        """
        try:
            salt, stored_hash = password_hash.split('$')

            # Hash the provided password with the same salt
            pwd_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            ).hex()

            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(pwd_hash, stored_hash)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    def generate_token(self, user: User, expires_in_hours: Optional[int] = None) -> str:
        """
        Generate a JWT token for a user.

        Args:
            user: User object
            expires_in_hours: Token expiry time (defaults to 24 hours)

        Returns:
            JWT token string
        """
        expires_in = expires_in_hours or self.token_expiry_hours
        expiry_time = datetime.utcnow() + timedelta(hours=expires_in)

        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'exp': expiry_time,
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload if valid, None if invalid/expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = 'user'
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user.

        Args:
            username: Unique username
            email: User email
            password: Plain text password (will be hashed)
            role: User role (default: 'user')

        Returns:
            Tuple of (success, message, user_object)
        """
        # Validate inputs
        if not username or len(username) < 3:
            return False, "Username phải có ít nhất 3 ký tự", None

        if not email or '@' not in email:
            return False, "Email không hợp lệ", None

        if not password or len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự", None

        # Check if username already exists
        existing_user = self.storage.find_user_by_username(username)
        if existing_user:
            return False, "Username đã tồn tại", None

        # Check if email already exists
        existing_email = self.storage.find_user_by_email(email)
        if existing_email:
            return False, "Email đã được sử dụng", None

        # Create user
        password_hash = self.hash_password(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )

        # Save to storage
        self.storage.save_user(user.to_dict())
        logger.info(f"Registered new user: {username}")

        return True, "Đăng ký thành công", user

    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[str], Optional[User]]:
        """
        Authenticate a user and generate a token.

        Args:
            username: Username
            password: Plain text password

        Returns:
            Tuple of (success, message, token, user_object)
        """
        # Find user
        user_data = self.storage.find_user_by_username(username)
        if not user_data:
            return False, "Tên đăng nhập hoặc mật khẩu không đúng", None, None

        # Verify password
        if not self.verify_password(password, user_data.get('password_hash', '')):
            return False, "Tên đăng nhập hoặc mật khẩu không đúng", None, None

        # Generate token
        user = User.from_dict(user_data)
        token = self.generate_token(user)

        logger.info(f"User logged in: {username}")
        return True, "Đăng nhập thành công", token, user

    def get_user_from_token(self, token: str) -> Optional[User]:
        """
        Get user object from a JWT token.

        Args:
            token: JWT token string

        Returns:
            User object if token is valid, None otherwise
        """
        payload = self.verify_token(token)
        if not payload:
            return None

        # Load fresh user data from storage
        user_data = self.storage.load_user(payload.get('user_id'))
        if not user_data:
            return None

        return User.from_dict(user_data)

    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change a user's password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            Tuple of (success, message)
        """
        user_data = self.storage.load_user(user_id)
        if not user_data:
            return False, "User không tồn tại"

        # Verify old password
        if not self.verify_password(old_password, user_data.get('password_hash', '')):
            return False, "Mật khẩu hiện tại không đúng"

        # Validate new password
        if len(new_password) < 6:
            return False, "Mật khẩu mới phải có ít nhất 6 ký tự"

        # Update password
        user_data['password_hash'] = self.hash_password(new_password)
        self.storage.save_user(user_data)

        logger.info(f"Password changed for user: {user_id}")
        return True, "Đổi mật khẩu thành công"

    def find_or_create_oauth_user(
        self,
        provider: str,
        provider_user_id: str,
        email: str,
        name: str,
        avatar_url: Optional[str] = None
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Find existing user by OAuth provider ID or create new one.

        Args:
            provider: OAuth provider (google, facebook, apple)
            provider_user_id: Unique user ID from provider
            email: User email from provider
            name: User's display name
            avatar_url: User's avatar URL (optional)

        Returns:
            Tuple of (success, message, user_object)
        """
        # Check if user already exists with this OAuth provider
        users = self.storage.list_users()
        for user_data in users:
            oauth_accounts = user_data.get('metadata', {}).get('oauth_accounts', {})
            if oauth_accounts.get(provider) == provider_user_id:
                # Found existing OAuth user
                user = User.from_dict(user_data)
                logger.info(f"OAuth login: existing user {user.username} via {provider}")
                return True, "Đăng nhập thành công", user

        # Check if user exists with this email (link accounts)
        existing_user_data = self.storage.find_user_by_email(email)
        if existing_user_data:
            # Link OAuth account to existing user
            user = User.from_dict(existing_user_data)
            if 'oauth_accounts' not in user.metadata:
                user.metadata['oauth_accounts'] = {}
            user.metadata['oauth_accounts'][provider] = provider_user_id
            if avatar_url and not user.metadata.get('avatar_url'):
                user.metadata['avatar_url'] = avatar_url

            self.storage.save_user(user.to_dict())
            logger.info(f"Linked {provider} account to existing user {user.username}")
            return True, f"Đã liên kết tài khoản {provider}", user

        # Create new user from OAuth
        # Generate username from email or name
        base_username = email.split('@')[0] if email else name.replace(' ', '_').lower()
        username = base_username
        counter = 1
        while self.storage.find_user_by_username(username):
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            username=username,
            email=email,
            password_hash='',  # No password for OAuth users
            role='user',
            metadata={
                'oauth_accounts': {provider: provider_user_id},
                'display_name': name,
                'avatar_url': avatar_url or '',
                'auth_provider': provider
            }
        )

        self.storage.save_user(user.to_dict())
        logger.info(f"Created new OAuth user {username} via {provider}")
        return True, "Tạo tài khoản thành công", user

