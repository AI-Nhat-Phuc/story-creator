"""Time cone model for temporal context in stories."""

import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class TimeCone:
    """Represents a time cone for temporal context in stories (light cone concept)."""
    
    def __init__(
        self,
        name: str,
        description: str,
        world_id: str,
        time_cone_id: Optional[str] = None,
        created_at: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        reference_event: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a TimeCone.
        
        Args:
            name: Name of the time cone
            description: Description of the time period/cone
            world_id: ID of the world this time cone belongs to
            time_cone_id: Unique identifier (generated if not provided)
            created_at: Creation timestamp (current time if not provided)
            start_time: Start of the time cone (narrative time)
            end_time: End of the time cone (narrative time)
            reference_event: Reference event for the time cone
            metadata: Additional metadata for the time cone
        """
        self.time_cone_id = time_cone_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.world_id = world_id
        self.created_at = created_at or datetime.now().isoformat()
        self.start_time = start_time
        self.end_time = end_time
        self.reference_event = reference_event
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert TimeCone to dictionary."""
        return {
            "type": "time_cone",
            "time_cone_id": self.time_cone_id,
            "name": self.name,
            "description": self.description,
            "world_id": self.world_id,
            "created_at": self.created_at,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "reference_event": self.reference_event,
            "metadata": self.metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert TimeCone to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeCone':
        """Create TimeCone from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            world_id=data["world_id"],
            time_cone_id=data.get("time_cone_id"),
            created_at=data.get("created_at"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            reference_event=data.get("reference_event"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TimeCone':
        """Create TimeCone from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
