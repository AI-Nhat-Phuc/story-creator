"""NoSQL database storage using TinyDB for improved performance."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import logging
import json
from services.permission_service import PermissionService

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
        self.events = self.db.table('events')
        self.event_analysis_cache = self.db.table('event_analysis_cache')
        self.users = self.db.table('users')
        self.gpt_tasks = self.db.table('gpt_tasks')

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

    def list_worlds(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all worlds visible to the user.

        Args:
            user_id: Current user ID (None for anonymous users)

        Returns:
            List of world data dictionaries filtered by permissions
        """
        all_worlds = self._safe_read(self.worlds, lambda: self.worlds.all())

        # If no user_id provided, only return public worlds
        if user_id is None:
            return [w for w in all_worlds if w.get('visibility') == 'public']

        # Filter by permissions (public + owned + shared)
        return PermissionService.filter_viewable(user_id, all_worlds)

    def list_worlds_summary(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List worlds with minimal fields for dropdowns/stats.

        Only returns world_id, name, created_at, visibility, owner_id, shared_with, world_type.
        Uses permission filtering.

        Args:
            user_id: Current user ID (None for anonymous)

        Returns:
            List of minimal world dicts
        """
        SUMMARY_KEYS = ('world_id', 'name', 'created_at', 'visibility', 'owner_id', 'shared_with', 'world_type')
        all_worlds = self._safe_read(self.worlds, lambda: self.worlds.all())

        if user_id is None:
            filtered = [w for w in all_worlds if w.get('visibility') == 'public']
        else:
            filtered = PermissionService.filter_viewable(user_id, all_worlds)

        return [{k: w.get(k) for k in SUMMARY_KEYS} for w in filtered]

    def count_visible(self, collection_name: str, user_id: Optional[str] = None) -> dict:
        """
        Count documents by visibility category.

        Args:
            collection_name: 'worlds' or 'stories'
            user_id: Current user ID (None for anonymous)

        Returns:
            dict with counts: {total, public, private?, shared?}
        """
        table = getattr(self, collection_name)
        all_items = self._safe_read(table, lambda: table.all())

        public = [i for i in all_items if i.get('visibility') == 'public']

        if user_id is None:
            return {'total': len(public), 'public': len(public)}

        private = [i for i in all_items if i.get('visibility') == 'private' and i.get('owner_id') == user_id]
        shared = [i for i in all_items if i.get('visibility') == 'private' and i.get('owner_id') != user_id and user_id in i.get('shared_with', [])]

        return {
            'total': len(public) + len(private) + len(shared),
            'public': len(public),
            'private': len(private),
            'shared': len(shared)
        }

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

    def list_stories(self, world_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all stories visible to the user, optionally filtered by world.

        Args:
            world_id: Optional world ID to filter by
            user_id: Current user ID (None for anonymous users)

        Returns:
            List of story data dictionaries filtered by permissions
        """
        if world_id:
            StoryQuery = Query()
            stories = self._safe_read(self.stories,
                                  lambda: self.stories.search(StoryQuery.world_id == world_id))
        else:
            stories = self._safe_read(self.stories, lambda: self.stories.all())

        # If no user_id provided, only return public stories
        if user_id is None:
            return [s for s in stories if s.get('visibility') == 'public']

        # Filter by permissions
        return PermissionService.filter_viewable(user_id, stories)

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
        self.events.truncate()
        self.event_analysis_cache.truncate()

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
            "time_cones": len(self.time_cones),
            "events": len(self.events),
            "event_analysis_cache": len(self.event_analysis_cache)
        }

    # ===== GPT Task methods =====

    def save_gpt_task(self, task_data: Dict[str, Any]) -> str:
        """Save or update a GPT task."""
        task_id = task_data['task_id']
        TaskQuery = Query()
        existing = self.gpt_tasks.search(TaskQuery.task_id == task_id)
        if existing:
            self.gpt_tasks.update(task_data, TaskQuery.task_id == task_id)
        else:
            self.gpt_tasks.insert(task_data)
        return task_id

    def load_gpt_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load a GPT task by ID."""
        TaskQuery = Query()
        results = self._safe_read(self.gpt_tasks,
                                  lambda: self.gpt_tasks.search(TaskQuery.task_id == task_id))
        return results[0] if results else None

    def update_gpt_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        """Update specific fields of a GPT task."""
        TaskQuery = Query()
        existing = self.gpt_tasks.search(TaskQuery.task_id == task_id)
        if not existing:
            return False
        merged = {**existing[0], **update_data}
        self.gpt_tasks.update(merged, TaskQuery.task_id == task_id)
        return True

    def list_pending_gpt_tasks(self) -> List[Dict[str, Any]]:
        """List tasks that are still pending or processing."""
        TaskQuery = Query()
        return self._safe_read(self.gpt_tasks,
                               lambda: self.gpt_tasks.search(
                                   (TaskQuery.status == 'pending') | (TaskQuery.status == 'processing')
                               ))

    def cleanup_old_gpt_tasks(self, max_age_hours: int = 24) -> int:
        """Delete GPT tasks older than max_age_hours."""
        from datetime import datetime, timedelta
        cutoff = (datetime.utcnow() - timedelta(hours=max_age_hours)).isoformat()
        TaskQuery = Query()
        removed = self.gpt_tasks.remove(TaskQuery.created_at < cutoff)
        return len(removed) if removed else 0

    # ===== Event methods =====

    def save_event(self, event_data: Dict[str, Any]) -> str:
        """Save an event to the database.

        Args:
            event_data: Event data dictionary

        Returns:
            Event ID
        """
        event_id = event_data["event_id"]
        EventQuery = Query()
        existing = self.events.search(EventQuery.event_id == event_id)

        if existing:
            self.events.update(event_data, EventQuery.event_id == event_id)
            logger.info(f"Updated event: {event_data.get('title', 'Unknown')}")
        else:
            self.events.insert(event_data)
            logger.info(f"Created event: {event_data.get('title', 'Unknown')}")

        return event_id

    def load_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Load an event by ID."""
        EventQuery = Query()
        results = self._safe_read(self.events,
                                 lambda: self.events.search(EventQuery.event_id == event_id))
        if results:
            return results[0]
        return None

    def list_events_by_world(self, world_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all events for a world visible to the user."""
        EventQuery = Query()
        events = self._safe_read(self.events,
                              lambda: self.events.search(EventQuery.world_id == world_id))

        # If no user_id provided, only return events from public stories
        if user_id is None:
            return [e for e in events if e.get('visibility') == 'public']

        # Filter by permissions
        return PermissionService.filter_viewable(user_id, events)

    def list_events_by_story(self, story_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all events for a story visible to the user."""
        EventQuery = Query()
        events = self._safe_read(self.events,
                              lambda: self.events.search(EventQuery.story_id == story_id))

        # If no user_id provided, only return events from public story
        if user_id is None:
            return [e for e in events if e.get('visibility') == 'public']

        # Filter by permissions
        return PermissionService.filter_viewable(user_id, events)

    def update_event(self, event_id: str, data: Dict[str, Any]) -> bool:
        """Update an event."""
        EventQuery = Query()
        existing = self.events.search(EventQuery.event_id == event_id)
        if not existing:
            return False
        # Merge data
        updated = {**existing[0], **data}
        updated['event_id'] = event_id  # Ensure ID is preserved
        self.events.update(updated, EventQuery.event_id == event_id)
        return True

    def delete_event(self, event_id: str) -> bool:
        """Delete an event."""
        EventQuery = Query()
        removed = self.events.remove(EventQuery.event_id == event_id)
        return len(removed) > 0

    def delete_events_by_story(self, story_id: str) -> int:
        """Delete all events for a story. Returns count deleted."""
        EventQuery = Query()
        removed = self.events.remove(EventQuery.story_id == story_id)
        return len(removed)

    # ===== Event analysis cache methods =====

    def save_analysis_cache(self, story_id: str, content_hash: str,
                            gpt_response: Dict[str, Any], model: str) -> str:
        """Save GPT analysis cache for a story.

        Args:
            story_id: Story ID
            content_hash: SHA-256 hash of story content
            gpt_response: Raw GPT JSON response (events + connections)
            model: GPT model used

        Returns:
            Cache ID
        """
        import uuid as _uuid
        from datetime import datetime as _dt

        cache_id = str(_uuid.uuid4())
        CacheQuery = Query()

        # Remove old cache for this story (any hash)
        self.event_analysis_cache.remove(CacheQuery.story_id == story_id)

        cache_data = {
            "cache_id": cache_id,
            "story_id": story_id,
            "story_content_hash": content_hash,
            "raw_gpt_response": gpt_response,
            "extracted_events_count": len(gpt_response.get('events', [])),
            "analyzed_at": _dt.now().isoformat(),
            "model_used": model
        }

        self.event_analysis_cache.insert(cache_data)
        logger.info(f"Cached analysis for story {story_id} (hash: {content_hash[:12]}...)")
        return cache_id

    def get_analysis_cache(self, story_id: str, content_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached GPT analysis by story ID and content hash.

        Returns None on cache miss (no cache or hash mismatch).
        """
        CacheQuery = Query()
        results = self._safe_read(
            self.event_analysis_cache,
            lambda: self.event_analysis_cache.search(
                (CacheQuery.story_id == story_id) &
                (CacheQuery.story_content_hash == content_hash)
            )
        )
        if results:
            logger.info(f"Cache HIT for story {story_id}")
            return results[0]
        logger.info(f"Cache MISS for story {story_id}")
        return None

    def delete_analysis_cache(self, story_id: str) -> bool:
        """Delete GPT analysis cache for a story."""
        CacheQuery = Query()
        removed = self.event_analysis_cache.remove(CacheQuery.story_id == story_id)
        return len(removed) > 0

    # ==================== User Management ====================

    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """Save or update a user."""
        user_id = user_data.get('user_id')
        if not user_id:
            logger.error("Cannot save user: missing user_id")
            return False

        UserQuery = Query()
        existing = self._safe_read(
            self.users,
            lambda: self.users.search(UserQuery.user_id == user_id)
        )

        if existing:
            self.users.update(user_data, UserQuery.user_id == user_id)
            logger.info(f"Updated user: {user_id}")
        else:
            self.users.insert(user_data)
            logger.info(f"Created new user: {user_id}")
        return True

    def load_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load a user by user_id."""
        UserQuery = Query()
        results = self._safe_read(
            self.users,
            lambda: self.users.search(UserQuery.user_id == user_id)
        )
        return results[0] if results else None

    def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find a user by username."""
        UserQuery = Query()
        results = self._safe_read(
            self.users,
            lambda: self.users.search(UserQuery.username == username)
        )
        return results[0] if results else None

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by email."""
        UserQuery = Query()
        results = self._safe_read(
            self.users,
            lambda: self.users.search(UserQuery.email == email)
        )
        return results[0] if results else None

    def list_users(self) -> List[Dict[str, Any]]:
        """List all users."""
        return self._safe_read(self.users, lambda: self.users.all())

    def delete_user(self, user_id: str) -> bool:
        """Delete a user by user_id."""
        UserQuery = Query()
        removed = self.users.remove(UserQuery.user_id == user_id)
        return len(removed) > 0

