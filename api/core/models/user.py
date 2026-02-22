"""User model for authentication and authorization."""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any


class User:
    """Represents a user account in the system."""

    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str = 'user',
        user_id: Optional[str] = None,
        created_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a User.

        Args:
            username: Unique username
            email: User email address
            password_hash: Hashed password (never store plain passwords)
            role: User role (user, admin, moderator, premium, guest)
            user_id: Unique identifier (auto-generated if None)
            created_at: ISO timestamp (auto-generated if None)
            metadata: Additional user data
        """
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.metadata = metadata or {}

        # Initialize quota limits based on role
        self._init_role_quotas()

    def _init_role_quotas(self):
        """Initialize quota limits based on user role."""
        from core.permissions import get_role_quota

        # Set quotas based on role if not already set
        if 'public_worlds_limit' not in self.metadata:
            self.metadata['public_worlds_limit'] = get_role_quota(self.role, 'public_worlds_limit')
        if 'public_stories_limit' not in self.metadata:
            self.metadata['public_stories_limit'] = get_role_quota(self.role, 'public_stories_limit')
        if 'gpt_requests_per_day' not in self.metadata:
            self.metadata['gpt_requests_per_day'] = get_role_quota(self.role, 'gpt_requests_per_day')

        # Initialize counters
        if 'public_worlds_count' not in self.metadata:
            self.metadata['public_worlds_count'] = 0
        if 'public_stories_count' not in self.metadata:
            self.metadata['public_stories_count'] = 0
        if 'gpt_requests_today' not in self.metadata:
            self.metadata['gpt_requests_today'] = 0
        if 'gpt_last_reset' not in self.metadata:
            self.metadata['gpt_last_reset'] = datetime.utcnow().date().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert User to dictionary."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at,
            'metadata': self.metadata
        }

    def to_safe_dict(self) -> Dict[str, Any]:
        """Convert User to dictionary without sensitive data (no password_hash)."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at,
            'metadata': self.metadata
        }

    def to_json(self) -> str:
        """Convert User to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User from dictionary."""
        return cls(
            user_id=data.get('user_id'),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            role=data.get('role', 'user'),
            created_at=data.get('created_at'),
            metadata=data.get('metadata', {})
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'User':
        """Create User from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def can_create_public_world(self) -> bool:
        """Check if user can create a new public world (within quota)."""
        return self.metadata.get('public_worlds_count', 0) < self.metadata.get('public_worlds_limit', 1)

    def can_create_public_story(self) -> bool:
        """Check if user can create a new public story (within quota)."""
        return self.metadata.get('public_stories_count', 0) < self.metadata.get('public_stories_limit', 20)

    def can_use_gpt(self) -> bool:
        """Check if user can use GPT (within daily quota)."""
        from core.permissions import has_permission, Permission

        # Check if unlimited GPT
        if has_permission(self.role, Permission.USE_GPT_UNLIMITED):
            return True

        # Check basic GPT permission
        if not has_permission(self.role, Permission.USE_GPT):
            return False

        # Reset counter if new day
        self._reset_gpt_counter_if_needed()

        # Check daily quota
        current = self.metadata.get('gpt_requests_today', 0)
        limit = self.metadata.get('gpt_requests_per_day', 50)
        return current < limit

    def _reset_gpt_counter_if_needed(self):
        """Reset GPT counter if it's a new day."""
        today = datetime.utcnow().date().isoformat()
        last_reset = self.metadata.get('gpt_last_reset', today)

        if last_reset != today:
            self.metadata['gpt_requests_today'] = 0
            self.metadata['gpt_last_reset'] = today

    def increment_public_worlds(self):
        """Increment public worlds count."""
        self.metadata['public_worlds_count'] = self.metadata.get('public_worlds_count', 0) + 1

    def increment_gpt_requests(self):
        """Increment GPT requests count."""
        self._reset_gpt_counter_if_needed()
        self.metadata['gpt_requests_today'] = self.metadata.get('gpt_requests_today', 0) + 1

    def decrement_public_worlds(self):
        """Decrement public worlds count (e.g., when world becomes private)."""
        self.metadata['public_worlds_count'] = max(0, self.metadata.get('public_worlds_count', 0) - 1)

    def increment_public_stories(self):
        """Increment public stories count."""
        self.metadata['public_stories_count'] = self.metadata.get('public_stories_count', 0) + 1

    def decrement_public_stories(self):
        """Decrement public stories count (e.g., when story becomes private)."""
        self.metadata['public_stories_count'] = max(0, self.metadata.get('public_stories_count', 0) - 1)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
