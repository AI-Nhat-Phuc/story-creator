"""Abstract base class for storage backends."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseStorage(ABC):
    """Abstract base class for all storage backends."""

    @abstractmethod
    def save_world(self, world_data: Dict[str, Any]) -> None:
        """Save world data."""
        pass

    @abstractmethod
    def load_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        """Load world data by ID."""
        pass

    @abstractmethod
    def list_worlds(self) -> List[Dict[str, Any]]:
        """List all worlds."""
        pass

    @abstractmethod
    def save_story(self, story_data: Dict[str, Any]) -> None:
        """Save story data."""
        pass

    @abstractmethod
    def load_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Load story data by ID."""
        pass

    @abstractmethod
    def list_stories(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all stories, optionally filtered by world_id."""
        pass

    @abstractmethod
    def save_location(self, location_data: Dict[str, Any]) -> None:
        """Save location data."""
        pass

    @abstractmethod
    def load_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Load location data by ID."""
        pass

    @abstractmethod
    def save_entity(self, entity_data: Dict[str, Any]) -> None:
        """Save entity data."""
        pass

    @abstractmethod
    def load_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Load entity data by ID."""
        pass

    @abstractmethod
    def save_time_cone(self, time_cone_data: Dict[str, Any]) -> None:
        """Save time cone data."""
        pass

    @abstractmethod
    def load_time_cone(self, time_cone_id: str) -> Optional[Dict[str, Any]]:
        """Load time cone data by ID."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about stored data."""
        pass
