import os
import sys

# Ensure api/ is on sys.path for both Vercel and local dev
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interfaces.api_backend import APIBackend

# Use /tmp for db_path if running on Vercel (read-only filesystem)
db_path = os.environ.get("STORY_DB_PATH", "/tmp/story_creator.db" if os.environ.get("VERCEL") else "story_creator.db")
api = APIBackend(db_path=db_path)
app = api.app  # Expose Flask app for Vercel/WSGI/ASGI
