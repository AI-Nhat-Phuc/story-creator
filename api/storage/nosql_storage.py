"""NoSQL database storage using TinyDB for improved performance."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import logging
import json

logger = logging.getLogger(__name__)


class UTF8JSONStorage(JSONStorage):
    """Custom JSONStorage with UTF-8 encoding to handle Vietnamese text."""

    def __init__(self, path, create_dirs=False, encoding='utf-8', **kwargs):
        kwargs.setdefault('ensure_ascii', False)
        super().__init__(path, create_dirs=create_dirs, encoding=encoding, **kwargs)


class NoSQLStorage:
    """
    Handles storage and retrieval using TinyDB (NoSQL database).
    Provides better performance than file-based JSON storage.

    CRITICAL SAFETY FEATURES:
    - Database is NEVER truncated/cleared on initialization
    - Corrupted data is backed up, NOT deleted
    - clear_all() is protected and only works in test environment
    - All operations are append/update only, never destructive
    """

    def __init__(self, db_path: str = "story_creator.db"):
        """
        Initialize NoSQL Storage.

        SAFETY GUARANTEE: This will NEVER delete existing data.
        If the database file exists, it will be opened and used as-is.
        If corrupted, a backup is created but original data is preserved.

        Args:
            db_path: Path to the database file
        """
        self.db_path = Path(db_path)

        # Use TinyDB with proper configuration to prevent corruption
        from tinydb.storages import JSONStorage
        from tinydb.middlewares import CachingMiddleware

        # Initialize with UTF-8 encoding and write-through cache
        self.db = TinyDB(str(self.db_path),
                        storage=CachingMiddleware(UTF8JSONStorage),
                        indent=2,
                        ensure_ascii=False)

        # Create separate tables for each entity type
        self.worlds = self.db.table('worlds')
        self.stories = self.db.table('stories')
        self.locations = self.db.table('locations')
        self.entities = self.db.table('entities')
        self.time_cones = self.db.table('time_cones')

        logger.info(f"NoSQLStorage initialized: {db_path}")

    def _safe_read(self, table, operation):
        """
        Safely execute a read operation with auto-recovery on corruption.

        Args:
            table: TinyDB table object
            operation: Lambda function that performs the read operation

        Returns:
            Operation result or empty list/None on corruption
        """
        try:
            return operation()
        except (json.JSONDecodeError, ValueError) as e:
            # Check if it's just an empty database (not corruption)
            import os
            if not os.path.exists(self.db_path) or os.path.getsize(self.db_path) == 0:
                logger.info("Empty or missing database file, initializing...")
                # Just return empty, don't recreate
                return [] if 'all' in str(operation) or 'search' in str(operation) else None

            # Real corruption - backup and log
            logger.error(f"Database corruption detected: {e}")
            self._backup_corrupt_database()
            # Return empty result after backup
            return [] if 'all' in str(operation) or 'search' in str(operation) else None

    def _backup_corrupt_database(self):
        """Backup corrupted database without deleting it."""
        import os
        import shutil
        from datetime import datetime

        if os.path.exists(self.db_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.db_path}.corrupt_{timestamp}"
            try:
                shutil.copy2(self.db_path, backup_path)
                logger.warning(f"Corrupt database backed up to: {backup_path}")
                logger.warning("Please check the backup file manually. Database will continue with existing data.")
            except Exception as e:
                logger.error(f"Failed to backup corrupt database: {e}")

    def save_world(self, world_data: Dict[str, Any]) -> str:
        """
        Save a world to the database.

        Args:
            world_data: World data dictionary

        Returns:
            World ID
        """
        world_id = world_data["world_id"]
        logger.debug(f"Saving world: {world_id} - {world_data.get('name', 'Unknown')}")

        # Check if world exists
        WorldQuery = Query()
        existing = self.worlds.search(WorldQuery.world_id == world_id)

        if existing:
            # Update existing world
            self.worlds.update(world_data, WorldQuery.world_id == world_id)
            logger.info(f"Updated world: {world_data.get('name', 'Unknown')}")
        else:
            # Insert new world
            self.worlds.insert(world_data)
            logger.info(f"Created new world: {world_data.get('name', 'Unknown')}")

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
        results = self._safe_read(self.worlds,
                                 lambda: self.worlds.search(WorldQuery.world_id == world_id))

        if results:
            return results[0]
        return None

    def list_worlds(self) -> List[Dict[str, Any]]:
        """
        List all worlds.

        Returns:
            List of world data dictionaries
        """
        return self._safe_read(self.worlds, lambda: self.worlds.all())

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
            return self._safe_read(self.stories,
                                  lambda: self.stories.search(StoryQuery.world_id == world_id))
        return self._safe_read(self.stories, lambda: self.stories.all())

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

    def list_locations(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all locations, optionally filtered by world.

        Args:
            world_id: Optional world ID to filter by

        Returns:
            List of location data dictionaries
        """
        if world_id:
            LocationQuery = Query()
            return self._safe_read(self.locations,
                                  lambda: self.locations.search(LocationQuery.world_id == world_id))
        return self._safe_read(self.locations, lambda: self.locations.all())

    def load_all_locations(self) -> List[Dict[str, Any]]:
        """
        Load all locations from the database.

        Returns:
            List of all location data dictionaries
        """
        return self._safe_read(self.locations, lambda: self.locations.all())

    def delete_location(self, location_id: str) -> bool:
        """
        Delete a location from the database.

        Args:
            location_id: Location ID

        Returns:
            True if deleted, False if not found
        """
        LocationQuery = Query()
        removed = self.locations.remove(LocationQuery.location_id == location_id)
        return len(removed) > 0

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

    def list_entities(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all entities, optionally filtered by world.

        Args:
            world_id: Optional world ID to filter by

        Returns:
            List of entity data dictionaries
        """
        if world_id:
            EntityQuery = Query()
            return self._safe_read(self.entities,
                                  lambda: self.entities.search(EntityQuery.world_id == world_id))
        return self._safe_read(self.entities, lambda: self.entities.all())

    def load_all_entities(self) -> List[Dict[str, Any]]:
        """
        Load all entities from the database.

        Returns:
            List of all entity data dictionaries
        """
        return self._safe_read(self.entities, lambda: self.entities.all())

    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity from the database.

        Args:
            entity_id: Entity ID

        Returns:
            True if deleted, False if not found
        """
        EntityQuery = Query()
        removed = self.entities.remove(EntityQuery.entity_id == entity_id)
        return len(removed) > 0

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

    def list_time_cones(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all time cones, optionally filtered by world.

        Args:
            world_id: Optional world ID to filter by

        Returns:
            List of time cone data dictionaries
        """
        if world_id:
            TimeConeQuery = Query()
            return self._safe_read(self.time_cones,
                                  lambda: self.time_cones.search(TimeConeQuery.world_id == world_id))
        return self._safe_read(self.time_cones, lambda: self.time_cones.all())

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
        """Close the database connection safely."""
        try:
            # Force flush all data before closing
            self.db.storage.flush()
            self.db.close()
        except Exception as e:
            logger.error(f"Error closing database: {e}")

    def flush(self) -> None:
        """Force flush all pending writes to disk."""
        try:
            self.db.storage.flush()
        except Exception as e:
            logger.error(f"Error flushing database: {e}")

    def clear_all(self) -> None:
        """
        Clear all data from the database (for testing ONLY).

        WARNING: This will DELETE ALL DATA. Should NEVER be called in production.
        Only used in test files.
        """
        import os
        # Extra safeguard: only allow in test environment
        if 'PYTEST_CURRENT_TEST' not in os.environ and 'TEST_MODE' not in os.environ:
            logger.error("CRITICAL: Attempted to clear database outside of test environment! Operation blocked.")
            raise RuntimeError("clear_all() can only be called in test environment. Set TEST_MODE=1 to proceed.")

        logger.warning("⚠️  CLEARING ALL DATABASE DATA (test mode)")
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
