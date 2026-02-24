"""Story model representing a narrative within a world."""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class Story:
    """Represents a story within a world."""

    def __init__(
        self,
        title: str,
        content: str,
        world_id: str,
        story_id: Optional[str] = None,
        created_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        visibility: str = 'private',
        owner_id: Optional[str] = None,
        shared_with: Optional[List[str]] = None
    ):
        """
        Initialize a Story.

        Args:
            title: Title of the story
            content: Content/narrative of the story
            world_id: ID of the world this story belongs to
            story_id: Unique identifier (generated if not provided)
            created_at: Creation timestamp (current time if not provided)
            metadata: Additional metadata for the story
            visibility: 'draft', 'private', or 'public' (default: 'private')
            owner_id: User ID of the creator
            shared_with: List of user IDs who have access (for private stories)
        """
        self.story_id = story_id or str(uuid.uuid4())
        self.title = title
        self.content = content
        self.world_id = world_id
        self.created_at = created_at or datetime.now().isoformat()
        self.metadata = metadata or {}
        self.visibility = visibility
        self.owner_id = owner_id
        self.shared_with = shared_with or []
        # World time: when this story happens in the world's timeline
        if 'world_time' not in self.metadata:
            self.metadata['world_time'] = {
                'era': '',
                'year': 0,
                'month': 0,
                'day': 0,
                'description': ''  # e.g., "Mùa xuân năm đầu tiên"
            }
        self.locations: List[str] = []  # Location IDs where story takes place
        self.entities: List[str] = []  # Entity IDs participating in story
        self.time_cones: List[str] = []  # Time cone IDs for temporal context
        self.linked_stories: List[str] = []  # Related story IDs

    def to_dict(self) -> Dict[str, Any]:
        """Convert Story to dictionary."""
        return {
            "type": "story",
            "story_id": self.story_id,
            "title": self.title,
            "content": self.content,
            "world_id": self.world_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "visibility": self.visibility,
            "owner_id": self.owner_id,
            "shared_with": self.shared_with,
            "locations": self.locations,
            "entities": self.entities,
            "time_cones": self.time_cones,
            "linked_stories": self.linked_stories
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert Story to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Story':
        """Create Story from dictionary."""
        story = cls(
            title=data["title"],
            content=data["content"],
            world_id=data["world_id"],
            story_id=data.get("story_id"),
            created_at=data.get("created_at"),
            metadata=data.get("metadata", {}),
            visibility=data.get("visibility", "private"),
            owner_id=data.get("owner_id"),
            shared_with=data.get("shared_with", [])
        )
        story.locations = data.get("locations", [])
        story.entities = data.get("entities", [])
        story.time_cones = data.get("time_cones", [])
        story.linked_stories = data.get("linked_stories", [])
        return story

    @classmethod
    def from_json(cls, json_str: str) -> 'Story':
        """Create Story from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def add_location(self, location_id: str) -> None:
        """Add a location to this story."""
        if location_id not in self.locations:
            self.locations.append(location_id)

    def add_entity(self, entity_id: str) -> None:
        """Add an entity to this story."""
        if entity_id not in self.entities:
            self.entities.append(entity_id)

    def add_time_cone(self, time_cone_id: str) -> None:
        """Add a time cone to this story."""
        if time_cone_id not in self.time_cones:
            self.time_cones.append(time_cone_id)

    def link_story(self, story_id: str) -> None:
        """Link this story to another story."""
        if story_id not in self.linked_stories:
            self.linked_stories.append(story_id)
