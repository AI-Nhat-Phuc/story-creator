"""NoSQL database storage using TinyDB for improved performance."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from tinydb import TinyDB, Query


class NoSQLStorage:
    """
    Handles storage and retrieval using TinyDB (NoSQL database).
    Provides better performance than file-based JSON storage.
    """
    
    def __init__(self, db_path: str = "story_creator.db"):
        """
        Initialize NoSQL Storage.
        
        Args:
            db_path: Path to the database file
        """
        self.db_path = Path(db_path)
        self.db = TinyDB(str(self.db_path))
        
        # Create separate tables for each entity type
        self.worlds = self.db.table('worlds')
        self.stories = self.db.table('stories')
        self.locations = self.db.table('locations')
        self.entities = self.db.table('entities')
        self.time_cones = self.db.table('time_cones')
    
    def save_world(self, world_data: Dict[str, Any]) -> str:
        """
        Save a world to the database.
        
        Args:
            world_data: World data dictionary
            
        Returns:
            World ID
        """
        world_id = world_data["world_id"]
        
        # Check if world exists
        WorldQuery = Query()
        existing = self.worlds.search(WorldQuery.world_id == world_id)
        
        if existing:
            # Update existing world
            self.worlds.update(world_data, WorldQuery.world_id == world_id)
        else:
            # Insert new world
            self.worlds.insert(world_data)
        
        return world_id
    
    def load_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a world from the database.
        
        Args:
            world_id: World ID
            
        Returns:
            World data dictionary or None if not found
        """
        WorldQuery = Query()
        results = self.worlds.search(WorldQuery.world_id == world_id)
        
        if results:
            return results[0]
        return None
    
    def list_worlds(self) -> List[Dict[str, Any]]:
        """
        List all worlds.
        
        Returns:
            List of world data dictionaries
        """
        return self.worlds.all()
    
    def save_story(self, story_data: Dict[str, Any]) -> str:
        """
        Save a story to the database.
        
        Args:
            story_data: Story data dictionary
            
        Returns:
            Story ID
        """
        story_id = story_data["story_id"]
        
        StoryQuery = Query()
        existing = self.stories.search(StoryQuery.story_id == story_id)
        
        if existing:
            self.stories.update(story_data, StoryQuery.story_id == story_id)
        else:
            self.stories.insert(story_data)
        
        return story_id
    
    def load_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a story from the database.
        
        Args:
            story_id: Story ID
            
        Returns:
            Story data dictionary or None if not found
        """
        StoryQuery = Query()
        results = self.stories.search(StoryQuery.story_id == story_id)
        
        if results:
            return results[0]
        return None
    
    def list_stories(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all stories, optionally filtered by world.
        
        Args:
            world_id: Optional world ID to filter by
            
        Returns:
            List of story data dictionaries
        """
        if world_id:
            StoryQuery = Query()
            return self.stories.search(StoryQuery.world_id == world_id)
        return self.stories.all()
    
    def save_location(self, location_data: Dict[str, Any]) -> str:
        """
        Save a location to the database.
        
        Args:
            location_data: Location data dictionary
            
        Returns:
            Location ID
        """
        location_id = location_data["location_id"]
        
        LocationQuery = Query()
        existing = self.locations.search(LocationQuery.location_id == location_id)
        
        if existing:
            self.locations.update(location_data, LocationQuery.location_id == location_id)
        else:
            self.locations.insert(location_data)
        
        return location_id
    
    def load_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a location from the database.
        
        Args:
            location_id: Location ID
            
        Returns:
            Location data dictionary or None if not found
        """
        LocationQuery = Query()
        results = self.locations.search(LocationQuery.location_id == location_id)
        
        if results:
            return results[0]
        return None
    
    def save_entity(self, entity_data: Dict[str, Any]) -> str:
        """
        Save an entity to the database.
        
        Args:
            entity_data: Entity data dictionary
            
        Returns:
            Entity ID
        """
        entity_id = entity_data["entity_id"]
        
        EntityQuery = Query()
        existing = self.entities.search(EntityQuery.entity_id == entity_id)
        
        if existing:
            self.entities.update(entity_data, EntityQuery.entity_id == entity_id)
        else:
            self.entities.insert(entity_data)
        
        return entity_id
    
    def load_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Load an entity from the database.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity data dictionary or None if not found
        """
        EntityQuery = Query()
        results = self.entities.search(EntityQuery.entity_id == entity_id)
        
        if results:
            return results[0]
        return None
    
    def save_time_cone(self, time_cone_data: Dict[str, Any]) -> str:
        """
        Save a time cone to the database.
        
        Args:
            time_cone_data: Time cone data dictionary
            
        Returns:
            Time cone ID
        """
        time_cone_id = time_cone_data["time_cone_id"]
        
        TimeConeQuery = Query()
        existing = self.time_cones.search(TimeConeQuery.time_cone_id == time_cone_id)
        
        if existing:
            self.time_cones.update(time_cone_data, TimeConeQuery.time_cone_id == time_cone_id)
        else:
            self.time_cones.insert(time_cone_data)
        
        return time_cone_id
    
    def load_time_cone(self, time_cone_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a time cone from the database.
        
        Args:
            time_cone_id: Time cone ID
            
        Returns:
            Time cone data dictionary or None if not found
        """
        TimeConeQuery = Query()
        results = self.time_cones.search(TimeConeQuery.time_cone_id == time_cone_id)
        
        if results:
            return results[0]
        return None
    
    def delete_world(self, world_id: str) -> bool:
        """
        Delete a world from the database.
        
        Args:
            world_id: World ID
            
        Returns:
            True if deleted, False if not found
        """
        WorldQuery = Query()
        result = self.worlds.remove(WorldQuery.world_id == world_id)
        return len(result) > 0
    
    def delete_story(self, story_id: str) -> bool:
        """
        Delete a story from the database.
        
        Args:
            story_id: Story ID
            
        Returns:
            True if deleted, False if not found
        """
        StoryQuery = Query()
        result = self.stories.remove(StoryQuery.story_id == story_id)
        return len(result) > 0
    
    def close(self) -> None:
        """Close the database connection."""
        self.db.close()
    
    def clear_all(self) -> None:
        """Clear all data from the database (for testing)."""
        self.worlds.truncate()
        self.stories.truncate()
        self.locations.truncate()
        self.entities.truncate()
        self.time_cones.truncate()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with counts of each entity type
        """
        return {
            "worlds": len(self.worlds),
            "stories": len(self.stories),
            "locations": len(self.locations),
            "entities": len(self.entities),
            "time_cones": len(self.time_cones)
        }
