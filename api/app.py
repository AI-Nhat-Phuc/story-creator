import os
from interfaces.api_backend import APIBackend

# Use /tmp for db_path if running on Vercel
db_path = os.environ.get("STORY_DB_PATH") or "/tmp/story_creator.db" if os.environ.get("VERCEL") else "story_creator.db"
api = APIBackend(db_path=db_path)
app = api.app  # Expose Flask app for Vercel/WSGI/ASGI
