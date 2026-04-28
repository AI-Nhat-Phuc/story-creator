"""Story routes for the API backend."""

import uuid as _uuid
from datetime import datetime
from flask import Blueprint, request, g
from core.models.world import World
from core.models.entity import Entity
from core.models.location import Location
from core.models.user import User
from core.exceptions import (
    ResourceNotFoundError,
    PermissionDeniedError,
    QuotaExceededError,
    BusinessRuleError,
    ConflictError
)
from services import CharacterService, PermissionService, NovelService
from interfaces.auth_middleware import token_required, optional_auth
from utils.responses import success_response, created_response, deleted_response
from utils.i18n import t
from utils.validation import validate_request, validate_query_params, extract_pagination
from schemas.story_schemas import CreateStorySchema, UpdateStorySchema, ListStoriesQuerySchema, LinkEntitiesSchema


def create_story_bp(storage, story_generator, flush_data):
    """Create and configure the story blueprint.

    Args:
        storage: Storage instance for data persistence
        story_generator: StoryGenerator instance for story creation
        flush_data: Function to flush data to storage

    Returns:
        Blueprint: Configured Flask blueprint for story routes
    """
    story_bp = Blueprint('stories', __name__)

    @story_bp.route('/api/stories', methods=['GET'])
    @optional_auth
    @validate_query_params(ListStoriesQuerySchema)
    @extract_pagination(lambda: storage.list_stories(
        user_id=g.current_user.user_id if hasattr(g, 'current_user') else None
    ))
    def list_stories():
        """List all stories visible to current user.
        ---
        tags:
          - Stories
        parameters:
          - in: header
            name: Authorization
            type: string
            required: false
            description: "Bearer {token} (optional)"
          - in: query
            name: page
            type: integer
            default: 1
          - in: query
            name: per_page
            type: integer
            default: 20
        responses:
          200:
            description: List of stories (public + owned + shared)
        """
        pass

    @story_bp.route('/api/stories', methods=['POST'])
    @token_required
    @validate_request(CreateStorySchema)
    def create_story():
        """Create new story (requires authentication).
        ---
        tags:
          - Stories
        parameters:
          - in: header
            name: Authorization
            type: string
            required: true
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                world_id:
                  type: string
                  example: "world-uuid-123"
                title:
                  type: string
                  example: "Cuộc phiêu lưu của John"
                description:
                  type: string
                  example: "John khám phá khu rừng bí ẩn..."
                genre:
                  type: string
                  enum: [adventure, mystery, conflict, discovery]
                  example: adventure
                visibility:
                  type: string
                  enum: [draft, private, public]
                  default: private
                selected_characters:
                  type: array
                  items:
                    type: string
        responses:
          201:
            description: Story created successfully
          400:
            description: Invalid input or quota exceeded
          403:
            description: Permission denied (cannot create story in this world)
          404:
            description: World not found
        """
        data = request.validated_data
        world_id = data['world_id']

        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        world_visibility = world_data.get('visibility', 'private')
        visibility = data.get('visibility', world_visibility)

        if not PermissionService.can_view(g.current_user.user_id, world_data):
            raise PermissionDeniedError('create story in', 'this world')

        if visibility == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            if user_data:
                user = User.from_dict(user_data)
                if not user.can_create_public_story():
                    raise QuotaExceededError(
                        t('story.quota_exceeded'),
                        current_count=user.metadata.get('public_stories_count', 0),
                        limit=user.metadata.get('public_stories_limit', 20)
                    )

        title = data.get('title', t('story.untitled'))
        description = data.get('description', '')
        genre = data.get('genre', 'adventure')
        explicit_order = data.get('order')
        selected_characters = data.get('selected_characters', None)

        world = World.from_dict(world_data)

        linked_entities = _resolve_linked_entities(
            storage, world, world_id, selected_characters, description
        )

        story = story_generator.generate(
            title,
            description,
            world.world_id,
            genre,
            locations=None,
            entities=linked_entities if linked_entities else None
        )

        story.owner_id = g.current_user.user_id
        story.visibility = visibility
        story.format = data['format']

        # Auto-create an immutable author token on first save
        _user_data = storage.load_user(g.current_user.user_id) or {}
        _user_sig = _user_data.get('metadata', {}).get('signature') or g.current_user.username
        story.author_signature = {
            'token': str(_uuid.uuid4()),
            'display': _user_sig,
            'owner_id': g.current_user.user_id,
        }
        if data['content']:
            story.content = data['content']

        # Spec BR-15/BR-16 — assign `order` (explicit wins; otherwise max+1)
        if explicit_order is not None:
            story.order = explicit_order
        else:
            story.order = NovelService.assign_next_order(storage, world.world_id)

        storage.save_story(story.to_dict())
        world.add_story(story.story_id)
        storage.save_world(world.to_dict())

        if visibility == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            if user_data:
                user = User.from_dict(user_data)
                user.increment_public_stories()
                storage.save_user(user.to_dict())

        flush_data()

        return created_response(
            {'story_id': story.story_id, 'story': story.to_dict()},
            t('story.created')
        )

    @story_bp.route('/api/stories/my-draft', methods=['GET'])
    @token_required
    def get_my_draft():
        """Get the current user's draft story (if any).
        ---
        tags:
          - Stories
        parameters:
          - in: header
            name: Authorization
            type: string
            required: true
        responses:
          200:
            description: Draft story or null
          401:
            description: Unauthorized
        """
        drafts = _get_user_drafts(storage, g.current_user.user_id)
        story = drafts[0] if drafts else None
        return success_response({'story': story})

    @story_bp.route('/api/stories/<story_id>', methods=['GET'])
    @optional_auth
    def get_story_detail(story_id):
        """Get a specific story.
        ---
        tags:
          - Stories
        parameters:
          - name: story_id
            in: path
            type: string
            required: true
          - in: header
            name: Authorization
            type: string
            required: false
        responses:
          200:
            description: Story details
          403:
            description: Permission denied
          404:
            description: Story not found
        """
        story_data = storage.load_story(story_id)
        if not story_data:
            raise ResourceNotFoundError('Story', story_id)

        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        if not PermissionService.can_view(user_id, story_data):
            raise PermissionDeniedError('view', 'story')

        return success_response(story_data)

    @story_bp.route('/api/stories/<story_id>', methods=['PUT'])
    @token_required
    @validate_request(UpdateStorySchema)
    def update_story(story_id):
        """Update a specific story (owner only).
        ---
        tags:
          - Stories
        parameters:
          - name: story_id
            in: path
            type: string
            required: true
          - in: header
            name: Authorization
            type: string
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                title:
                  type: string
                content:
                  type: string
                visibility:
                  type: string
                  enum: [draft, private, public]
        responses:
          200:
            description: Story updated
          400:
            description: Quota exceeded
          403:
            description: Permission denied
          404:
            description: Story not found
        """
        story_data = storage.load_story(story_id)
        if not story_data:
            raise ResourceNotFoundError('Story', story_id)

        if not PermissionService.can_edit(g.current_user.user_id, story_data):
            raise PermissionDeniedError('edit', 'story')

        data = request.validated_data
        old_visibility = story_data.get('visibility', 'private')
        new_visibility = data.get('visibility', old_visibility)

        if old_visibility != new_visibility:
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data) if user_data else None

            if old_visibility != 'public' and new_visibility == 'public':
                if user and not user.can_create_public_story():
                    raise QuotaExceededError(
                        'Bạn đã đạt giới hạn số câu chuyện công khai',
                        current_count=user.metadata.get('public_stories_count', 0),
                        limit=user.metadata.get('public_stories_limit', 20)
                    )
                if user:
                    user.increment_public_stories()
                    storage.save_user(user.to_dict())

            elif old_visibility == 'public' and new_visibility != 'public':
                if user:
                    user.decrement_public_stories()
                    storage.save_user(user.to_dict())

            story_data['visibility'] = new_visibility

        for field in ['title', 'content', 'format']:
            if field in data:
                story_data[field] = data[field]

        story_data['updated_at'] = datetime.now().isoformat()
        storage.save_story(story_data)
        flush_data()

        return success_response(story_data, t('story.updated'))

    @story_bp.route('/api/stories/<story_id>', methods=['PATCH'])
    @token_required
    @validate_request(UpdateStorySchema)
    def patch_story(story_id):
        """Auto-save story content or update chapter number.
        ---
        tags:
          - Stories
        parameters:
          - name: story_id
            in: path
            type: string
            required: true
          - in: header
            name: Authorization
            type: string
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                content:
                  type: string
                chapter_number:
                  type: integer
                  minimum: 1
        responses:
          200:
            description: Story saved, returns story_id and updated_at
          403:
            description: Permission denied
          404:
            description: Story not found
        """
        story_data = storage.load_story(story_id)
        if not story_data:
            raise ResourceNotFoundError('Story', story_id)

        user_id = g.current_user.user_id
        if not PermissionService.can_edit(user_id, story_data):
            world_data = storage.load_world(story_data.get('world_id'))
            if not world_data or not PermissionService.is_world_coauthor(user_id, world_data):
                raise PermissionDeniedError('edit', 'story')

        data = request.validated_data
        for field in ['title', 'content', 'format']:
            if data.get(field) is not None:
                story_data[field] = data[field]
        if data.get('chapter_number') is not None:
            story_data['chapter_number'] = data['chapter_number']
        if data.get('order') is not None:
            story_data['order'] = data['order']
        if 'author_signature' in data:
            existing = story_data.get('author_signature') or {}
            story_data['author_signature'] = {
                'token': existing.get('token') or str(_uuid.uuid4()),
                'display': data['author_signature'].get('display', existing.get('display', '')),
                'owner_id': existing.get('owner_id') or story_data.get('owner_id'),
            }

        story_data['updated_at'] = datetime.now().isoformat()
        storage.save_story(story_data)
        flush_data()

        return success_response(
            {'story_id': story_id, 'updated_at': story_data['updated_at']},
            "Story saved"
        )

    @story_bp.route('/api/stories/<story_id>', methods=['DELETE'])
    @token_required
    def delete_story(story_id):
        """Delete a story (owner only).
        ---
        tags:
          - Stories
        parameters:
          - name: story_id
            in: path
            type: string
            required: true
          - in: header
            name: Authorization
            type: string
            required: true
        responses:
          200:
            description: Story deleted
          403:
            description: Permission denied
          404:
            description: Story not found
        """
        story_data = storage.load_story(story_id)
        if not story_data:
            raise ResourceNotFoundError('Story', story_id)

        if not PermissionService.can_delete(g.current_user.user_id, story_data):
            raise PermissionDeniedError('delete', 'story')

        if story_data.get('visibility') == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data)
            user.decrement_public_stories()
            storage.save_user(user.to_dict())

        storage.delete_events_by_story(story_id)
        storage.delete_story(story_id)
        flush_data()

        return deleted_response(t('story.deleted'))

    @story_bp.route('/api/stories/<story_id>/neighbors', methods=['GET'])
    @optional_auth
    def story_neighbors(story_id):
        """Return the previous and next stories in the world's novel order.
        ---
        tags:
          - Stories
        parameters:
          - name: story_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Neighbor summaries ({prev, next}).
          404:
            description: Story not found
        """
        story_data = storage.load_story(story_id)
        if not story_data:
            raise ResourceNotFoundError('Story', story_id)

        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        if not PermissionService.can_view(user_id, story_data):
            raise PermissionDeniedError('view', 'story')

        world_id = story_data.get('world_id')
        neighbors = NovelService.get_neighbors(storage, world_id, story_id, user_id)
        return success_response(neighbors)

    @story_bp.route('/api/stories/<story_id>/link-entities', methods=['POST'])
    @token_required
    @validate_request(LinkEntitiesSchema)
    def story_link_entities(story_id):
        """Link analyzed characters and locations to a story.
        ---
        tags:
          - Stories
        parameters:
          - name: story_id
            in: path
            type: string
            required: true
            description: Story UUID
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                characters:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      role:
                        type: string
                locations:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      description:
                        type: string
        responses:
          200:
            description: Entities linked successfully
          404:
            description: Story not found
        """
        story_data = storage.load_story(story_id)
        if not story_data:
            raise ResourceNotFoundError('Story', story_id)

        data = request.validated_data
        characters = data.get('characters', [])
        locations = data.get('locations', [])
        auto_create = data.get('auto_create', True)

        world_id = story_data.get('world_id')
        world_data = storage.load_world(world_id) if world_id else None

        existing_entities = storage.list_entities(world_id) if world_id else []
        existing_locations = storage.list_locations(world_id) if world_id else []

        linked_entities = []
        linked_locations = []
        created_entities = []
        created_locations = []
        unmatched_characters = []
        unmatched_locations = []

        for char in characters:
            char_name = char.get('name') if isinstance(char, dict) else char
            char_role = char.get('role', 'nhân vật') if isinstance(char, dict) else 'nhân vật'
            if char_name and world_id:
                existing = next(
                    (e for e in existing_entities if e.get('name', '').lower() == char_name.lower()),
                    None
                )
                if existing:
                    entity_id = existing.get('entity_id')
                    if entity_id not in linked_entities:
                        linked_entities.append(entity_id)
                elif auto_create:
                    char_desc = char.get('description', '') if isinstance(char, dict) else ''
                    new_entity = Entity(
                        name=char_name,
                        entity_type=char_role or 'nhân vật',
                        description=char_desc or 'Nhân vật trong câu chuyện',
                        world_id=world_id,
                        metadata={'role': char_role, 'auto_created': True}
                    )
                    entity_data = new_entity.to_dict()
                    storage.save_entity(entity_data)
                    created_entities.append(entity_data)
                    linked_entities.append(new_entity.entity_id)
                    existing_entities.append(entity_data)
                    if world_data is not None:
                        world_data.setdefault('entities', [])
                        if new_entity.entity_id not in world_data['entities']:
                            world_data['entities'].append(new_entity.entity_id)
                else:
                    unmatched_characters.append({'name': char_name, 'role': char_role})

        for loc in locations:
            loc_name = loc.get('name') if isinstance(loc, dict) else loc
            loc_desc = loc.get('description', '') if isinstance(loc, dict) else ''
            if loc_name and world_id:
                existing = next(
                    (l for l in existing_locations if l.get('name', '').lower() == loc_name.lower()),
                    None
                )
                if existing:
                    location_id = existing.get('location_id')
                    if location_id not in linked_locations:
                        linked_locations.append(location_id)
                elif auto_create:
                    new_location = Location(
                        name=loc_name,
                        description=loc_desc or t('story.default_locations_title'),
                        world_id=world_id,
                        metadata={'auto_created': True}
                    )
                    location_data = new_location.to_dict()
                    storage.save_location(location_data)
                    created_locations.append(location_data)
                    linked_locations.append(new_location.location_id)
                    existing_locations.append(location_data)
                    if world_data is not None:
                        world_data.setdefault('locations', [])
                        if new_location.location_id not in world_data['locations']:
                            world_data['locations'].append(new_location.location_id)
                else:
                    unmatched_locations.append({'name': loc_name, 'description': loc_desc})

        story_data.setdefault('entities', [])
        story_data.setdefault('locations', [])

        for eid in linked_entities:
            if eid not in story_data['entities']:
                story_data['entities'].append(eid)
        for lid in linked_locations:
            if lid not in story_data['locations']:
                story_data['locations'].append(lid)

        storage.save_story(story_data)
        if world_data:
            storage.save_world(world_data)
        flush_data()

        return success_response({
            'linked_entities': linked_entities,
            'linked_locations': linked_locations,
            'created_entities': created_entities,
            'created_locations': created_locations,
            'unmatched_characters': unmatched_characters,
            'unmatched_locations': unmatched_locations,
            'story': story_data
        }, "Entities linked successfully")

    @story_bp.route('/api/stories/<story_id>/clear-links', methods=['POST'])
    @token_required
    def story_clear_links(story_id):
        """Clear all entity and location links from a story for re-analysis.
        ---
        tags:
          - Stories
        parameters:
          - name: story_id
            in: path
            type: string
            required: true
            description: Story UUID
        responses:
          200:
            description: Links cleared successfully
          404:
            description: Story not found
        """
        story_data = storage.load_story(story_id)
        if not story_data:
            raise ResourceNotFoundError('Story', story_id)

        previous_entities = story_data.get('entities', [])
        previous_locations = story_data.get('locations', [])

        story_data['entities'] = []
        story_data['locations'] = []

        storage.save_story(story_data)
        flush_data()

        return success_response({
            'cleared_entities': previous_entities,
            'cleared_locations': previous_locations,
            'story': story_data
        }, "Links cleared successfully")

    return story_bp


# Helper functions

def _get_user_drafts(storage, user_id, exclude_story_id=None):
    """Return draft stories owned by user_id, optionally excluding one story."""
    stories = storage.list_stories(user_id=user_id)
    drafts = [s for s in stories if s.get('visibility') == 'draft' and s.get('owner_id') == user_id]
    if exclude_story_id:
        drafts = [s for s in drafts if s['story_id'] != exclude_story_id]
    return drafts


def _resolve_linked_entities(storage, world, world_id, selected_characters, description):
    """Resolve entity IDs from selected characters or auto-detect from description."""
    if selected_characters is not None:
        selected_ids = set(selected_characters)
        linked_entities = []

        if '__new__' in selected_ids:
            new_entity = Entity(
                name='(GPT đặt tên)',
                entity_type='nhân vật',
                description='Nhân vật mới được tạo bởi GPT',
                world_id=world_id
            )
            storage.save_entity(new_entity.to_dict())
            linked_entities.append(new_entity.entity_id)
            if new_entity.entity_id not in world.entities:
                world.entities.append(new_entity.entity_id)
            selected_ids.remove('__new__')

        for ent_id in selected_ids:
            if ent_id in world.entities:
                linked_entities.append(ent_id)

        return linked_entities
    else:
        entity_data_list = [
            storage.load_entity(ent_id)
            for ent_id in world.entities
            if storage.load_entity(ent_id)
        ]
        _, mentioned_entity_ids = CharacterService.detect_mentioned_characters(
            description, entity_data_list
        )
        return mentioned_entity_ids or []


