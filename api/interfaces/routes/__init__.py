"""API route blueprints for Story Creator."""

from .health_routes import create_health_bp
from .world_routes import create_world_bp
from .story_routes import create_story_bp
from .gpt_routes import create_gpt_bp
from .stats_routes import create_stats_bp
from .event_routes import create_event_bp
from .auth_routes import create_auth_bp
from .admin_routes import create_admin_bp

__all__ = [
    'create_health_bp',
    'create_world_bp',
    'create_story_bp',
    'create_gpt_bp',
    'create_stats_bp',
    'create_event_bp',
    'create_auth_bp',
    'create_admin_bp'
]
