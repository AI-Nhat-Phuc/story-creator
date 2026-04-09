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


def get_db_config() -> tuple:
    """Return (db_path, mongo_db_name) based on APP_ENV and runtime context.

    Rules:
    - STORY_DB_PATH env var overrides db_path (any APP_ENV)
    - VERCEL env var present → db_path prefix is /tmp/
    - APP_ENV=production  → *_prod.db  / story_creator_prod
    - APP_ENV=staging     → *_staging.db / story_creator_staging
    - APP_ENV=development (default) → story_creator.db / story_creator_dev
    """
    env = os.environ.get("APP_ENV", "development").lower()
    if env not in _VALID_ENVS:
        logger.warning("Invalid APP_ENV=%r, falling back to 'development'", env)
        env = "development"

    mongo_db_name = get_mongo_db_name()

    # Determine TinyDB file path
    if env == "development":
        default_path = "story_creator.db"
    else:
        suffix = _SUFFIXES[env]  # "_prod" or "_staging"
        filename = f"story_creator{suffix}.db"
        if os.environ.get("VERCEL"):
            default_path = f"/tmp/{filename}"
        else:
            default_path = filename

    db_path = os.environ.get("STORY_DB_PATH") or default_path
    return db_path, mongo_db_name
