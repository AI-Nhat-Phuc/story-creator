"""World management routes."""

from flask import Blueprint, request, jsonify, current_app
from core.models import World, Entity, Location
from services import CharacterService


def create_world_bp(storage, world_generator, diagram_generator, flush_data):
    """Create world blueprint with dependencies."""

    world_bp = Blueprint('worlds', __name__)

    @world_bp.route('/api/worlds', methods=['GET', 'POST'])
    def worlds_endpoint():
        """List all worlds or create new world.
        ---
        tags:
          - Worlds
        parameters:
          - in: body
            name: body
            required: false
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
                gpt_entities:
                  type: object
                  description: GPT analysis result (optional)
        responses:
          200:
            description: List of worlds
          201:
            description: World created successfully
          400:
            description: Invalid input
        """
        if request.method == 'GET':
            worlds = storage.list_worlds()
            return jsonify(worlds)

        elif request.method == 'POST':
            data = request.json
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
            flush_data()

            return jsonify(world.to_dict()), 201

    @world_bp.route('/api/worlds/<world_id>', methods=['GET', 'PUT', 'DELETE'])
    def world_detail(world_id):
        """Get, update or delete a specific world.
        ---
        tags:
          - Worlds
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
            description: World UUID
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
        responses:
          200:
            description: World details or update success
          404:
            description: World not found
        """
        if request.method == 'GET':
            world_data = storage.load_world(world_id)
            if not world_data:
                return jsonify({'error': 'World not found'}), 404
            return jsonify(world_data)

        elif request.method == 'PUT':
            world_data = storage.load_world(world_id)
            if not world_data:
                return jsonify({'error': 'World not found'}), 404

            data = request.json
            if 'name' in data:
                world_data['name'] = data['name']
            if 'description' in data:
                world_data['description'] = data['description']

            storage.save_world(world_data)
            flush_data()

            return jsonify(world_data), 200

        elif request.method == 'DELETE':
            world_data = storage.load_world(world_id)
            if not world_data:
                return jsonify({'error': 'World not found'}), 404
            return jsonify({'message': 'Delete not fully implemented'}), 501

    @world_bp.route('/api/worlds/<world_id>/stories', methods=['GET'])
    def world_stories(world_id):
        """Get all stories in a world."""
        world_data = storage.load_world(world_id)
        if not world_data:
            return jsonify({'error': 'World not found'}), 404
        stories = storage.list_stories(world_id)
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

        # Load all stories in this world
        stories_data = storage.list_stories(world_id)
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

        return jsonify({
            'message': f'Đã liên kết {linked_count} câu chuyện',
            'linked_count': linked_count,
            'links': all_links
        })

    return world_bp
