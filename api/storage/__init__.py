"""Storage backends for story creator."""

from .base_storage import BaseStorage
from .nosql_storage import NoSQLStorage
from .json_storage import Storage as JSONStorage

try:
    from .mongo_storage import MongoStorage
except ImportError:
    MongoStorage = None

__all__ = ['BaseStorage', 'NoSQLStorage', 'JSONStorage', 'MongoStorage']
