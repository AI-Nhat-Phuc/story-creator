"""Story routes for the API backend."""

from flask import Blueprint, request, jsonify, g
from core.models.world import World
from core.models.entity import Entity
from core.models.location import Location
from core.models.user import User
from services import CharacterService, PermissionService
from interfaces.auth_middleware import token_required, optional_auth
import random


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
        responses:
          200:
            description: List of stories (public + owned + shared)
        """
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None

        # Get all stories across all worlds (filtered by permissions)
        all_stories = storage.list_stories(user_id=user_id)
        return jsonify(all_stories)

    @story_bp.route('/api/stories', methods=['POST'])
    @token_required
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
                time_index:
                  type: integer
                  minimum: 0
                  maximum: 100
                  example: 10
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
        data = request.json
        world_id = data.get('world_id')

        # Load world to check ownership
        world_data = storage.load_world(world_id)
        if not world_data:
            return jsonify({'error': 'World not found'}), 404

        # Default visibility inherits from the world
        world_visibility = world_data.get('visibility', 'private')
        visibility = data.get('visibility', world_visibility)

        # Check if user can create stories in this world (must view world)
        if not PermissionService.can_view(g.current_user.user_id, world_data):
            return jsonify({'error': 'Bạn không có quyền tạo câu chuyện trong thế giới này'}), 403

        # Check quota for public stories
        if visibility == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data)

            if not user.can_create_public_story():
                return jsonify({
                    'error': 'Bạn đã đạt giới hạn số câu chuyện công khai',
                    'current_count': user.metadata.get('public_stories_count', 0),
                    'limit': user.metadata.get('public_stories_limit', 20)
                }), 400

        title = data.get('title', 'Untitled Story')
        description = data.get('description', '')
        genre = data.get('genre', 'adventure')
        time_index = data.get('time_index', 0)
        selected_characters = data.get('selected_characters', None)

        world = World.from_dict(world_data)

        # Use selected_characters if provided, else auto-detect
        linked_entities = []
        if selected_characters:
          # Remove duplicates
          selected_ids = set(selected_characters)
          # Handle new character creation
          if '__new__' in selected_ids:
            # Create a new character entity with a placeholder name (GPT will name in description)
            new_entity = Entity(
              name='(GPT đặt tên)',
              entity_type='nhân vật',
              description='Nhân vật mới được tạo bởi GPT',
              world_id=world_id
            )
            storage.save_entity(new_entity.to_dict())
            linked_entities.append(new_entity.entity_id)
            # Add to world
            if new_entity.entity_id not in world.entities:
              world.entities.append(new_entity.entity_id)
            selected_ids.remove('__new__')
          # Add existing character IDs
          for ent_id in selected_ids:
            if ent_id in world.entities:
              linked_entities.append(ent_id)
        else:
          # Auto-detect mentioned characters (do NOT fallback to random entity)
          entity_data_list = []
          for ent_id in world.entities:
            ent_data = storage.load_entity(ent_id)
            if ent_data:
              entity_data_list.append(ent_data)
          _, mentioned_entity_ids = CharacterService.detect_mentioned_characters(
            description, entity_data_list
          )
          linked_entities = mentioned_entity_ids or []

        # Generate story (don't auto-assign locations, let user/GPT decide)
        story = story_generator.generate(
            title,
            description,
            world.world_id,
            genre,
            locations=None,
            entities=linked_entities if linked_entities else None
        )

        # Set ownership and visibility
        story.owner_id = g.current_user.user_id
        story.visibility = visibility

        # Set world time based on time_index
        calendar = world.metadata.get('calendar', {})
        if calendar:
            # Map time_index (0-100) to world's timeline
            # time_index None or 0 = unknown time
            # time_index 50 = current_year
            # time_index 100 = current_year + 50
            if time_index is None or time_index == 0:
                # Unknown time
                story.metadata['world_time'] = {
                    'era': '',
                    'year': 0,
                    'month': 0,
                    'day': 0,
                    'description': 'Không xác định'
                }
            else:
                # Calculate year from time_index
                current_year = calendar.get('current_year', 1)
                year_range = 100  # 100 years span
                calculated_year = max(1, current_year + int((time_index / 100) * year_range) - (year_range // 2))

                story.metadata['world_time'] = {
                    'era': calendar.get('current_era', 'Kỷ nguyên mới'),
                    'year': calculated_year,
                    'month': 0,  # Can be set by user later
                    'day': 0,    # Can be set by user later
                    'description': f"{calendar.get('year_name', 'Năm')} {calculated_year}, {calendar.get('current_era', 'Kỷ nguyên mới')}"
                }

        # Generate time cone
        time_cone = story_generator.generate_time_cone(
            story,
            world.world_id,
            time_index=time_index
        )

        # Save
        storage.save_story(story.to_dict())
        storage.save_time_cone(time_cone.to_dict())
        world.add_story(story.story_id)
        storage.save_world(world.to_dict())

        # Update user quota if public
        if visibility == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data)
            user.increment_public_stories()
            storage.save_user(user.to_dict())

        flush_data()

        return jsonify({
          'story': story.to_dict(),
          'time_cone': time_cone.to_dict()
        }), 201

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
            return jsonify({'error': 'Story not found'}), 404

        # Check view permission
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        if not PermissionService.can_view(user_id, story_data):
            return jsonify({'error': 'Bạn không có quyền xem câu chuyện này'}), 403

        return jsonify(story_data)

    @story_bp.route('/api/stories/<story_id>', methods=['PUT'])
    @token_required
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
            return jsonify({'error': 'Story not found'}), 404

        # Check edit permission
        if not PermissionService.can_edit(g.current_user.user_id, story_data):
            return jsonify({'error': 'Chỉ chủ sở hữu mới có thể chỉnh sửa'}), 403

        data = request.json
        old_visibility = story_data.get('visibility', 'private')
        new_visibility = data.get('visibility', old_visibility)

        # Handle visibility change
        if old_visibility != new_visibility:
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data)

            if old_visibility != 'public' and new_visibility == 'public':
                if not user.can_create_public_story():
                    return jsonify({
                        'error': 'Bạn đã đạt giới hạn số câu chuyện công khai',
                        'current_count': user.metadata.get('public_stories_count', 0),
                        'limit': user.metadata.get('public_stories_limit', 20)
                    }), 400
                user.increment_public_stories()
                storage.save_user(user.to_dict())

            elif old_visibility == 'public' and new_visibility != 'public':
                user.decrement_public_stories()
                storage.save_user(user.to_dict())

            story_data['visibility'] = new_visibility

        # Update other fields
        if 'title' in data:
            story_data['title'] = data['title']
        if 'content' in data:
            story_data['content'] = data['content']

        storage.save_story(story_data)
        flush_data()

        return jsonify(story_data), 200

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
            return jsonify({'error': 'Story not found'}), 404

        # Check delete permission
        if not PermissionService.can_delete(g.current_user.user_id, story_data):
            return jsonify({'error': 'Chỉ chủ sở hữu mới có thể xóa'}), 403

        # Update quota if deleting public story
        if story_data.get('visibility') == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data)
            user.decrement_public_stories()
            storage.save_user(user.to_dict())

        # Delete associated events
        storage.delete_events_by_story(story_id)

        storage.delete_story(story_id)
        flush_data()

        return jsonify({'message': 'Story deleted successfully'}), 200

    @story_bp.route('/api/stories/<story_id>/link-entities', methods=['POST'])
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
            return jsonify({'error': 'Story not found'}), 404

        data = request.json
        characters = data.get('characters', [])
        locations = data.get('locations', [])
        auto_create = data.get('auto_create', True)

        # Get world to add entities
        world_id = story_data.get('world_id')
        world_data = storage.load_world(world_id) if world_id else None

        # Load existing entities and locations in the world to check for duplicates
        existing_entities = []
        existing_locations = []
        if world_id:
            # Use list_entities/list_locations with world_id filter for better performance
            existing_entities = storage.list_entities(world_id)
            existing_locations = storage.list_locations(world_id)

        linked_entities = []
        linked_locations = []
        created_entities = []
        created_locations = []
        unmatched_characters = []
        unmatched_locations = []

        # Link or create entities from analyzed characters
        for char in characters:
            char_name = char.get('name') if isinstance(char, dict) else char
            char_role = char.get('role', 'nhân vật') if isinstance(char, dict) else 'nhân vật'
            if char_name and world_id:
                # Check if entity with same name already exists in this world
                existing = next(
                    (e for e in existing_entities if e.get('name', '').lower() == char_name.lower()),
                    None
                )

                if existing:
                    # Use existing entity
                    entity_id = existing.get('entity_id')
                    if entity_id not in linked_entities:
                        linked_entities.append(entity_id)
                elif auto_create and world_id:
                    # Auto-create new entity and link it
                    from core.models.entity import Entity
                    char_desc = char.get('description', '') if isinstance(char, dict) else ''
                    new_entity = Entity(
                        name=char_name,
                        entity_type=char_role or 'nhân vật',
                        description=char_desc or f'Nhân vật trong câu chuyện',
                        world_id=world_id,
                        metadata={'role': char_role, 'auto_created': True}
                    )
                    entity_data = new_entity.to_dict()
                    storage.save_entity(entity_data)
                    created_entities.append(entity_data)
                    linked_entities.append(new_entity.entity_id)
                    # Add to existing list so subsequent lookups find it
                    existing_entities.append(entity_data)
                    # Add to world's entity list so it appears in character listings
                    if world_data is not None:
                        world_data.setdefault('entities', [])
                        if new_entity.entity_id not in world_data['entities']:
                            world_data['entities'].append(new_entity.entity_id)
                else:
                    # Not found - mark as unmatched
                    unmatched_characters.append({'name': char_name, 'role': char_role})

        # Link or create locations from analyzed locations
        for loc in locations:
            loc_name = loc.get('name') if isinstance(loc, dict) else loc
            loc_desc = loc.get('description', '') if isinstance(loc, dict) else ''
            if loc_name and world_id:
                # Check if location with same name already exists in this world
                existing = next(
                    (l for l in existing_locations if l.get('name', '').lower() == loc_name.lower()),
                    None
                )

                if existing:
                    # Use existing location
                    location_id = existing.get('location_id')
                    if location_id not in linked_locations:
                        linked_locations.append(location_id)
                elif auto_create and world_id:
                    # Auto-create new location and link it
                    from core.models.location import Location
                    new_location = Location(
                        name=loc_name,
                        description=loc_desc or f'Địa điểm trong câu chuyện',
                        world_id=world_id,
                        metadata={'auto_created': True}
                    )
                    location_data = new_location.to_dict()
                    storage.save_location(location_data)
                    created_locations.append(location_data)
                    linked_locations.append(new_location.location_id)
                    # Add to existing list so subsequent lookups find it
                    existing_locations.append(location_data)
                    # Add to world's location list so it appears in location listings
                    if world_data is not None:
                        world_data.setdefault('locations', [])
                        if new_location.location_id not in world_data['locations']:
                            world_data['locations'].append(new_location.location_id)
                else:
                    # Not found - mark as unmatched
                    unmatched_locations.append({'name': loc_name, 'description': loc_desc})

        # Update story with entity and location IDs (avoid duplicates)
        if 'entities' not in story_data:
            story_data['entities'] = []
        if 'locations' not in story_data:
            story_data['locations'] = []

        for eid in linked_entities:
            if eid not in story_data['entities']:
                story_data['entities'].append(eid)
        for lid in linked_locations:
            if lid not in story_data['locations']:
                story_data['locations'].append(lid)

        # Save everything
        storage.save_story(story_data)
        if world_data:
            storage.save_world(world_data)
        flush_data()

        return jsonify({
            'message': 'Entities linked successfully',
            'linked_entities': linked_entities,
            'linked_locations': linked_locations,
            'created_entities': created_entities,
            'created_locations': created_locations,
            'unmatched_characters': unmatched_characters,
            'unmatched_locations': unmatched_locations,
            'story': story_data
        }), 200

    @story_bp.route('/api/stories/<story_id>/clear-links', methods=['POST'])
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
            return jsonify({'error': 'Story not found'}), 404

        # Store previous links for response
        previous_entities = story_data.get('entities', [])
        previous_locations = story_data.get('locations', [])

        # Clear the links
        story_data['entities'] = []
        story_data['locations'] = []

        # Save updated story
        storage.save_story(story_data)
        flush_data()

        return jsonify({
            'message': 'Links cleared successfully',
            'cleared_entities': previous_entities,
            'cleared_locations': previous_locations,
            'story': story_data
        }), 200

    return story_bp
