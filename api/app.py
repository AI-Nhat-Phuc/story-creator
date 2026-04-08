import os
import sys

# Ensure api/ is on sys.path for both Vercel and local dev
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interfaces.api_backend import APIBackend
from utils.env_config import get_mongo_uri, get_mongo_db_name

api = APIBackend(mongodb_uri=get_mongo_uri(), mongo_db_name=get_mongo_db_name())
app = api.app  # Expose Flask app for Vercel/WSGI/ASGI
