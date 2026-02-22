"""World model representing a fictional world."""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class World:
    """Represents a fictional world that can contain multiple stories."""

    def __init__(
        self,
        name: str,
        description: str,
        world_id: Optional[str] = None,
        created_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        visibility: str = 'private',
        owner_id: Optional[str] = None,
        shared_with: Optional[List[str]] = None
    ):
        """
        Initialize a World.

        Args:
            name: Name of the world
            description: Description of the world
            world_id: Unique identifier (generated if not provided)
            created_at: Creation timestamp (current time if not provided)
            metadata: Additional metadata for the world
            visibility: 'public' or 'private' (default: 'private')
            owner_id: User ID of the creator
            shared_with: List of user IDs who have access (for private worlds)
        """
        self.world_id = world_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now().isoformat()
        self.metadata = metadata or {}
        self.visibility = visibility
        self.owner_id = owner_id
        self.shared_with = shared_with or []
        # Initialize calendar system if not exists
        if 'calendar' not in self.metadata:
            self.metadata['calendar'] = {
                'type': 'custom',  # custom/earth/fantasy
                'current_era': 'Kỷ nguyên mới',
                'current_year': 1,
                'year_name': 'Năm',
                'year_zero_name': 'Thời kỳ hỗn độn',  # Special name for year 0/null
                'month_count': 12,
                'day_count': 365
            }
        self.stories: List[str] = []  # Story IDs
        self.locations: List[str] = []  # Location IDs
        self.entities: List[str] = []  # Entity IDs

    def to_dict(self) -> Dict[str, Any]:
        """Convert World to dictionary."""
        return {
            "type": "world",
            "world_id": self.world_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "visibility": self.visibility,
            "owner_id": self.owner_id,
            "shared_with": self.shared_with,
            "stories": self.stories,
            "locations": self.locations,
            "entities": self.entities
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert World to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'World':
        """Create World from dictionary."""
        world = cls(
            name=data["name"],
            description=data["description"],
            world_id=data.get("world_id"),
            created_at=data.get("created_at"),
            metadata=data.get("metadata", {}),
            visibility=data.get("visibility", "private"),
            owner_id=data.get("owner_id"),
            shared_with=data.get("shared_with", [])
        )
        world.stories = data.get("stories", [])
        world.locations = data.get("locations", [])
        world.entities = data.get("entities", [])
        return world

    @classmethod
    def from_json(cls, json_str: str) -> 'World':
        """Create World from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def add_story(self, story_id: str) -> None:
        """Add a story to this world."""
        if story_id not in self.stories:
            self.stories.append(story_id)

    def add_location(self, location_id: str) -> None:
        """Add a location to this world."""
        if location_id not in self.locations:
            self.locations.append(location_id)

    def add_entity(self, entity_id: str) -> None:
        """Add an entity to this world."""
        if entity_id not in self.entities:
            self.entities.append(entity_id)
