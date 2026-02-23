"""MongoDB Atlas storage backend for persistent cloud database.

Replaces TinyDB's ephemeral /tmp/ storage on Vercel with a persistent
MongoDB Atlas database. Implements the same BaseStorage interface.

Setup:
    1. Create free cluster at https://cloud.mongodb.com
    2. Get connection string (Database → Connect → Drivers → Python)
    3. Set MONGODB_URI env var in Vercel dashboard:
       MONGODB_URI=mongodb+srv://user:pass@cluster.xxxxx.mongodb.net/story_creator?retryWrites=true&w=majority
"""

from typing import Dict, Any, List, Optional
import logging
import os

logger = logging.getLogger(__name__)

# Lazy import pymongo to avoid import errors when not using MongoDB
_pymongo = None
_mongo_client_class = None


def _ensure_pymongo():
    """Lazy-load pymongo module."""
    global _pymongo, _mongo_client_class
    if _pymongo is None:
        import pymongo
        _pymongo = pymongo
        _mongo_client_class = pymongo.MongoClient
    return _pymongo


class MongoStorage:
    """
    MongoDB Atlas storage backend for Story Creator.

    Provides persistent cloud storage that survives Vercel cold starts.
    Implements the same interface as NoSQLStorage (TinyDB).

    Collections: worlds, stories, locations, entities, time_cones,
                 events, event_analysis_cache, users
    """

    def __init__(self, mongodb_uri: Optional[str] = None, db_name: str = "story_creator"):
        """
        Initialize MongoDB storage.

        Args:
            mongodb_uri: MongoDB connection string (defaults to MONGODB_URI env var)
            db_name: Database name (default: story_creator)
        """
        _ensure_pymongo()

        self.uri = mongodb_uri or os.environ.get('MONGODB_URI')
        if not self.uri:
            raise ValueError(
                "MongoDB URI not provided. Set MONGODB_URI environment variable.\n"
                "Example: mongodb+srv://user:pass@cluster.xxxxx.mongodb.net/story_creator"
            )

        # Connect with sensible defaults for serverless
        self.client = _mongo_client_class(
            self.uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=10000,
            maxPoolSize=10,
            retryWrites=True
        )

        self.db = self.client[db_name]

        # Collection references
        self.worlds = self.db['worlds']
        self.stories = self.db['stories']
        self.locations = self.db['locations']
        self.entities = self.db['entities']
        self.time_cones = self.db['time_cones']
        self.events = self.db['events']
        self.event_analysis_cache = self.db['event_analysis_cache']
        self.users = self.db['users']

        # Create indexes for fast lookups
        self._ensure_indexes()

        logger.info(f"MongoStorage initialized: {db_name}")

    def _ensure_indexes(self):
        """Create indexes for efficient queries."""
        try:
            self.worlds.create_index('world_id', unique=True)
            self.stories.create_index('story_id', unique=True)
            self.stories.create_index('world_id')
            self.locations.create_index('location_id', unique=True)
            self.locations.create_index('world_id')
            self.entities.create_index('entity_id', unique=True)
            self.entities.create_index('world_id')
            self.time_cones.create_index('time_cone_id', unique=True)
            self.time_cones.create_index('world_id')
            self.events.create_index('event_id', unique=True)
            self.events.create_index('world_id')
            self.events.create_index('story_id')
            self.event_analysis_cache.create_index('story_id')
            self.event_analysis_cache.create_index(
                [('story_id', 1), ('story_content_hash', 1)]
            )
            self.users.create_index('user_id', unique=True)
            self.users.create_index('username', unique=True)
            self.users.create_index('email', unique=True, sparse=True)
        except Exception as e:
            logger.warning(f"Index creation warning (may already exist): {e}")

    @staticmethod
    def _clean_doc(doc: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Remove MongoDB's internal _id field from a document."""
        if doc and '_id' in doc:
            doc = dict(doc)
            del doc['_id']
        return doc

    @staticmethod
    def _clean_docs(docs: List[Dict]) -> List[Dict[str, Any]]:
        """Remove MongoDB's internal _id field from multiple documents."""
        return [MongoStorage._clean_doc(dict(d)) for d in docs]

    # ==================== World Methods ====================

    def save_world(self, world_data: Dict[str, Any]) -> str:
        """Save a world (upsert)."""
        world_id = world_data['world_id']
        self.worlds.replace_one(
            {'world_id': world_id},
            world_data,
            upsert=True
        )
        logger.info(f"Saved world: {world_data.get('name', 'Unknown')}")
        return world_id

    def load_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        """Load a world by ID."""
        doc = self.worlds.find_one({'world_id': world_id})
        return self._clean_doc(doc)

    def list_worlds(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all worlds visible to the user."""
        from services.permission_service import PermissionService

        all_worlds = self._clean_docs(list(self.worlds.find()))

        if user_id is None:
            return [w for w in all_worlds if w.get('visibility') == 'public']

        return PermissionService.filter_viewable(user_id, all_worlds)

    def delete_world(self, world_id: str) -> bool:
        """Delete a world."""
        result = self.worlds.delete_one({'world_id': world_id})
        return result.deleted_count > 0

    # ==================== Story Methods ====================

    def save_story(self, story_data: Dict[str, Any]) -> str:
        """Save a story (upsert)."""
        story_id = story_data['story_id']
        self.stories.replace_one(
            {'story_id': story_id},
            story_data,
            upsert=True
        )
        return story_id

    def load_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Load a story by ID."""
        doc = self.stories.find_one({'story_id': story_id})
        return self._clean_doc(doc)

    def list_stories(self, world_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List stories, optionally filtered by world."""
        from services.permission_service import PermissionService

        query = {'world_id': world_id} if world_id else {}
        stories = self._clean_docs(list(self.stories.find(query)))

        if user_id is None:
            return [s for s in stories if s.get('visibility') == 'public']

        return PermissionService.filter_viewable(user_id, stories)

    def delete_story(self, story_id: str) -> bool:
        """Delete a story."""
        result = self.stories.delete_one({'story_id': story_id})
        return result.deleted_count > 0

    # ==================== Location Methods ====================

    def save_location(self, location_data: Dict[str, Any]) -> str:
        """Save a location (upsert)."""
        location_id = location_data['location_id']
        self.locations.replace_one(
            {'location_id': location_id},
            location_data,
            upsert=True
        )
        return location_id

    def load_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Load a location by ID."""
        doc = self.locations.find_one({'location_id': location_id})
        return self._clean_doc(doc)

    def list_locations(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List locations, optionally filtered by world."""
        query = {'world_id': world_id} if world_id else {}
        return self._clean_docs(list(self.locations.find(query)))

    def load_all_locations(self) -> List[Dict[str, Any]]:
        """Load all locations."""
        return self._clean_docs(list(self.locations.find()))

    def delete_location(self, location_id: str) -> bool:
        """Delete a location."""
        result = self.locations.delete_one({'location_id': location_id})
        return result.deleted_count > 0

    # ==================== Entity Methods ====================

    def save_entity(self, entity_data: Dict[str, Any]) -> str:
        """Save an entity (upsert)."""
        entity_id = entity_data['entity_id']
        self.entities.replace_one(
            {'entity_id': entity_id},
            entity_data,
            upsert=True
        )
        return entity_id

    def load_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Load an entity by ID."""
        doc = self.entities.find_one({'entity_id': entity_id})
        return self._clean_doc(doc)

    def list_entities(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List entities, optionally filtered by world."""
        query = {'world_id': world_id} if world_id else {}
        return self._clean_docs(list(self.entities.find(query)))

    def load_all_entities(self) -> List[Dict[str, Any]]:
        """Load all entities."""
        return self._clean_docs(list(self.entities.find()))

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity."""
        result = self.entities.delete_one({'entity_id': entity_id})
        return result.deleted_count > 0

    # ==================== Time Cone Methods ====================

    def save_time_cone(self, time_cone_data: Dict[str, Any]) -> str:
        """Save a time cone (upsert)."""
        time_cone_id = time_cone_data['time_cone_id']
        self.time_cones.replace_one(
            {'time_cone_id': time_cone_id},
            time_cone_data,
            upsert=True
        )
        return time_cone_id

    def load_time_cone(self, time_cone_id: str) -> Optional[Dict[str, Any]]:
        """Load a time cone by ID."""
        doc = self.time_cones.find_one({'time_cone_id': time_cone_id})
        return self._clean_doc(doc)

    def list_time_cones(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List time cones, optionally filtered by world."""
        query = {'world_id': world_id} if world_id else {}
        return self._clean_docs(list(self.time_cones.find(query)))

    # ==================== Event Methods ====================

    def save_event(self, event_data: Dict[str, Any]) -> str:
        """Save an event (upsert)."""
        event_id = event_data['event_id']
        self.events.replace_one(
            {'event_id': event_id},
            event_data,
            upsert=True
        )
        logger.info(f"Saved event: {event_data.get('title', 'Unknown')}")
        return event_id

    def load_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Load an event by ID."""
        doc = self.events.find_one({'event_id': event_id})
        return self._clean_doc(doc)

    def list_events_by_world(self, world_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all events for a world visible to the user."""
        from services.permission_service import PermissionService

        events = self._clean_docs(list(self.events.find({'world_id': world_id})))

        if user_id is None:
            return [e for e in events if e.get('visibility') == 'public']

        return PermissionService.filter_viewable(user_id, events)

    def list_events_by_story(self, story_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all events for a story visible to the user."""
        from services.permission_service import PermissionService

        events = self._clean_docs(list(self.events.find({'story_id': story_id})))

        if user_id is None:
            return [e for e in events if e.get('visibility') == 'public']

        return PermissionService.filter_viewable(user_id, events)

    def update_event(self, event_id: str, data: Dict[str, Any]) -> bool:
        """Update an event (merge fields)."""
        result = self.events.update_one(
            {'event_id': event_id},
            {'$set': data}
        )
        return result.matched_count > 0

    def delete_event(self, event_id: str) -> bool:
        """Delete an event."""
        result = self.events.delete_one({'event_id': event_id})
        return result.deleted_count > 0

    def delete_events_by_story(self, story_id: str) -> int:
        """Delete all events for a story."""
        result = self.events.delete_many({'story_id': story_id})
        return result.deleted_count

    # ==================== Event Analysis Cache ====================

    def save_analysis_cache(self, story_id: str, content_hash: str,
                            gpt_response: Dict[str, Any], model: str) -> str:
        """Save GPT analysis cache for a story."""
        import uuid as _uuid
        from datetime import datetime as _dt

        cache_id = str(_uuid.uuid4())

        # Remove old cache for this story
        self.event_analysis_cache.delete_many({'story_id': story_id})

        cache_data = {
            "cache_id": cache_id,
            "story_id": story_id,
            "story_content_hash": content_hash,
            "raw_gpt_response": gpt_response,
            "extracted_events_count": len(gpt_response.get('events', [])),
            "analyzed_at": _dt.now().isoformat(),
            "model_used": model
        }

        self.event_analysis_cache.insert_one(cache_data)
        logger.info(f"Cached analysis for story {story_id} (hash: {content_hash[:12]}...)")
        return cache_id

    def get_analysis_cache(self, story_id: str, content_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached GPT analysis by story ID and content hash."""
        doc = self.event_analysis_cache.find_one({
            'story_id': story_id,
            'story_content_hash': content_hash
        })
        if doc:
            logger.info(f"Cache HIT for story {story_id}")
            return self._clean_doc(doc)
        logger.info(f"Cache MISS for story {story_id}")
        return None

    def delete_analysis_cache(self, story_id: str) -> bool:
        """Delete GPT analysis cache for a story."""
        result = self.event_analysis_cache.delete_many({'story_id': story_id})
        return result.deleted_count > 0

    # ==================== User Management ====================

    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """Save or update a user."""
        user_id = user_data.get('user_id')
        if not user_id:
            logger.error("Cannot save user: missing user_id")
            return False

        self.users.replace_one(
            {'user_id': user_id},
            user_data,
            upsert=True
        )
        logger.info(f"Saved user: {user_id}")
        return True

    def load_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load a user by user_id."""
        doc = self.users.find_one({'user_id': user_id})
        return self._clean_doc(doc)

    def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find a user by username."""
        doc = self.users.find_one({'username': username})
        return self._clean_doc(doc)

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by email."""
        doc = self.users.find_one({'email': email})
        return self._clean_doc(doc)

    def list_users(self) -> List[Dict[str, Any]]:
        """List all users."""
        return self._clean_docs(list(self.users.find()))

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        result = self.users.delete_one({'user_id': user_id})
        return result.deleted_count > 0

    # ==================== Utility Methods ====================

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        return {
            "worlds": self.worlds.count_documents({}),
            "stories": self.stories.count_documents({}),
            "locations": self.locations.count_documents({}),
            "entities": self.entities.count_documents({}),
            "time_cones": self.time_cones.count_documents({}),
            "events": self.events.count_documents({}),
            "event_analysis_cache": self.event_analysis_cache.count_documents({})
        }

    def close(self) -> None:
        """Close the MongoDB connection."""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

    def flush(self) -> None:
        """No-op for MongoDB (writes are immediate)."""
        pass

    def clear_all(self) -> None:
        """
        Clear all data (for testing ONLY).

        WARNING: This will DELETE ALL DATA.
        """
        import os
        if 'PYTEST_CURRENT_TEST' not in os.environ and 'TEST_MODE' not in os.environ:
            logger.error("CRITICAL: Attempted to clear database outside of test environment!")
            raise RuntimeError("clear_all() can only be called in test environment.")

        logger.warning("⚠️  CLEARING ALL MONGODB DATA (test mode)")
        self.worlds.delete_many({})
        self.stories.delete_many({})
        self.locations.delete_many({})
        self.entities.delete_many({})
        self.time_cones.delete_many({})
        self.events.delete_many({})
        self.event_analysis_cache.delete_many({})
        self.users.delete_many({})
