"""World management routes."""

from flask import Blueprint, request, g
from core.models import World, Entity, Location, User, Story
from core.exceptions import (
    ResourceNotFoundError,
    PermissionDeniedError,
    QuotaExceededError,
    ValidationError as APIValidationError,
    BusinessRuleError
)
from services import CharacterService, PermissionService, NovelService
from interfaces.auth_middleware import token_required, optional_auth
from utils.responses import success_response, created_response, deleted_response, paginated_response
from utils.validation import validate_request, validate_query_params
from utils.i18n import t
from schemas.world_schemas import (
    CreateWorldSchema,
    UpdateWorldSchema,
    ListWorldsQuerySchema,
    ListWorldStoriesQuerySchema,
    CreateEntitySchema,
    UpdateEntitySchema,
    UpdateLocationSchema,
    UpdateNovelSchema,
    ReorderChaptersSchema,
    NovelContentQuerySchema,
)
import random


def create_world_bp(storage, world_generator, diagram_generator, flush_data):
    """Create world blueprint with dependencies."""

    world_bp = Blueprint('worlds', __name__)

    @world_bp.route('/api/worlds', methods=['GET'])
    @optional_auth
    @validate_query_params(ListWorldsQuerySchema)
    def list_worlds():
        """List world summaries visible to current user (paginated, without heavy fields).
        ---
        tags:
          - Worlds
        parameters:
          - in: header
            name: Authorization
            type: string
            required: false
            description: "Bearer {token} (optional, for accessing private worlds)"
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
            description: Paginated world summaries (excludes description/metadata/novel)
        """
        params = request.validated_data
        page = params.get('page', 1)
        per_page = params.get('per_page', 20)
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None

        items, total = storage.list_worlds_summary(
            user_id=user_id, page=page, per_page=per_page,
        )
        if items:
            owner_ids = {item['owner_id'] for item in items if item.get('owner_id')}
            username_map = storage.load_users_by_ids(owner_ids)
            for item in items:
                item['owner_username'] = username_map.get(item.get('owner_id', ''), '')
        return paginated_response(items, page, per_page, total)

    @world_bp.route('/api/worlds', methods=['POST'])
    @token_required
    @validate_request(CreateWorldSchema)
    def create_world():
        """Create new world (requires authentication).
        ---
        tags:
          - Worlds
        parameters:
          - in: header
            name: Authorization
            type: string
            required: true
            description: "Bearer {token}"
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                  example: "Thế giới kỳ ảo"
                world_type:
                  type: string
                  enum: [fantasy, sci-fi, modern, historical]
                  example: fantasy
                description:
                  type: string
                  example: "Một thế giới đầy phép thuật và rồng"
                visibility:
                  type: string
                  enum: [draft, private, public]
                  default: private
                gpt_entities:
                  type: object
                  description: GPT analysis result (optional)
        responses:
          201:
            description: World created successfully
          400:
            description: Invalid input or quota exceeded
          401:
            description: Unauthorized
        """
        data = request.validated_data
        visibility = data.get('visibility', 'private')

        if visibility == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            if user_data:
                user = User.from_dict(user_data)
                if not user.can_create_public_world():
                    raise QuotaExceededError(
                        'Bạn đã đạt giới hạn số thế giới công khai',
                        current_count=user.metadata.get('public_worlds_count', 0),
                        limit=user.metadata.get('public_worlds_limit', 1)
                    )

        world = world_generator.generate(data.get('description', ''), world_type=data['world_type'])
        if data.get('name'):
            world.name = data['name']
        # Always use the user's exact description — prevent world_generator from
        # appending auto-generated English theme text to user-provided content.
        if data.get('description'):
            world.description = data['description']

        world.owner_id = g.current_user.user_id
        world.visibility = visibility

        gpt_entities = data.get('gpt_entities')
        if gpt_entities and 'entities' in gpt_entities and 'locations' in gpt_entities:
            _create_entities_from_gpt(storage, world, gpt_entities)
        else:
            _create_random_entities(storage, world_generator, world)

        storage.save_world(world.to_dict())

        if visibility == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            if user_data:
                user = User.from_dict(user_data)
                user.increment_public_worlds()
                storage.save_user(user.to_dict())

        flush_data()

        return created_response(world.to_dict(), t('world.created'))

    @world_bp.route('/api/worlds/<world_id>', methods=['GET'])
    @optional_auth
    def get_world_detail(world_id):
        """Get a specific world.
        ---
        tags:
          - Worlds
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
            description: World UUID
          - in: header
            name: Authorization
            type: string
            required: false
            description: "Bearer {token} (optional)"
        responses:
          200:
            description: World details
          403:
            description: Permission denied
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        if not PermissionService.can_view(user_id, world_data):
            raise PermissionDeniedError('view', 'world')

        world_data = dict(world_data)
        if world_data.get('owner_id'):
            username_map = storage.load_users_by_ids({world_data['owner_id']})
            world_data['owner_username'] = username_map.get(world_data['owner_id'], '')
        return success_response(world_data)

    @world_bp.route('/api/worlds/<world_id>', methods=['PUT'])
    @token_required
    @validate_request(UpdateWorldSchema)
    def update_world(world_id):
        """Update a specific world (owner only).
        ---
        tags:
          - Worlds
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - in: header
            name: Authorization
            type: string
            required: true
            description: "Bearer {token}"
          - in: body
            name: body
            required: false
            schema:
              type: object
              properties:
                name:
                  type: string
                description:
                  type: string
                visibility:
                  type: string
                  enum: [draft, private, public]
        responses:
          200:
            description: World updated successfully
          400:
            description: Quota exceeded
          403:
            description: Permission denied
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        if not PermissionService.can_edit(g.current_user.user_id, world_data):
            raise PermissionDeniedError('edit', 'world')

        data = request.validated_data

        if 'visibility' in data:
            old_visibility = world_data.get('visibility', 'private')
            new_visibility = data['visibility']

            if old_visibility != new_visibility:
                user_data = storage.load_user(g.current_user.user_id)
                user = User.from_dict(user_data)

                if old_visibility != 'public' and new_visibility == 'public':
                    if not user.can_create_public_world():
                        raise QuotaExceededError(
                            'Bạn đã đạt giới hạn số thế giới công khai',
                            current_count=user.metadata.get('public_worlds_count', 0),
                            limit=user.metadata.get('public_worlds_limit', 1)
                        )
                    user.increment_public_worlds()
                    storage.save_user(user.to_dict())
                elif old_visibility == 'public' and new_visibility != 'public':
                    user.decrement_public_worlds()
                    storage.save_user(user.to_dict())

                world_data['visibility'] = new_visibility

        for field in ['name', 'description', 'world_type']:
            if field in data:
                world_data[field] = data[field]

        storage.save_world(world_data)
        flush_data()

        return success_response(world_data, t('world.updated'))

    @world_bp.route('/api/worlds/<world_id>', methods=['DELETE'])
    @token_required
    def delete_world(world_id):
        """Delete a world (owner only).
        ---
        tags:
          - Worlds
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - in: header
            name: Authorization
            type: string
            required: true
        responses:
          200:
            description: World deleted
          403:
            description: Permission denied
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        if not PermissionService.can_delete(g.current_user.user_id, world_data):
            raise PermissionDeniedError('delete', 'world')

        if world_data.get('visibility') == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data)
            user.decrement_public_worlds()
            storage.save_user(user.to_dict())

        storage.delete_world(world_id)
        flush_data()

        return deleted_response(t('world.deleted'))

    @world_bp.route('/api/worlds/<world_id>/stories', methods=['GET'])
    @optional_auth
    @validate_query_params(ListWorldStoriesQuerySchema)
    def world_stories(world_id):
        """Get stories in a world (paginated, without full content).
        ---
        tags:
          - Worlds
        parameters:
          - in: path
            name: world_id
            type: string
            required: true
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
            description: Paginated story summaries (content_preview instead of full content)
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        params = request.validated_data
        page = params.get('page', 1)
        per_page = params.get('per_page', 20)
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None

        items, total = storage.list_stories_summary(
            world_id, user_id=user_id, page=page, per_page=per_page,
        )
        return paginated_response(items, page, per_page, total)

    @world_bp.route('/api/worlds/<world_id>/characters', methods=['GET'])
    def world_characters(world_id):
        """Get all characters in a world (excluding dangerous creatures)."""
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        entities = []
        for ent_id in world_data.get('entities', []):
            ent_data = storage.load_entity(ent_id)
            if ent_data and ent_data.get('entity_type', '') not in ['dragon', 'demon', 'monster']:
                entities.append({
                    **ent_data,
                    'display': CharacterService.format_character_display(ent_data)
                })
        return success_response(entities)

    @world_bp.route('/api/worlds/<world_id>/locations', methods=['GET'])
    def world_locations(world_id):
        """Get all locations in a world."""
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        locations = [
            storage.load_location(loc_id)
            for loc_id in world_data.get('locations', [])
            if storage.load_location(loc_id)
        ]
        return success_response(locations)

    @world_bp.route('/api/worlds/<world_id>/entities/<entity_id>', methods=['PUT'])
    @token_required
    @validate_request(UpdateEntitySchema)
    def update_entity(world_id, entity_id):
        """Update an entity in a world.
        ---
        tags:
          - Worlds
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - name: entity_id
            in: path
            type: string
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                name:
                  type: string
                entity_type:
                  type: string
                description:
                  type: string
                attributes:
                  type: object
        responses:
          200:
            description: Entity updated successfully
          403:
            description: Permission denied
          404:
            description: World or entity not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        entity_data = storage.load_entity(entity_id)
        if not entity_data:
            raise ResourceNotFoundError('Entity', entity_id)

        owner_id = world_data.get('owner_id')
        if owner_id and g.current_user.user_id != owner_id and g.current_user.role != 'admin':
            raise PermissionDeniedError('edit', 'entity')

        data = request.validated_data
        for field in ['name', 'entity_type', 'description', 'attributes']:
            if field in data:
                entity_data[field] = data[field]

        storage.save_entity(entity_data)
        flush_data()

        return success_response(entity_data, t('entity.updated'))

    @world_bp.route('/api/worlds/<world_id>/entities/<entity_id>', methods=['DELETE'])
    @token_required
    def delete_entity(world_id, entity_id):
        """Delete an entity from a world.
        ---
        tags:
          - Worlds
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - name: entity_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Entity deleted successfully
          404:
            description: World or entity not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        entity_data = storage.load_entity(entity_id)
        if not entity_data:
            raise ResourceNotFoundError('Entity', entity_id)

        if entity_id in world_data.get('entities', []):
            world_data['entities'].remove(entity_id)
            storage.save_world(world_data)

        for story_data in storage.list_stories(world_id):
            if entity_id in story_data.get('entities', []):
                story_data['entities'].remove(entity_id)
                storage.save_story(story_data)

        storage.delete_entity(entity_id)
        flush_data()

        return deleted_response(t('entity.deleted'))

    @world_bp.route('/api/worlds/<world_id>/locations/<location_id>', methods=['PUT'])
    @token_required
    @validate_request(UpdateLocationSchema)
    def update_location(world_id, location_id):
        """Update a location in a world."""
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        location_data = storage.load_location(location_id)
        if not location_data:
            raise ResourceNotFoundError('Location', location_id)

        owner_id = world_data.get('owner_id')
        collaborators = world_data.get('collaborators', [])
        collab_ids = [c.get('user_id') for c in collaborators]
        if owner_id and g.current_user.user_id != owner_id and g.current_user.user_id not in collab_ids and g.current_user.role != 'admin':
            raise PermissionDeniedError('edit', 'location')

        data = request.validated_data
        for field in ['name', 'location_type', 'description']:
            if field in data:
                location_data[field] = data[field]

        storage.save_location(location_data)
        flush_data()

        return success_response(location_data, t('location.updated'))

    @world_bp.route('/api/worlds/<world_id>/locations/<location_id>', methods=['DELETE'])
    @token_required
    def delete_location(world_id, location_id):
        """Delete a location from a world.
        ---
        tags:
          - Worlds
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - name: location_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Location deleted successfully
          404:
            description: World or location not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        location_data = storage.load_location(location_id)
        if not location_data:
            raise ResourceNotFoundError('Location', location_id)

        if location_id in world_data.get('locations', []):
            world_data['locations'].remove(location_id)
            storage.save_world(world_data)

        for story_data in storage.list_stories(world_id):
            if location_id in story_data.get('locations', []):
                story_data['locations'].remove(location_id)
                storage.save_story(story_data)

        storage.delete_location(location_id)
        flush_data()

        return deleted_response(t('location.deleted'))

    @world_bp.route('/api/worlds/<world_id>/relationships', methods=['GET'])
    def world_relationships(world_id):
        """Get relationship diagram for a world."""
        from core.models import Entity as EntityModel

        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        stories = storage.list_stories(world_id)
        entities = [
            EntityModel.from_dict(storage.load_entity(ent_id))
            for ent_id in world_data.get('entities', [])
            if storage.load_entity(ent_id)
        ]

        svg_content = diagram_generator.generate_svg(
            entities=entities,
            stories=[Story.from_dict(s) for s in stories]
        )
        return success_response({'svg': svg_content})

    @world_bp.route('/api/worlds/<world_id>/auto-link-stories', methods=['POST'])
    @optional_auth
    def auto_link_stories(world_id):
        """Auto-link stories that share entities or locations.
        ---
        tags:
          - Worlds
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
            description: World UUID
        responses:
          200:
            description: Stories linked successfully
          404:
            description: World not found
        """
        from generators import StoryLinker

        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        stories_data = storage.list_stories(world_id, user_id=user_id)

        if len(stories_data) < 2:
            return success_response(
                {'linked_count': 0, 'links': [], 'unlinked_stories': []},
                t('world.need_two_stories_to_link')
            )

        stories = [Story.from_dict(s) for s in stories_data]
        linker = StoryLinker()
        linker.link_stories(stories, link_by_entities=True, link_by_locations=True, link_by_time=False)

        all_links = []
        linked_count = 0

        for story in stories:
            if story.linked_stories:
                linked_count += 1
                storage.save_story(story.to_dict())
                for linked_id in story.linked_stories:
                    linked_story = next((s for s in stories if s.story_id == linked_id), None)
                    if linked_story:
                        link_info = {
                            'from_id': story.story_id,
                            'from_title': story.title,
                            'to_id': linked_id,
                            'to_title': linked_story.title
                        }
                        reverse_exists = any(
                            l['from_id'] == linked_id and l['to_id'] == story.story_id
                            for l in all_links
                        )
                        if not reverse_exists:
                            all_links.append(link_info)

        flush_data()

        unlinked_stories = sorted(
            [
                {
                    'story_id': s.story_id,
                    'title': s.title,
                    'order': getattr(s, 'order', None),
                    'created_at': getattr(s, 'created_at', '') or '',
                    'description': s.content[:200] if s.content else ''
                }
                for s in stories if not s.entities and not s.locations
            ],
            key=lambda s: (s['order'] if s['order'] is not None else float('inf'), s['created_at'])
        )

        return success_response({
            'linked_count': linked_count,
            'links': all_links,
            'unlinked_stories': unlinked_stories
        }, t('world.auto_link_done', count=linked_count))

    @world_bp.route('/api/worlds/<world_id>/share', methods=['POST'])
    @token_required
    def share_world(world_id):
        """Share a private world with specific users.
        ---
        tags:
          - Worlds
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
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
                user_ids:
                  type: array
                  items:
                    type: string
                  description: List of user IDs to share with
        responses:
          200:
            description: World shared successfully
          400:
            description: Cannot share public worlds
          403:
            description: Only owner can share
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        if not PermissionService.can_share(g.current_user.user_id, world_data):
            raise PermissionDeniedError('share', 'world')

        if world_data.get('visibility') == 'public':
            raise BusinessRuleError(t('world.public_no_share'))

        data = request.json
        user_ids = data.get('user_ids', [])

        for user_id in user_ids:
            if not storage.load_user(user_id):
                raise APIValidationError(t('world.share_user_not_found', user_id=user_id))

        current_shared = world_data.get('shared_with', [])
        for user_id in user_ids:
            if user_id not in current_shared:
                current_shared.append(user_id)

        world_data['shared_with'] = current_shared
        storage.save_world(world_data)
        flush_data()

        return success_response({'shared_with': current_shared}, t('world.shared'))

    @world_bp.route('/api/worlds/<world_id>/unshare', methods=['POST'])
    @token_required
    def unshare_world(world_id):
        """Remove users from shared world access.
        ---
        tags:
          - Worlds
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
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
                user_ids:
                  type: array
                  items:
                    type: string
        responses:
          200:
            description: Access removed
          403:
            description: Permission denied
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        if not PermissionService.can_share(g.current_user.user_id, world_data):
            raise PermissionDeniedError('manage access for', 'world')

        data = request.json
        user_ids = data.get('user_ids', [])
        current_shared = world_data.get('shared_with', [])
        world_data['shared_with'] = [uid for uid in current_shared if uid not in user_ids]

        storage.save_world(world_data)
        flush_data()

        return success_response({'shared_with': world_data['shared_with']}, t('world.unshared'))

    # ------------------------------------------------------------------
    # SUB-4 — Novel Structure
    # ------------------------------------------------------------------

    @world_bp.route('/api/worlds/<world_id>/novel', methods=['GET'])
    @optional_auth
    def get_novel(world_id):
        """Get novel metadata and ordered chapter list for a world.
        ---
        tags:
          - Novel
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Novel metadata with chapters
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        novel = world_data.get('novel') or {}
        chapter_order = novel.get('chapter_order', [])

        # Match /novel/content, /world detail and /world/stories — when no
        # auth token is present we treat the visitor as anonymous so only
        # public stories surface in the chapter list.
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        all_stories = storage.list_stories(world_id=world_id, user_id=user_id)
        stories_by_id = {s['story_id']: s for s in all_stories}

        if chapter_order:
            story_ids_to_load = chapter_order
        else:
            numbered = sorted(
                [s for s in all_stories if s.get('chapter_number') is not None],
                key=lambda s: s.get('chapter_number', 0)
            )
            story_ids_to_load = [s['story_id'] for s in numbered]

        chapters = []
        total_word_count = 0
        for story_id in story_ids_to_load:
            story = stories_by_id.get(story_id)
            if not story:
                continue
            content = story.get('content') or ''
            word_count = len(content.split()) if content.strip() else 0
            total_word_count += word_count
            chapters.append({
                'story_id': story_id,
                'chapter_number': story.get('chapter_number'),
                'title': story.get('title'),
                'word_count': word_count,
                'updated_at': story.get('updated_at')
            })

        owner_id = world_data.get('owner_id')
        owner_username = ''
        if owner_id:
            username_map = storage.load_users_by_ids({owner_id})
            owner_username = username_map.get(owner_id, '')
        return success_response({
            'title': novel.get('title', world_data.get('name')),
            'description': novel.get('description', ''),
            'world_description': world_data.get('description', ''),
            'chapters': chapters,
            'total_word_count': total_word_count,
            'owner_id': owner_id,
            'owner_username': owner_username,
            'co_authors': world_data.get('co_authors', [])
        })

    @world_bp.route('/api/worlds/<world_id>/novel/content', methods=['GET'])
    @optional_auth
    @validate_query_params(NovelContentQuerySchema)
    def get_novel_content(world_id):
        """Paginated novel content across chapters ordered by Story.order ASC.
        ---
        tags:
          - Novel
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - name: cursor
            in: query
            type: string
            required: false
          - name: line_budget
            in: query
            type: integer
            required: false
            default: 100
        responses:
          200:
            description: Batch of chapter blocks with next_cursor for pagination.
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        if not PermissionService.can_view(user_id, world_data):
            raise PermissionDeniedError('view', 'world')

        params = request.validated_data
        batch = NovelService.get_content_batch(
            storage,
            world_id,
            cursor=params.get('cursor'),
            line_budget=params.get('line_budget', 100),
            user_id=user_id,
        )
        return success_response(batch)

    @world_bp.route('/api/worlds/<world_id>/novel', methods=['PUT'])
    @token_required
    @validate_request(UpdateNovelSchema)
    def upsert_novel(world_id):
        """Create or update novel metadata for a world.
        ---
        tags:
          - Novel
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                title:
                  type: string
                description:
                  type: string
        responses:
          200:
            description: Novel metadata saved
          403:
            description: Permission denied
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        if not PermissionService.is_world_coauthor(g.current_user.user_id, world_data):
            raise PermissionDeniedError('manage novel for', 'world')

        novel = _get_or_create_novel(world_data)

        data = request.validated_data
        if 'title' in data:
            novel['title'] = data['title']
        if 'description' in data:
            novel['description'] = data['description']

        world_data['novel'] = novel
        storage.save_world(world_data)
        flush_data()

        return success_response({
            'title': novel['title'],
            'description': novel['description']
        }, "Novel updated")

    @world_bp.route('/api/worlds/<world_id>/novel/chapters', methods=['PATCH'])
    @token_required
    @validate_request(ReorderChaptersSchema)
    def reorder_chapters(world_id):
        """Reorder chapters in the novel.
        ---
        tags:
          - Novel
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [order]
              properties:
                order:
                  type: array
                  items:
                    type: string
        responses:
          200:
            description: Chapters reordered
          403:
            description: Permission denied
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        if not PermissionService.is_world_coauthor(g.current_user.user_id, world_data):
            raise PermissionDeniedError('reorder chapters for', 'world')

        order = request.validated_data['order']

        world_story_ids = set(world_data.get('stories', []))

        # Update chapter_number and order on each story (1-based, contiguous).
        # `order` is the sort key used by NovelService; keeping it in sync with
        # chapter_number ensures the drag-reorder actually changes reading order.
        updated_chapters = []
        for idx, story_id in enumerate(order, start=1):
            if story_id not in world_story_ids:
                continue
            story = storage.load_story(story_id)
            if story:
                story['chapter_number'] = idx
                story['order'] = idx
                storage.save_story(story)
                updated_chapters.append({'story_id': story_id, 'chapter_number': idx, 'order': idx})

        novel = _get_or_create_novel(world_data)
        novel['chapter_order'] = order
        world_data['novel'] = novel
        storage.save_world(world_data)
        flush_data()

        return success_response({'chapters': updated_chapters}, t('novel.chapters_reordered'))

    return world_bp


# Helper functions

def _get_or_create_novel(world_data):
    """Return existing novel block or a fresh default dict (not yet persisted)."""
    return world_data.get('novel') or {
        'title': world_data.get('name'),
        'description': '',
        'chapter_order': []
    }


def _create_entities_from_gpt(storage, world, gpt_entities):
    """Create entities and locations from GPT analysis."""
    for ent_data in gpt_entities['entities']:
        entity = Entity(
            name=ent_data['name'],
            description=ent_data.get('description', ''),
            entity_type=ent_data.get('entity_type', 'commoner'),
            world_id=world.world_id,
            attributes=ent_data.get('attributes', {
                'Strength': random.randint(3, 8),
                'Intelligence': random.randint(3, 8),
                'Charisma': random.randint(3, 8)
            })
        )
        storage.save_entity(entity.to_dict())
        world.add_entity(entity.entity_id)

    for loc_data in gpt_entities['locations']:
        coords = loc_data.get('coordinates', {})
        location = Location(
            name=loc_data['name'],
            description=loc_data.get('description', ''),
            world_id=world.world_id,
            coordinates={
                'x': coords.get('x', random.uniform(-100, 100)),
                'y': coords.get('y', random.uniform(-100, 100))
            }
        )
        storage.save_location(location.to_dict())
        world.add_location(location.location_id)


def _create_random_entities(storage, world_generator, world):
    """Create random entities and locations for world."""
    for location in world_generator.generate_locations(world, count=3):
        storage.save_location(location.to_dict())
        world.add_location(location.location_id)

    for entity in world_generator.generate_entities(world, count=5):
        storage.save_entity(entity.to_dict())
        world.add_entity(entity.entity_id)
