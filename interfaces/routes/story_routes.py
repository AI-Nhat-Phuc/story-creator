"""Story routes for the API backend."""

from flask import Blueprint, request, jsonify
from core.models.world import World
from core.models.entity import Entity
from core.models.location import Location
from services.character_service import CharacterService
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

    @story_bp.route('/api/stories', methods=['GET', 'POST'])
    def stories_endpoint():
        """List all stories or create new story.
        ---
        tags:
          - Stories
        parameters:
          - in: body
            name: body
            required: false
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
                time_index:
                  type: integer
                  minimum: 0
                  maximum: 100
                  example: 10
        responses:
          200:
            description: List of all stories
          201:
            description: Story created successfully
          400:
            description: Invalid input
          404:
            description: World not found
        """
        if request.method == 'GET':
            # Get all stories across all worlds
            all_stories = []
            worlds = storage.list_worlds()
            for world in worlds:
                stories = storage.list_stories(world['world_id'])
                all_stories.extend(stories)
            return jsonify(all_stories)

        elif request.method == 'POST':
            data = request.json
            world_id = data.get('world_id')
            title = data.get('title', 'Untitled Story')
            description = data.get('description', '')
            genre = data.get('genre', 'adventure')
            time_index = data.get('time_index', 0)
            selected_characters = data.get('selected_characters', None)

            world_data = storage.load_world(world_id)
            if not world_data:
                return jsonify({'error': 'World not found'}), 404

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
                  entity_type='character',
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
              # Auto-detect mentioned characters
              entity_data_list = []
              for ent_id in world.entities:
                ent_data = storage.load_entity(ent_id)
                if ent_data:
                  entity_data_list.append(ent_data)
              _, mentioned_entity_ids = CharacterService.detect_mentioned_characters(
                description, entity_data_list
              )
              linked_entities = mentioned_entity_ids or (
                [world.entities[0]] if world.entities else []
              )

            # Generate story
            story = story_generator.generate(
                title,
                description,
                world.world_id,
                genre,
                locations=world.locations[:1] if world.locations else None,
                entities=linked_entities
            )

            # Set world time based on time_index
            calendar = world.metadata.get('calendar', {})
            if calendar:
                # Map time_index (0-100) to world's timeline
                # time_index None or 0 = year 0 (special "unknown time")
                # time_index 50 = current_year
                # time_index 100 = current_year + 50
                if time_index is None or time_index == 0:
                    # Year 0 - use special name
                    year_zero_name = calendar.get('year_zero_name', 'Thời kỳ hỗn độn')
                    story.metadata['world_time'] = {
                        'era': calendar.get('current_era', 'Kỷ nguyên mới'),
                        'year': 0,
                        'month': 0,
                        'day': 0,
                        'description': year_zero_name
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
            flush_data()

            return jsonify({
              'story': story.to_dict(),
              'time_cone': time_cone.to_dict()
            }), 201

    @story_bp.route('/api/stories/<story_id>', methods=['GET', 'PUT', 'DELETE'])
    def story_detail(story_id):
        """Get, update or delete a specific story."""
        if request.method == 'GET':
            story_data = storage.load_story(story_id)
            if not story_data:
                return jsonify({'error': 'Story not found'}), 404
            return jsonify(story_data)

        elif request.method == 'PUT':
            story_data = storage.load_story(story_id)
            if not story_data:
                return jsonify({'error': 'Story not found'}), 404

            data = request.json
            # Update allowed fields
            if 'title' in data:
                story_data['title'] = data['title']
            if 'content' in data:
                story_data['content'] = data['content']
            # Support both 'content' and 'description' for backwards compatibility
            if 'description' in data and 'content' not in data:
                story_data['content'] = data['description']

            # Save updated story
            storage.save_story(story_data)
            flush_data()

            return jsonify(story_data), 200

        elif request.method == 'DELETE':
            # TODO: Implement delete
            return jsonify({'message': 'Delete not implemented'}), 501

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
                else:
                    # Create new entity
                    entity = Entity(
                        name=char_name,
                        entity_type='character',
                        description=f"{char_role} trong câu chuyện",
                        world_id=world_id
                    )
                    storage.save_entity(entity.to_dict())
                    created_entities.append(entity.entity_id)
                    linked_entities.append(entity.entity_id)
                    # Add to existing list to prevent duplicates in same request
                    existing_entities.append(entity.to_dict())

                    # Add to world if available
                    if world_data and entity.entity_id not in world_data.get('entities', []):
                        if 'entities' not in world_data:
                            world_data['entities'] = []
                        world_data['entities'].append(entity.entity_id)

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
                else:
                    # Create new location
                    location = Location(
                        name=loc_name,
                        description=loc_desc,
                        world_id=world_id,
                        coordinates={'x': random.randint(0, 100), 'y': random.randint(0, 100)}
                    )
                    storage.save_location(location.to_dict())
                    created_locations.append(location.location_id)
                    linked_locations.append(location.location_id)
                    # Add to existing list to prevent duplicates in same request
                    existing_locations.append(location.to_dict())

                    # Add to world if available
                    if world_data and location.location_id not in world_data.get('locations', []):
                        if 'locations' not in world_data:
                            world_data['locations'] = []
                        world_data['locations'].append(location.location_id)

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
