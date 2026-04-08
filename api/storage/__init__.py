"""Storage backends for story creator."""

from .base_storage import BaseStorage
from .mongo_storage import MongoStorage

__all__ = ['BaseStorage', 'MongoStorage']
