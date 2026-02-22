"""Event model representing a significant occurrence within a story's timeline."""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class Event:
    """Represents a significant event extracted from a story."""

    def __init__(
        self,
        title: str,
        description: str,
        story_id: str,
        world_id: str,
        event_id: Optional[str] = None,
        year: int = 0,
        era: str = "",
        characters: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        connections: Optional[List[Dict[str, Any]]] = None,
        story_position: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None,
        visibility: str = 'private',
        owner_id: Optional[str] = None
    ):
        """
        Initialize an Event.

        Args:
            title: Short title of the event
            description: Brief description (1-2 sentences)
            story_id: ID of the story this event belongs to
            world_id: ID of the world
            event_id: Unique identifier (generated if not provided)
            year: Year in the world's timeline
            era: Era/epoch name (optional)
            characters: List of entity IDs involved
            locations: List of location IDs involved
            connections: List of connections to other events
                [{target_event_id, relation_type, relation_label}]
            story_position: Paragraph index in story content (0-based)
            metadata: Additional metadata (abstract_image_seed, color, etc.)
            created_at: Creation timestamp
            visibility: 'public' or 'private' (inherited from story)
            owner_id: User ID of the creator (inherited from story)
        """
        self.event_id = event_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.story_id = story_id
        self.world_id = world_id
        self.year = year
        self.era = era
        self.characters = characters or []
        self.locations = locations or []
        self.connections = connections or []
        self.story_position = story_position
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now().isoformat()
        self.visibility = visibility
        self.owner_id = owner_id

        # Ensure abstract_image_seed exists in metadata
        if 'abstract_image_seed' not in self.metadata:
            self.metadata['abstract_image_seed'] = self.title.lower().replace(' ', '_')

    def to_dict(self) -> Dict[str, Any]:
        """Convert Event to dictionary."""
        return {
            "type": "event",
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "story_id": self.story_id,
            "world_id": self.world_id,
            "year": self.year,
            "era": self.era,
            "characters": self.characters,
            "locations": self.locations,
            "connections": self.connections,
            "story_position": self.story_position,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "visibility": self.visibility,
            "owner_id": self.owner_id
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert Event to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create Event from dictionary."""
        event = cls(
            title=data["title"],
            description=data["description"],
            story_id=data["story_id"],
            world_id=data["world_id"],
            event_id=data.get("event_id"),
            year=data.get("year", 0),
            era=data.get("era", ""),
            characters=data.get("characters", []),
            locations=data.get("locations", []),
            connections=data.get("connections", []),
            story_position=data.get("story_position", 0),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            visibility=data.get("visibility", "private"),
            owner_id=data.get("owner_id")
        )
        return event

    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        """Create Event from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def add_connection(self, target_event_id: str, relation_type: str, relation_label: str = "") -> None:
        """Add a connection to another event.

        Args:
            target_event_id: ID of the target event
            relation_type: Type of relation (character, location, causation, temporal)
            relation_label: Description of the connection
        """
        # Avoid duplicates
        for conn in self.connections:
            if conn.get('target_event_id') == target_event_id and conn.get('relation_type') == relation_type:
                return

        self.connections.append({
            'target_event_id': target_event_id,
            'relation_type': relation_type,
            'relation_label': relation_label
        })

    def remove_connection(self, target_event_id: str) -> None:
        """Remove all connections to a specific event."""
        self.connections = [
            c for c in self.connections
            if c.get('target_event_id') != target_event_id
        ]

    def __repr__(self) -> str:
        return f"Event(id={self.event_id[:8]}, title='{self.title}', year={self.year})"
