"""Role and permission definitions for the system."""

from enum import Enum
from typing import List, Dict, Set


class Role(str, Enum):
    """User roles in the system."""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    PREMIUM = 'premium'
    USER = 'user'
    GUEST = 'guest'


class Permission(str, Enum):
    """Permissions that can be assigned to roles."""
    # User management
    MANAGE_USERS = 'manage_users'
    VIEW_USERS = 'view_users'
    BAN_USERS = 'ban_users'

    # Content management
    MANAGE_ALL_CONTENT = 'manage_all_content'
    DELETE_ANY_CONTENT = 'delete_any_content'
    VIEW_ALL_CONTENT = 'view_all_content'

    # World permissions
    CREATE_WORLD = 'create_world'
    EDIT_OWN_WORLD = 'edit_own_world'
    DELETE_OWN_WORLD = 'delete_own_world'
    SHARE_WORLD = 'share_world'

    # Story permissions
    CREATE_STORY = 'create_story'
    EDIT_OWN_STORY = 'edit_own_story'
    DELETE_OWN_STORY = 'delete_own_story'
    SHARE_STORY = 'share_story'

    # Event permissions
    CREATE_EVENT = 'create_event'
    EDIT_OWN_EVENT = 'edit_own_event'
    DELETE_OWN_EVENT = 'delete_own_event'

    # GPT features
    USE_GPT = 'use_gpt'
    USE_GPT_UNLIMITED = 'use_gpt_unlimited'

    # Quota permissions
    UNLIMITED_PUBLIC_WORLDS = 'unlimited_public_worlds'
    UNLIMITED_PUBLIC_STORIES = 'unlimited_public_stories'
    INCREASED_QUOTA = 'increased_quota'


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Admin chỉ quản lý user và hệ thống, KHÔNG tạo content
        Permission.MANAGE_USERS,
        Permission.VIEW_USERS,
        Permission.BAN_USERS,
        Permission.MANAGE_ALL_CONTENT,  # Quản lý content của người khác
        Permission.DELETE_ANY_CONTENT,  # Xóa content vi phạm
        Permission.VIEW_ALL_CONTENT,    # Xem tất cả content
    },

    Role.MODERATOR: {
        # Content moderation
        Permission.VIEW_USERS,
        Permission.VIEW_ALL_CONTENT,
        Permission.DELETE_ANY_CONTENT,
        Permission.CREATE_WORLD,
        Permission.EDIT_OWN_WORLD,
        Permission.DELETE_OWN_WORLD,
        Permission.SHARE_WORLD,
        Permission.CREATE_STORY,
        Permission.EDIT_OWN_STORY,
        Permission.DELETE_OWN_STORY,
        Permission.SHARE_STORY,
        Permission.CREATE_EVENT,
        Permission.EDIT_OWN_EVENT,
        Permission.DELETE_OWN_EVENT,
        Permission.USE_GPT,
        Permission.INCREASED_QUOTA,
    },

    Role.PREMIUM: {
        # Premium features
        Permission.CREATE_WORLD,
        Permission.EDIT_OWN_WORLD,
        Permission.DELETE_OWN_WORLD,
        Permission.SHARE_WORLD,
        Permission.CREATE_STORY,
        Permission.EDIT_OWN_STORY,
        Permission.DELETE_OWN_STORY,
        Permission.SHARE_STORY,
        Permission.CREATE_EVENT,
        Permission.EDIT_OWN_EVENT,
        Permission.DELETE_OWN_EVENT,
        Permission.USE_GPT,
        Permission.USE_GPT_UNLIMITED,
        Permission.INCREASED_QUOTA,
    },

    Role.USER: {
        # Standard user
        Permission.CREATE_WORLD,
        Permission.EDIT_OWN_WORLD,
        Permission.DELETE_OWN_WORLD,
        Permission.SHARE_WORLD,
        Permission.CREATE_STORY,
        Permission.EDIT_OWN_STORY,
        Permission.DELETE_OWN_STORY,
        Permission.SHARE_STORY,
        Permission.CREATE_EVENT,
        Permission.EDIT_OWN_EVENT,
        Permission.DELETE_OWN_EVENT,
        Permission.USE_GPT,
    },

    Role.GUEST: {
        # Read-only access
    }
}


# Quota limits by role
ROLE_QUOTAS: Dict[Role, Dict[str, int]] = {
    Role.ADMIN: {
        # Admin không tạo content, chỉ quản lý hệ thống
        'public_worlds_limit': 0,
        'public_stories_limit': 0,
        'gpt_requests_per_day': 0,
    },
    Role.MODERATOR: {
        'public_worlds_limit': 20,
        'public_stories_limit': 100,
        'gpt_requests_per_day': 500,
    },
    Role.PREMIUM: {
        'public_worlds_limit': 10,
        'public_stories_limit': 50,
        'gpt_requests_per_day': 200,
    },
    Role.USER: {
        'public_worlds_limit': 1,
        'public_stories_limit': 20,
        'gpt_requests_per_day': 50,
    },
    Role.GUEST: {
        'public_worlds_limit': 0,
        'public_stories_limit': 0,
        'gpt_requests_per_day': 0,
    },
}


def has_permission(role: str, permission: Permission) -> bool:
    """
    Check if a role has a specific permission.

    Args:
        role: User role as string
        permission: Permission to check

    Returns:
        True if role has permission, False otherwise
    """
    try:
        role_enum = Role(role)
        return permission in ROLE_PERMISSIONS.get(role_enum, set())
    except ValueError:
        return False


def get_role_permissions(role: str) -> Set[Permission]:
    """
    Get all permissions for a role.

    Args:
        role: User role as string

    Returns:
        Set of permissions for the role
    """
    try:
        role_enum = Role(role)
        return ROLE_PERMISSIONS.get(role_enum, set())
    except ValueError:
        return set()


def get_role_quota(role: str, quota_key: str) -> int:
    """
    Get quota limit for a role.

    Args:
        role: User role as string
        quota_key: Quota key (e.g., 'public_worlds_limit')

    Returns:
        Quota limit for the role
    """
    try:
        role_enum = Role(role)
        quotas = ROLE_QUOTAS.get(role_enum, ROLE_QUOTAS[Role.USER])
        return quotas.get(quota_key, 0)
    except ValueError:
        return ROLE_QUOTAS[Role.USER].get(quota_key, 0)


def can_access_resource(user_role: str, resource_owner_role: str) -> bool:
    """
    Check if a user role can access resources from another role.

    Rules:
    - Admin can access everything
    - Moderator can access user/premium content
    - Users can only access their own content

    Args:
        user_role: Role of the user trying to access
        resource_owner_role: Role of the resource owner

    Returns:
        True if access is allowed
    """
    try:
        user = Role(user_role)
        owner = Role(resource_owner_role)

        if user == Role.ADMIN:
            return True

        if user == Role.MODERATOR:
            return owner in [Role.USER, Role.PREMIUM, Role.MODERATOR]

        # Users can only access their own content
        return user == owner

    except ValueError:
        return False


# Role display information
ROLE_INFO: Dict[Role, Dict[str, str]] = {
    Role.ADMIN: {
        'label': 'Quản trị viên',
        'badge_color': 'badge-error',
        'icon': '👑',
        'description': 'Quản lý hệ thống và người dùng (không tạo nội dung)'
    },
    Role.MODERATOR: {
        'label': 'Kiểm duyệt viên',
        'badge_color': 'badge-warning',
        'icon': '🛡️',
        'description': 'Quản lý nội dung và người dùng'
    },
    Role.PREMIUM: {
        'label': 'Premium',
        'badge_color': 'badge-primary',
        'icon': '⭐',
        'description': 'Tính năng cao cấp không giới hạn'
    },
    Role.USER: {
        'label': 'Người dùng',
        'badge_color': 'badge-info',
        'icon': '👤',
        'description': 'Người dùng thường'
    },
    Role.GUEST: {
        'label': 'Khách',
        'badge_color': 'badge-ghost',
        'icon': '👁️',
        'description': 'Chỉ xem nội dung công khai'
    },
}


def get_role_info(role: str) -> Dict[str, str]:
    """
    Get display information for a role.

    Args:
        role: User role as string

    Returns:
        Dictionary with label, badge_color, icon, description
    """
    try:
        role_enum = Role(role)
        return ROLE_INFO.get(role_enum, ROLE_INFO[Role.USER])
    except ValueError:
        return ROLE_INFO[Role.USER]
