"""MongoDB Atlas storage backend for persistent cloud database.

Implements the BaseStorage interface with lazy connection — the MongoClient
is created on the first actual database operation, not at construction time.
This eliminates network I/O during Vercel cold start.

Setup:
    1. Create free cluster at https://cloud.mongodb.com
    2. Get connection string (Database → Connect → Drivers → Python)
    3. Set MONGODB_URI env var in Vercel dashboard:
       MONGODB_URI=mongodb+srv://user:pass@cluster.xxxxx.mongodb.net/story_creator?retryWrites=true&w=majority
"""

from typing import Dict, Any, List, Optional
import logging
import threading

logger = logging.getLogger(__name__)

# Lazy import pymongo — loaded only on first DB operation
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
    Connection is deferred until the first database operation (lazy connect).

    Collections: worlds, stories, locations, entities, time_cones,
                 events, event_analysis_cache, users, gpt_tasks
    """

    def __init__(self, mongodb_uri: str, db_name: str = "story_creator_dev"):
        """
        Store connection config. Does NOT open a network connection.

        Args:
            mongodb_uri: MongoDB connection string
            db_name: Database name
        """
        if not mongodb_uri:
            raise ValueError(
                "MongoDB URI not provided. Set MONGODB_URI environment variable.\n"
                "Example: mongodb+srv://user:pass@cluster.xxxxx.mongodb.net/story_creator"
            )
        self.uri = mongodb_uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self._lock = threading.Lock()
        # Collection references — set by _connect()
        self.worlds = None
        self.stories = None
        self.locations = None
        self.entities = None
        self.time_cones = None
        self.events = None
        self.event_analysis_cache = None
        self.users = None
        self.gpt_tasks = None

    def _connect(self) -> None:
        """Open MongoDB connection on first use. Thread-safe, runs at most once."""
        if self.db is not None:
            return
        with self._lock:
            if self.db is not None:
                return
            if self.uri.startswith('mongomock://'):
                # In-memory mock for local dev / testing — no network required
                import mongomock
                self.client = mongomock.MongoClient()
            else:
                _ensure_pymongo()
                self.client = _mongo_client_class(
                    self.uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=10000,
                    maxPoolSize=10,
                    retryWrites=True
                )
            self.db = self.client[self.db_name]
            self.worlds = self.db['worlds']
            self.stories = self.db['stories']
            self.locations = self.db['locations']
            self.entities = self.db['entities']
            self.time_cones = self.db['time_cones']
            self.events = self.db['events']
            self.event_analysis_cache = self.db['event_analysis_cache']
            self.users = self.db['users']
            self.gpt_tasks = self.db['gpt_tasks']
            self._ensure_indexes()
            logger.info(f"MongoStorage connected: {self.db_name}")

    def _ensure_indexes(self):
        """Create indexes for efficient queries."""
        try:
            self.worlds.create_index('world_id', unique=True)
            self.worlds.create_index([('visibility', 1), ('owner_id', 1)])
            self.worlds.create_index('shared_with')
            self.stories.create_index('story_id', unique=True)
            self.stories.create_index('world_id')
            self.stories.create_index([('visibility', 1), ('owner_id', 1)])
            self.stories.create_index('shared_with')
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
            self.gpt_tasks.create_index('task_id', unique=True)
            self.gpt_tasks.create_index('created_at')
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
        self._connect()
        world_id = world_data['world_id']
        self.worlds.replace_one({'world_id': world_id}, world_data, upsert=True)
        logger.info(f"Saved world: {world_data.get('name', 'Unknown')}")
        return world_id

    def load_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        self._connect()
        doc = self.worlds.find_one({'world_id': world_id})
        return self._clean_doc(doc)

    def _build_permission_query(self, user_id: Optional[str] = None) -> dict:
        if user_id is None:
            return {'visibility': 'public'}
        return {'$or': [
            {'visibility': 'public'},
            {'owner_id': user_id},
            {'shared_with': user_id}
        ]}

    def list_worlds(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        self._connect()
        query = self._build_permission_query(user_id)
        return self._clean_docs(list(self.worlds.find(query)))

    def list_worlds_summary(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        self._connect()
        query = self._build_permission_query(user_id)
        projection = {
            '_id': 0, 'world_id': 1, 'name': 1, 'created_at': 1,
            'visibility': 1, 'owner_id': 1, 'shared_with': 1, 'world_type': 1
        }
        return list(self.worlds.find(query, projection))

    def count_visible(self, collection_name: str, user_id: Optional[str] = None) -> dict:
        self._connect()
        coll = getattr(self, collection_name)
        public_count = coll.count_documents({'visibility': 'public'})
        if user_id is None:
            return {'total': public_count, 'public': public_count}
        private_count = coll.count_documents({'visibility': 'private', 'owner_id': user_id})
        shared_count = coll.count_documents({
            'visibility': 'private',
            'owner_id': {'$ne': user_id},
            'shared_with': user_id
        })
        return {
            'total': public_count + private_count + shared_count,
            'public': public_count,
            'private': private_count,
            'shared': shared_count
        }

    def delete_world(self, world_id: str) -> bool:
        self._connect()
        result = self.worlds.delete_one({'world_id': world_id})
        return result.deleted_count > 0

    # ==================== Story Methods ====================

    def save_story(self, story_data: Dict[str, Any]) -> str:
        self._connect()
        story_id = story_data['story_id']
        self.stories.replace_one({'story_id': story_id}, story_data, upsert=True)
        return story_id

    def load_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        self._connect()
        doc = self.stories.find_one({'story_id': story_id})
        return self._clean_doc(doc)

    def list_stories(self, world_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        self._connect()
        perm_query = self._build_permission_query(user_id)
        if world_id:
            query = {'$and': [{'world_id': world_id}, perm_query]}
        else:
            query = perm_query
        return self._clean_docs(list(self.stories.find(query)))

    def delete_story(self, story_id: str) -> bool:
        self._connect()
        result = self.stories.delete_one({'story_id': story_id})
        return result.deleted_count > 0

    # ==================== Location Methods ====================

    def save_location(self, location_data: Dict[str, Any]) -> str:
        self._connect()
        location_id = location_data['location_id']
        self.locations.replace_one({'location_id': location_id}, location_data, upsert=True)
        return location_id

    def load_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        self._connect()
        doc = self.locations.find_one({'location_id': location_id})
        return self._clean_doc(doc)

    def list_locations(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        self._connect()
        query = {'world_id': world_id} if world_id else {}
        return self._clean_docs(list(self.locations.find(query)))

    def load_all_locations(self) -> List[Dict[str, Any]]:
        self._connect()
        return self._clean_docs(list(self.locations.find()))

    def delete_location(self, location_id: str) -> bool:
        self._connect()
        result = self.locations.delete_one({'location_id': location_id})
        return result.deleted_count > 0

    # ==================== Entity Methods ====================

    def save_entity(self, entity_data: Dict[str, Any]) -> str:
        self._connect()
        entity_id = entity_data['entity_id']
        self.entities.replace_one({'entity_id': entity_id}, entity_data, upsert=True)
        return entity_id

    def load_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        self._connect()
        doc = self.entities.find_one({'entity_id': entity_id})
        return self._clean_doc(doc)

    def list_entities(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        self._connect()
        query = {'world_id': world_id} if world_id else {}
        return self._clean_docs(list(self.entities.find(query)))

    def load_all_entities(self) -> List[Dict[str, Any]]:
        self._connect()
        return self._clean_docs(list(self.entities.find()))

    def delete_entity(self, entity_id: str) -> bool:
        self._connect()
        result = self.entities.delete_one({'entity_id': entity_id})
        return result.deleted_count > 0

    # ==================== Time Cone Methods ====================

    def save_time_cone(self, time_cone_data: Dict[str, Any]) -> str:
        self._connect()
        time_cone_id = time_cone_data['time_cone_id']
        self.time_cones.replace_one({'time_cone_id': time_cone_id}, time_cone_data, upsert=True)
        return time_cone_id

    def load_time_cone(self, time_cone_id: str) -> Optional[Dict[str, Any]]:
        self._connect()
        doc = self.time_cones.find_one({'time_cone_id': time_cone_id})
        return self._clean_doc(doc)

    def list_time_cones(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        self._connect()
        query = {'world_id': world_id} if world_id else {}
        return self._clean_docs(list(self.time_cones.find(query)))

    # ==================== Event Methods ====================

    def save_event(self, event_data: Dict[str, Any]) -> str:
        self._connect()
        event_id = event_data['event_id']
        self.events.replace_one({'event_id': event_id}, event_data, upsert=True)
        logger.info(f"Saved event: {event_data.get('title', 'Unknown')}")
        return event_id

    def load_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        self._connect()
        doc = self.events.find_one({'event_id': event_id})
        return self._clean_doc(doc)

    def list_events_by_world(self, world_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        self._connect()
        from services.permission_service import PermissionService
        events = self._clean_docs(list(self.events.find({'world_id': world_id})))
        if user_id is None:
            return [e for e in events if e.get('visibility') == 'public']
        return PermissionService.filter_viewable(user_id, events)

    def list_events_by_story(self, story_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        self._connect()
        from services.permission_service import PermissionService
        events = self._clean_docs(list(self.events.find({'story_id': story_id})))
        if user_id is None:
            return [e for e in events if e.get('visibility') == 'public']
        return PermissionService.filter_viewable(user_id, events)

    def update_event(self, event_id: str, data: Dict[str, Any]) -> bool:
        self._connect()
        result = self.events.update_one({'event_id': event_id}, {'$set': data})
        return result.matched_count > 0

    def delete_event(self, event_id: str) -> bool:
        self._connect()
        result = self.events.delete_one({'event_id': event_id})
        return result.deleted_count > 0

    def delete_events_by_story(self, story_id: str) -> int:
        self._connect()
        result = self.events.delete_many({'story_id': story_id})
        return result.deleted_count

    # ==================== Event Analysis Cache ====================

    def save_analysis_cache(self, story_id: str, content_hash: str,
                            gpt_response: Dict[str, Any], model: str) -> str:
        self._connect()
        import uuid as _uuid
        from datetime import datetime as _dt
        cache_id = str(_uuid.uuid4())
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
        self._connect()
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
        self._connect()
        result = self.event_analysis_cache.delete_many({'story_id': story_id})
        return result.deleted_count > 0

    # ==================== User Management ====================

    def save_user(self, user_data: Dict[str, Any]) -> bool:
        self._connect()
        user_id = user_data.get('user_id')
        if not user_id:
            logger.error("Cannot save user: missing user_id")
            return False
        self.users.replace_one({'user_id': user_id}, user_data, upsert=True)
        logger.info(f"Saved user: {user_id}")
        return True

    def load_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        self._connect()
        doc = self.users.find_one({'user_id': user_id})
        return self._clean_doc(doc)

    def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        self._connect()
        doc = self.users.find_one({'username': username})
        return self._clean_doc(doc)

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        self._connect()
        doc = self.users.find_one({'email': email})
        return self._clean_doc(doc)

    def list_users(self) -> List[Dict[str, Any]]:
        self._connect()
        return self._clean_docs(list(self.users.find()))

    def delete_user(self, user_id: str) -> bool:
        self._connect()
        result = self.users.delete_one({'user_id': user_id})
        return result.deleted_count > 0

    # ==================== Utility Methods ====================

    def get_stats(self) -> Dict[str, int]:
        self._connect()
        return {
            "worlds": self.worlds.estimated_document_count(),
            "stories": self.stories.estimated_document_count(),
            "locations": self.locations.estimated_document_count(),
            "entities": self.entities.estimated_document_count(),
            "time_cones": self.time_cones.estimated_document_count(),
            "events": self.events.estimated_document_count(),
            "event_analysis_cache": self.event_analysis_cache.estimated_document_count()
        }

    def get_dashboard_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        self._connect()

        def _build_faceted_count_pipeline(user_id):
            facets = {
                'public': [{'$match': {'visibility': 'public'}}, {'$count': 'n'}]
            }
            if user_id:
                facets['private'] = [
                    {'$match': {'visibility': 'private', 'owner_id': user_id}},
                    {'$count': 'n'}
                ]
                facets['shared'] = [
                    {'$match': {
                        'visibility': 'private',
                        'owner_id': {'$ne': user_id},
                        'shared_with': user_id
                    }},
                    {'$count': 'n'}
                ]
            return [{'$facet': facets}]

        def _parse_facet_result(result):
            row = result[0] if result else {}
            public = row.get('public', [{}])[0].get('n', 0) if row.get('public') else 0
            private = row.get('private', [{}])[0].get('n', 0) if row.get('private') else 0
            shared = row.get('shared', [{}])[0].get('n', 0) if row.get('shared') else 0
            counts = {'total': public + private + shared, 'public': public}
            if 'private' in row:
                counts['private'] = private
                counts['shared'] = shared
            return counts

        pipeline = _build_faceted_count_pipeline(user_id)
        worlds_counts = _parse_facet_result(list(self.worlds.aggregate(pipeline)))
        stories_counts = _parse_facet_result(list(self.stories.aggregate(pipeline)))
        perm_query = self._build_permission_query(user_id)
        projection = {
            '_id': 0, 'world_id': 1, 'name': 1, 'created_at': 1,
            'visibility': 1, 'owner_id': 1, 'shared_with': 1, 'world_type': 1
        }
        worlds_summary = list(self.worlds.find(perm_query, projection))
        return {
            'worlds_counts': worlds_counts,
            'stories_counts': stories_counts,
            'entity_count': self.entities.estimated_document_count(),
            'location_count': self.locations.estimated_document_count(),
            'worlds_summary': worlds_summary
        }

    # ==================== GPT Task Methods ====================

    def save_gpt_task(self, task_data: Dict[str, Any]) -> str:
        self._connect()
        task_id = task_data['task_id']
        self.gpt_tasks.replace_one({'task_id': task_id}, task_data, upsert=True)
        return task_id

    def load_gpt_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        self._connect()
        doc = self.gpt_tasks.find_one({'task_id': task_id})
        return self._clean_doc(doc)

    def update_gpt_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        self._connect()
        result = self.gpt_tasks.update_one(
            {'task_id': task_id},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def list_pending_gpt_tasks(self) -> List[Dict[str, Any]]:
        self._connect()
        return self._clean_docs(list(self.gpt_tasks.find(
            {'status': {'$in': ['pending', 'processing']}}
        )))

    def cleanup_old_gpt_tasks(self, max_age_hours: int = 24) -> int:
        self._connect()
        from datetime import datetime, timedelta
        cutoff = (datetime.utcnow() - timedelta(hours=max_age_hours)).isoformat()
        result = self.gpt_tasks.delete_many({'created_at': {'$lt': cutoff}})
        return result.deleted_count

    def close(self) -> None:
        """Close the MongoDB connection."""
        try:
            if self.client is not None:
                self.client.close()
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

    def flush(self) -> None:
        """No-op for MongoDB (writes are immediate)."""
        pass

    def clear_all(self) -> None:
        """Clear all data (for testing ONLY)."""
        import os
        if 'PYTEST_CURRENT_TEST' not in os.environ and 'TEST_MODE' not in os.environ:
            logger.error("CRITICAL: Attempted to clear database outside of test environment!")
            raise RuntimeError("clear_all() can only be called in test environment.")
        self._connect()
        logger.warning("⚠️  CLEARING ALL MONGODB DATA (test mode)")
        self.worlds.delete_many({})
        self.stories.delete_many({})
        self.locations.delete_many({})
        self.entities.delete_many({})
        self.time_cones.delete_many({})
        self.events.delete_many({})
        self.event_analysis_cache.delete_many({})
        self.users.delete_many({})
        self.gpt_tasks.delete_many({})
