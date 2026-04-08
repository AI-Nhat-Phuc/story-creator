"""Environment-aware database configuration."""

import os
import logging

logger = logging.getLogger(__name__)

_VALID_ENVS = {"production", "staging", "development"}
_SUFFIXES = {"production": "_prod", "staging": "_staging", "development": ""}


def get_mongo_db_name() -> str:
    """Return MongoDB database name based on APP_ENV.

    APP_ENV=production  → story_creator_prod
    APP_ENV=staging     → story_creator_staging
    APP_ENV=*           → story_creator_dev  (default)
    """
    env = os.environ.get("APP_ENV", "development").lower()
    if env not in _VALID_ENVS:
        logger.warning("Invalid APP_ENV=%r, falling back to 'development'", env)
        env = "development"

    suffix = _SUFFIXES[env]
    return f"story_creator{suffix or '_dev'}"


def get_mongo_uri() -> str:
    """Return MONGODB_URI environment variable or raise RuntimeError if missing."""
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise RuntimeError(
            "MONGODB_URI environment variable is required. "
            "Set it in your .env file or Vercel dashboard.\n"
            "Example: mongodb+srv://user:pass@cluster.xxxxx.mongodb.net/story_creator"
        )
    return uri
