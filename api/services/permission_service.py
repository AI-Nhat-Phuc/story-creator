"""Permission service for checking access control on worlds, stories, and events."""

from typing import Optional, Dict, Any, List
from core.models.world import World
from core.models.story import Story
from core.models.event import Event


class PermissionService:
    """Service for checking permissions on content items."""

    @staticmethod
    def can_view(user_id: Optional[str], item: Dict[str, Any]) -> bool:
        """
        Check if a user can view an item (world/story/event).

        Rules:
        - Public items: Anyone can view (including anonymous)
        - Private items: Only owner and shared users can view

        Args:
            user_id: Current user's ID (None for anonymous)
            item: Dictionary representation of World/Story/Event

        Returns:
            True if user can view, False otherwise
        """
        visibility = item.get('visibility', 'private')

        # Public items are viewable by anyone
        if visibility == 'public':
            return True

        # Anonymous users can only see public items
        if user_id is None:
            return False

        # Owner can always view their own items
        owner_id = item.get('owner_id')
        if owner_id == user_id:
            return True

        # Check if user is in shared_with list
        shared_with = item.get('shared_with', [])
        if user_id in shared_with:
            return True

        return False

    @staticmethod
    def can_edit(user_id: Optional[str], item: Dict[str, Any]) -> bool:
        """
        Check if a user can edit an item.

        Rules:
        - Only the owner can edit
        - Shared users have read-only access

        Args:
            user_id: Current user's ID (None for anonymous)
            item: Dictionary representation of World/Story/Event

        Returns:
            True if user can edit, False otherwise
        """
        if user_id is None:
            return False

        owner_id = item.get('owner_id')
        return owner_id == user_id

    @staticmethod
    def can_delete(user_id: Optional[str], item: Dict[str, Any]) -> bool:
        """
        Check if a user can delete an item.

        Rules:
        - Only the owner can delete

        Args:
            user_id: Current user's ID (None for anonymous)
            item: Dictionary representation of World/Story/Event

        Returns:
            True if user can delete, False otherwise
        """
        return PermissionService.can_edit(user_id, item)

    @staticmethod
    def can_share(user_id: Optional[str], item: Dict[str, Any]) -> bool:
        """
        Check if a user can share an item with others.

        Rules:
        - Only the owner can share

        Args:
            user_id: Current user's ID (None for anonymous)
            item: Dictionary representation of World/Story/Event

        Returns:
            True if user can share, False otherwise
        """
        return PermissionService.can_edit(user_id, item)

    @staticmethod
    def filter_viewable(user_id: Optional[str], items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of items to only those the user can view.

        Args:
            user_id: Current user's ID (None for anonymous)
            items: List of dictionaries representing World/Story/Event

        Returns:
            Filtered list of viewable items
        """
        return [item for item in items if PermissionService.can_view(user_id, item)]

    @staticmethod
    def get_user_owned_items(user_id: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get all items owned by a specific user.

        Args:
            user_id: User ID to filter by
            items: List of dictionaries representing World/Story/Event

        Returns:
            List of items owned by user
        """
        return [item for item in items if item.get('owner_id') == user_id]

    @staticmethod
    def get_shared_with_user(user_id: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get all items shared with a specific user.

        Args:
            user_id: User ID to filter by
            items: List of dictionaries representing World/Story/Event

        Returns:
            List of items shared with user
        """
        return [item for item in items if user_id in item.get('shared_with', [])]
