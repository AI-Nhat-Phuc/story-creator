"""Environment-aware database configuration."""

import os
import logging

logger = logging.getLogger(__name__)

_VALID_ENVS = {"production", "staging", "development"}
_SUFFIXES = {"production": "_prod", "staging": "_staging", "development": ""}


def get_db_config() -> tuple:
    """
    Return (db_path, mongo_db_name) based on APP_ENV.

    APP_ENV=production  → story_creator_prod.db   / story_creator_prod
    APP_ENV=staging     → story_creator_staging.db / story_creator_staging
    APP_ENV=*           → story_creator.db          / story_creator_dev  (default)

    STORY_DB_PATH overrides db_path.
    VERCEL=1 adds /tmp/ prefix.
    """
    env = os.environ.get("APP_ENV", "development").lower()
    if env not in _VALID_ENVS:
        logger.warning("Invalid APP_ENV=%r, falling back to 'development'", env)
        env = "development"

    suffix = _SUFFIXES[env]
    is_vercel = os.environ.get("VERCEL")
    default_db = f"/tmp/story_creator{suffix}.db" if is_vercel else f"story_creator{suffix}.db"
    db_path = os.environ.get("STORY_DB_PATH", default_db)
    mongo_db_name = f"story_creator{suffix}" if suffix else "story_creator_dev"
    return db_path, mongo_db_name
