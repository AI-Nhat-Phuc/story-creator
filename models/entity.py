"""Entity model representing characters or objects in stories."""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


class Entity:
    """Represents an entity (character, object, etc.) in a world."""
    
    def __init__(
        self,
        name: str,
        entity_type: str,
        description: str,
        world_id: str,
        entity_id: Optional[str] = None,
        created_at: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an Entity.
        
        Args:
            name: Name of the entity
            entity_type: Type of entity (character, object, creature, etc.)
            description: Description of the entity
            world_id: ID of the world this entity belongs to
            entity_id: Unique identifier (generated if not provided)
            created_at: Creation timestamp (current time if not provided)
            attributes: Entity attributes (strength, intelligence, etc.)
            metadata: Additional metadata for the entity
        """
        self.entity_id = entity_id or str(uuid.uuid4())
        self.name = name
        self.entity_type = entity_type
        self.description = description
        self.world_id = world_id
        self.created_at = created_at or datetime.now().isoformat()
        self.attributes = attributes or {}
        self.metadata = metadata or {}
        self.relationships: List[Dict[str, str]] = []  # Relationships with other entities
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert Entity to dictionary."""
        return {
            "type": "entity",
            "entity_id": self.entity_id,
            "name": self.name,
            "entity_type": self.entity_type,
            "description": self.description,
            "world_id": self.world_id,
            "created_at": self.created_at,
            "attributes": self.attributes,
            "metadata": self.metadata,
            "relationships": self.relationships
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert Entity to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create Entity from dictionary."""
        entity = cls(
            name=data["name"],
            entity_type=data["entity_type"],
            description=data["description"],
            world_id=data["world_id"],
            entity_id=data.get("entity_id"),
            created_at=data.get("created_at"),
            attributes=data.get("attributes", {}),
            metadata=data.get("metadata", {})
        )
        entity.relationships = data.get("relationships", [])
        return entity
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Entity':
        """Create Entity from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def add_relationship(self, entity_id: str, relationship_type: str) -> None:
        """Add a relationship to another entity."""
        relationship = {
            "entity_id": entity_id,
            "relationship_type": relationship_type
        }
        if relationship not in self.relationships:
            self.relationships.append(relationship)
