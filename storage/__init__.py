"""Storage backends for story creator."""

from .base_storage import BaseStorage
from .nosql_storage import NoSQLStorage
from .json_storage import Storage as JSONStorage

__all__ = ['BaseStorage', 'NoSQLStorage', 'JSONStorage']
