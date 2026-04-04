import os
import sys

# Ensure api/ is on sys.path for both Vercel and local dev
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interfaces.api_backend import APIBackend
from utils.env_config import get_db_config

db_path, mongo_db_name = get_db_config()
api = APIBackend(db_path=db_path, mongo_db_name=mongo_db_name)
app = api.app  # Expose Flask app for Vercel/WSGI/ASGI
