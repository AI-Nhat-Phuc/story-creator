import os
import sys

# Ensure api/ is on sys.path for both Vercel and local dev
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interfaces.api_backend import APIBackend

# Separate db per environment (APP_ENV=production|staging|development)
_env = os.environ.get("APP_ENV", "development").lower()
_env_suffix = {"production": "_prod", "staging": "_staging"}.get(_env, "")
_is_vercel = os.environ.get("VERCEL")
_default_db = f"/tmp/story_creator{_env_suffix}.db" if _is_vercel else f"story_creator{_env_suffix}.db"
db_path = os.environ.get("STORY_DB_PATH", _default_db)
mongo_db_name = f"story_creator{_env_suffix}" if _env_suffix else "story_creator_dev"
api = APIBackend(db_path=db_path, mongo_db_name=mongo_db_name)
app = api.app  # Expose Flask app for Vercel/WSGI/ASGI
