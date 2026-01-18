"""Location model representing places where stories occur."""

import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class Location:
    """Represents a location/place in a world."""
    
    def __init__(
        self,
        name: str,
        description: str,
        world_id: str,
        location_id: Optional[str] = None,
        created_at: Optional[str] = None,
        coordinates: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Location.
        
        Args:
            name: Name of the location
            description: Description of the location
            world_id: ID of the world this location belongs to
            location_id: Unique identifier (generated if not provided)
            created_at: Creation timestamp (current time if not provided)
            coordinates: Spatial coordinates (x, y, z, etc.)
            metadata: Additional metadata for the location
        """
        self.location_id = location_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.world_id = world_id
        self.created_at = created_at or datetime.now().isoformat()
        self.coordinates = coordinates or {}
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert Location to dictionary."""
        return {
            "type": "location",
            "location_id": self.location_id,
            "name": self.name,
            "description": self.description,
            "world_id": self.world_id,
            "created_at": self.created_at,
            "coordinates": self.coordinates,
            "metadata": self.metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert Location to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """Create Location from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            world_id=data["world_id"],
            location_id=data.get("location_id"),
            created_at=data.get("created_at"),
            coordinates=data.get("coordinates", {}),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Location':
        """Create Location from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
