"""Validation schemas for request validation."""

from .world_schemas import (
    CreateWorldSchema,
    UpdateWorldSchema,
    ListWorldsQuerySchema
)

from .story_schemas import (
    CreateStorySchema,
    UpdateStorySchema,
    ListStoriesQuerySchema
)

from .auth_schemas import (
    RegisterSchema,
    LoginSchema,
    GoogleAuthSchema,
    FacebookAuthSchema
)

__all__ = [
    # World schemas
    'CreateWorldSchema',
    'UpdateWorldSchema',
    'ListWorldsQuerySchema',
    # Story schemas
    'CreateStorySchema',
    'UpdateStorySchema',
    'ListStoriesQuerySchema',
    # Auth schemas
    'RegisterSchema',
    'LoginSchema',
    'GoogleAuthSchema',
    'FacebookAuthSchema',
]
