"""World management routes."""

from flask import Blueprint, request, jsonify, current_app, g
from core.models import World, Entity, Location, User
from services import CharacterService, PermissionService
from interfaces.auth_middleware import token_required, optional_auth


def create_world_bp(storage, world_generator, diagram_generator, flush_data):
    """Create world blueprint with dependencies."""

    world_bp = Blueprint('worlds', __name__)

    @world_bp.route('/api/worlds', methods=['GET'])
    @optional_auth
    def list_worlds():
        """List all worlds visible to current user.
        ---
        tags:
          - Worlds
        parameters:
          - in: header
            name: Authorization
            type: string
            required: false
            description: "Bearer {token} (optional, for accessing private worlds)"
        responses:
          200:
            description: List of worlds (public + owned + shared)
        """
        # Get current user ID if authenticated
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None

        # Get filtered worlds based on permissions
        worlds = storage.list_worlds(user_id=user_id)
        return jsonify(worlds)

    @world_bp.route('/api/worlds', methods=['POST'])
    @token_required
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
        data = request.json
        visibility = data.get('visibility', 'private')

        # Check quota for public worlds
        if visibility == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data)

            if not user.can_create_public_world():
                return jsonify({
                    'error': 'Bạn đã đạt giới hạn số thế giới công khai',
                    'current_count': user.metadata.get('public_worlds_count', 0),
                    'limit': user.metadata.get('public_worlds_limit', 1)
                }), 400

        world_type = data.get('world_type', 'fantasy')
        description = data.get('description', '')
        name = data.get('name')
        gpt_entities = data.get('gpt_entities')

        # Validate: Name required when using GPT
        if gpt_entities and not name:
            return jsonify({
                'error': 'Tên thế giới là bắt buộc khi sử dụng GPT'
            }), 400

        # Generate world
        world = world_generator.generate(description, world_type=world_type)
        if name:
            world.name = name

        # Set ownership and visibility
        world.owner_id = g.current_user.user_id
        world.visibility = visibility

        # Create entities and locations
        if gpt_entities and 'entities' in gpt_entities and 'locations' in gpt_entities:
            import random
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
        else:
            # Random generation
            locations = world_generator.generate_locations(world, count=3)
            for location in locations:
                storage.save_location(location.to_dict())
                world.add_location(location.location_id)

            entities = world_generator.generate_entities(world, count=5)
            for entity in entities:
                storage.save_entity(entity.to_dict())
                world.add_entity(entity.entity_id)

        # Save world
        storage.save_world(world.to_dict())

        # Update user quota if public
        if visibility == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data)
            user.increment_public_worlds()
            storage.save_user(user.to_dict())

        flush_data()

        return jsonify(world.to_dict()), 201

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
            return jsonify({'error': 'World not found'}), 404

        # Check view permission
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        if not PermissionService.can_view(user_id, world_data):
            return jsonify({'error': 'Bạn không có quyền xem thế giới này'}), 403

        return jsonify(world_data)

    @world_bp.route('/api/worlds/<world_id>', methods=['PUT'])
    @token_required
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
            return jsonify({'error': 'World not found'}), 404

        # Check edit permission (owner only)
        if not PermissionService.can_edit(g.current_user.user_id, world_data):
            return jsonify({'error': 'Chỉ chủ sở hữu mới có thể chỉnh sửa'}), 403

        data = request.json
        old_visibility = world_data.get('visibility', 'private')
        new_visibility = data.get('visibility', old_visibility)

        # Handle visibility change
        if old_visibility != new_visibility:
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data)

            if old_visibility != 'public' and new_visibility == 'public':
                # Changing to public - check quota
                if not user.can_create_public_world():
                    return jsonify({
                        'error': 'Bạn đã đạt giới hạn số thế giới công khai',
                        'current_count': user.metadata.get('public_worlds_count', 0),
                        'limit': user.metadata.get('public_worlds_limit', 1)
                    }), 400
                user.increment_public_worlds()
                storage.save_user(user.to_dict())

            elif old_visibility == 'public' and new_visibility != 'public':
                # Changing from public - decrement quota
                user.decrement_public_worlds()
                storage.save_user(user.to_dict())

            world_data['visibility'] = new_visibility

        # Update other fields
        if 'name' in data:
            world_data['name'] = data['name']
        if 'description' in data:
            world_data['description'] = data['description']

        storage.save_world(world_data)
        flush_data()

        return jsonify(world_data), 200

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
            return jsonify({'error': 'World not found'}), 404

        # Check delete permission
        if not PermissionService.can_delete(g.current_user.user_id, world_data):
            return jsonify({'error': 'Chỉ chủ sở hữu mới có thể xóa'}), 403

        # Update quota if deleting public world
        if world_data.get('visibility') == 'public':
            user_data = storage.load_user(g.current_user.user_id)
            user = User.from_dict(user_data)
            user.decrement_public_worlds()
            storage.save_user(user.to_dict())

        # TODO: Implement cascade delete for stories, entities, locations, events
        storage.delete_world(world_id)
        flush_data()

        return jsonify({'message': 'World deleted successfully'}), 200

    @world_bp.route('/api/worlds/<world_id>/stories', methods=['GET'])
    @optional_auth
    def world_stories(world_id):
        """Get all stories in a world."""
        world_data = storage.load_world(world_id)
        if not world_data:
            return jsonify({'error': 'World not found'}), 404
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        stories = storage.list_stories(world_id, user_id=user_id)
        return jsonify(stories)

    @world_bp.route('/api/worlds/<world_id>/characters', methods=['GET'])
    def world_characters(world_id):
        """Get all characters in a world (excluding dangerous creatures)."""
        world_data = storage.load_world(world_id)
        if not world_data:
            return jsonify({'error': 'World not found'}), 404

        entities = []
        for ent_id in world_data.get('entities', []):
            ent_data = storage.load_entity(ent_id)
            if ent_data:
                entity_type = ent_data.get('entity_type', '')
                if entity_type not in ['dragon', 'demon', 'monster']:
                    entities.append({
                        **ent_data,
                        'display': CharacterService.format_character_display(ent_data)
                    })
        return jsonify(entities)

    @world_bp.route('/api/worlds/<world_id>/locations', methods=['GET'])
    def world_locations(world_id):
        """Get all locations in a world."""
        world_data = storage.load_world(world_id)
        if not world_data:
            return jsonify({'error': 'World not found'}), 404

        locations = []
        for loc_id in world_data.get('locations', []):
            loc_data = storage.load_location(loc_id)
            if loc_data:
                locations.append(loc_data)
        return jsonify(locations)

    @world_bp.route('/api/worlds/<world_id>/entities/<entity_id>', methods=['DELETE'])
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
            return jsonify({'error': 'World not found'}), 404

        entity_data = storage.load_entity(entity_id)
        if not entity_data:
            return jsonify({'error': 'Entity not found'}), 404

        # Remove entity from world's entity list
        if entity_id in world_data.get('entities', []):
            world_data['entities'].remove(entity_id)
            storage.save_world(world_data)

        # Remove entity from all stories in this world
        stories = storage.list_stories(world_id)
        for story_data in stories:
            if entity_id in story_data.get('entities', []):
                story_data['entities'].remove(entity_id)
                storage.save_story(story_data)

        # Delete the entity itself
        storage.delete_entity(entity_id)
        flush_data()

        return jsonify({
            'message': 'Entity deleted successfully',
            'entity_id': entity_id
        }), 200

    @world_bp.route('/api/worlds/<world_id>/locations/<location_id>', methods=['DELETE'])
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
            return jsonify({'error': 'World not found'}), 404

        location_data = storage.load_location(location_id)
        if not location_data:
            return jsonify({'error': 'Location not found'}), 404

        # Remove location from world's location list
        if location_id in world_data.get('locations', []):
            world_data['locations'].remove(location_id)
            storage.save_world(world_data)

        # Remove location from all stories in this world
        stories = storage.list_stories(world_id)
        for story_data in stories:
            if location_id in story_data.get('locations', []):
                story_data['locations'].remove(location_id)
                storage.save_story(story_data)

        # Delete the location itself
        storage.delete_location(location_id)
        flush_data()

        return jsonify({
            'message': 'Location deleted successfully',
            'location_id': location_id
        }), 200

    @world_bp.route('/api/worlds/<world_id>/relationships', methods=['GET'])
    def world_relationships(world_id):
        """Get relationship diagram for a world."""
        from core.models import Story, Entity as EntityModel

        world_data = storage.load_world(world_id)
        if not world_data:
            return jsonify({'error': 'World not found'}), 404

        stories = storage.list_stories(world_id)
        entities = []
        for ent_id in world_data.get('entities', []):
            ent_data = storage.load_entity(ent_id)
            if ent_data:
                entities.append(EntityModel.from_dict(ent_data))

        svg_content = diagram_generator.generate_svg(
            entities=entities,
            stories=[Story.from_dict(s) for s in stories]
        )
        return jsonify({'svg': svg_content})

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
        from core.models import Story
        from generators import StoryLinker

        world_data = storage.load_world(world_id)
        if not world_data:
            return jsonify({'error': 'World not found'}), 404

        # Load all stories in this world (with user context for permission filtering)
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        stories_data = storage.list_stories(world_id, user_id=user_id)
        if len(stories_data) < 2:
            return jsonify({
                'message': 'Cần ít nhất 2 câu chuyện để liên kết',
                'linked_count': 0,
                'links': []
            })

        # Convert to Story objects
        stories = [Story.from_dict(s) for s in stories_data]

        # Use StoryLinker to find and create links
        linker = StoryLinker()
        linker.link_stories(stories, link_by_entities=True, link_by_locations=True, link_by_time=False)

        # Collect all links and save stories
        all_links = []
        linked_count = 0

        for story in stories:
            if story.linked_stories:
                linked_count += 1
                # Save updated story
                storage.save_story(story.to_dict())

                # Record links for response
                for linked_id in story.linked_stories:
                    linked_story = next((s for s in stories if s.story_id == linked_id), None)
                    if linked_story:
                        link_info = {
                            'from_id': story.story_id,
                            'from_title': story.title,
                            'to_id': linked_id,
                            'to_title': linked_story.title
                        }
                        # Avoid duplicate links (A->B and B->A)
                        reverse_exists = any(
                            l['from_id'] == linked_id and l['to_id'] == story.story_id
                            for l in all_links
                        )
                        if not reverse_exists:
                            all_links.append(link_info)

        flush_data()

        # Identify unlinked stories (no entities AND no locations)
        unlinked_stories = []
        for story in stories:
            if not story.entities and not story.locations:
                unlinked_stories.append({
                    'story_id': story.story_id,
                    'title': story.title,
                    'time_index': story.metadata.get('world_time', {}).get('year', 0) if story.metadata else 0,
                    'description': story.content[:200] if story.content else ''
                })

        # Sort unlinked stories by time_index
        unlinked_stories.sort(key=lambda s: s['time_index'])

        return jsonify({
            'message': f'Đã liên kết {linked_count} câu chuyện',
            'linked_count': linked_count,
            'links': all_links,
            'unlinked_stories': unlinked_stories
        })

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
            return jsonify({'error': 'World not found'}), 404

        # Check share permission (owner only)
        if not PermissionService.can_share(g.current_user.user_id, world_data):
            return jsonify({'error': 'Chỉ chủ sở hữu mới có thể chia sẻ'}), 403

        # Can only share private worlds
        if world_data.get('visibility') == 'public':
            return jsonify({'error': 'Thế giới công khai không cần chia sẻ'}), 400

        data = request.json
        user_ids = data.get('user_ids', [])

        # Validate user IDs exist
        for user_id in user_ids:
            if not storage.load_user(user_id):
                return jsonify({'error': f'User {user_id} không tồn tại'}), 400

        # Update shared_with list (avoid duplicates)
        current_shared = world_data.get('shared_with', [])
        for user_id in user_ids:
            if user_id not in current_shared:
                current_shared.append(user_id)

        world_data['shared_with'] = current_shared
        storage.save_world(world_data)
        flush_data()

        return jsonify({
            'message': 'Đã chia sẻ thế giới',
            'shared_with': current_shared
        })

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
            return jsonify({'error': 'World not found'}), 404

        # Check permission
        if not PermissionService.can_share(g.current_user.user_id, world_data):
            return jsonify({'error': 'Chỉ chủ sở hữu mới có thể quản lý quyền truy cập'}), 403

        data = request.json
        user_ids = data.get('user_ids', [])

        # Remove from shared_with list
        current_shared = world_data.get('shared_with', [])
        world_data['shared_with'] = [uid for uid in current_shared if uid not in user_ids]

        storage.save_world(world_data)
        flush_data()

        return jsonify({
            'message': 'Đã xóa quyền truy cập',
            'shared_with': world_data['shared_with']
        })

    return world_bp
