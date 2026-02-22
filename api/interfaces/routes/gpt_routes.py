"""GPT routes for the API backend."""

from flask import Blueprint, request, jsonify
import uuid
import threading


def create_gpt_bp(gpt, gpt_service, gpt_results, has_gpt, storage=None, flush_data=None):
    """Create and configure the GPT blueprint.

    Args:
        gpt: GPT integration instance
        gpt_service: GPTService instance for async operations
        gpt_results: Shared dict to store GPT task results
        has_gpt: Boolean indicating if GPT is available
        storage: Storage instance for database access (optional, needed for batch analyze)
        flush_data: Function to flush data to disk (optional)

    Returns:
        Blueprint: Configured Flask blueprint for GPT routes
    """
    gpt_bp = Blueprint('gpt', __name__)

    @gpt_bp.route('/api/gpt/generate-description', methods=['POST'])
    def gpt_generate_description():
        """Generate world or story description with GPT.
        ---
        tags:
          - GPT
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                type:
                  type: string
                  enum: [world, story]
                  example: world
                world_name:
                  type: string
                  example: "Vương quốc Eldoria"
                world_type:
                  type: string
                  enum: [fantasy, sci-fi, modern, historical]
                  example: fantasy
                story_title:
                  type: string
                  example: "Cuộc phiêu lưu của John"
                story_genre:
                  type: string
                  enum: [adventure, mystery, conflict, discovery]
                  example: adventure
                world_description:
                  type: string
                  description: World context for story generation
                characters:
                  type: string
                  description: Comma-separated character names
        responses:
          200:
            description: Generation task created
            schema:
              type: object
              properties:
                task_id:
                  type: string
          400:
            description: Invalid input
          503:
            description: GPT not available
        """
        if not has_gpt:
            return jsonify({'error': 'GPT not available'}), 503

        data = request.json
        gen_type = data.get('type', 'world')

        task_id = str(uuid.uuid4())
        gpt_results[task_id] = {'status': 'pending'}

        def generate_description():
            try:
                if gen_type == 'world':
                    world_name = data.get('world_name', '')
                    world_type = data.get('world_type', 'fantasy')

                    if not world_name:
                        gpt_results[task_id] = {
                            'status': 'error',
                            'result': 'World name is required'
                        }
                        return

                    # Generate world description using PromptTemplates
                    from ai.prompts import PromptTemplates
                    prompt = PromptTemplates.API_WORLD_DESCRIPTION_TEMPLATE.format(
                        world_type=world_type,
                        world_name=world_name
                    )

                    response = gpt.client.chat.completions.create(
                        model=gpt.model,
                        messages=[
                            {"role": "system", "content": PromptTemplates.API_WORLD_GENERATOR_SYSTEM},
                            {"role": "user", "content": prompt}
                        ],
                        max_completion_tokens=500
                    )

                    description = response.choices[0].message.content.strip()

                    # Debug logging
                    print(f"[DEBUG] Generated world description: {description[:100]}..." if len(description) > 100 else f"[DEBUG] Generated world description: {description}")

                    gpt_results[task_id] = {
                        'status': 'completed',
                        'result': {'description': description}
                    }

                elif gen_type == 'story':
                    story_title = data.get('story_title', '')
                    story_genre = data.get('story_genre', 'adventure')
                    world_desc = data.get('world_description', '')
                    characters = data.get('characters', '')

                    if not story_title:
                        gpt_results[task_id] = {
                            'status': 'error',
                            'result': 'Story title is required'
                        }
                        return

                    # Generate story description using PromptTemplates
                    from ai.prompts import PromptTemplates
                    context_parts = []
                    if world_desc:
                        context_parts.append(f"Bối cảnh thế giới: {world_desc}")
                    if characters:
                        context_parts.append(f"Nhân vật: {characters}")
                    context = "\n".join(context_parts)
                    if context:
                        context = "\n" + context + "\n"

                    prompt = PromptTemplates.API_STORY_DESCRIPTION_TEMPLATE.format(
                        story_genre=story_genre,
                        story_title=story_title,
                        context=context
                    )

                    response = gpt.client.chat.completions.create(
                        model=gpt.model,
                        messages=[
                            {"role": "system", "content": PromptTemplates.API_STORY_GENERATOR_SYSTEM},
                            {"role": "user", "content": prompt}
                        ],
                        max_completion_tokens=400
                    )

                    description = response.choices[0].message.content.strip()

                    # Debug logging
                    print(f"[DEBUG] Generated story description: {description[:100]}..." if len(description) > 100 else f"[DEBUG] Generated story description: {description}")

                    gpt_results[task_id] = {
                        'status': 'completed',
                        'result': {'story_description': description}
                    }

            except Exception as e:
                gpt_results[task_id] = {
                    'status': 'error',
                    'result': str(e)
                }

        # Run in background thread
        thread = threading.Thread(target=generate_description)
        thread.daemon = True
        thread.start()

        return jsonify({'task_id': task_id})

    @gpt_bp.route('/api/gpt/analyze', methods=['POST'])
    def gpt_analyze():
        """Analyze world or story description with GPT to extract entities and locations.
        ---
        tags:
          - GPT
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                world_description:
                  type: string
                  example: "Một vương quốc với 3 vị vua và 5 thành phố lớn"
                world_type:
                  type: string
                  enum: [fantasy, sci-fi, modern, historical]
                  example: fantasy
                story_description:
                  type: string
                  example: "Cuộc phiêu lưu của anh hùng Minh tại thành phố cổ"
                story_title:
                  type: string
                  example: "Hành trình vĩ đại"
                story_genre:
                  type: string
                  example: "adventure"
        responses:
          200:
            description: GPT analysis task created
            schema:
              type: object
              properties:
                task_id:
                  type: string
                  example: "task-uuid-123"
          400:
            description: Invalid input
          503:
            description: GPT not available
        """
        if not has_gpt:
            return jsonify({'error': 'GPT not available'}), 503

        data = request.json
        world_description = data.get('world_description', '')
        story_description = data.get('story_description', '')
        world_type = data.get('world_type', 'fantasy')
        story_title = data.get('story_title', '')
        story_genre = data.get('story_genre', '')

        # Check if analyzing world or story
        if not world_description and not story_description:
            return jsonify({'error': 'Either world_description or story_description is required'}), 400

        task_id = str(uuid.uuid4())
        gpt_results[task_id] = {'status': 'pending'}

        def on_success(result):
            gpt_results[task_id] = {
                'status': 'completed',
                'result': result
            }

        def on_error(error):
            gpt_results[task_id] = {
                'status': 'error',
                'result': str(error)
            }

        # Choose analyze method based on input
        if story_description:
            gpt_service.analyze_story_entities(
                story_description,
                story_title,
                story_genre,
                callback_success=on_success,
                callback_error=on_error
            )
        else:
            gpt_service.analyze_world_entities(
                world_description,
                world_type,
                callback_success=on_success,
                callback_error=on_error
            )

        return jsonify({'task_id': task_id})

    @gpt_bp.route('/api/gpt/results/<task_id>', methods=['GET'])
    def gpt_get_results(task_id):
        """Get GPT task results.
        ---
        tags:
          - GPT
        parameters:
          - name: task_id
            in: path
            type: string
            required: true
            description: Task UUID from analyze endpoint
        responses:
          200:
            description: Task result
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [pending, completed, error]
                result:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        type: object
                    locations:
                      type: array
                      items:
                        type: object
          404:
            description: Task not found
        """
        result = gpt_results.get(task_id)
        if not result:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(result)

    @gpt_bp.route('/api/gpt/batch-analyze-stories', methods=['POST'])
    def gpt_batch_analyze_stories():
        """Batch analyze stories with GPT, creating entities and linking them.
        Processes stories in time order, carrying character/location context forward.
        ---
        tags:
          - GPT
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - world_id
              properties:
                world_id:
                  type: string
                  description: World UUID
                story_ids:
                  type: array
                  items:
                    type: string
                  description: Optional list of story IDs to analyze (default all unlinked)
        responses:
          200:
            description: Batch analysis task created
            schema:
              type: object
              properties:
                task_id:
                  type: string
          400:
            description: Invalid input
          503:
            description: GPT not available
        """
        if not has_gpt:
            return jsonify({'error': 'GPT not available'}), 503
        if not storage:
            return jsonify({'error': 'Storage not configured for batch operations'}), 500

        data = request.json
        world_id = data.get('world_id')
        story_ids = data.get('story_ids', [])

        if not world_id:
            return jsonify({'error': 'world_id is required'}), 400

        # Limit batch size to 3 stories max
        MAX_BATCH = 3
        if len(story_ids) > MAX_BATCH:
            return jsonify({'error': f'Tối đa {MAX_BATCH} câu chuyện mỗi lần phân tích'}), 400

        # Validate world exists
        world_data = storage.load_world(world_id)
        if not world_data:
            return jsonify({'error': 'World not found'}), 404

        task_id = str(uuid.uuid4())
        gpt_results[task_id] = {'status': 'pending', 'result': {'progress': 0, 'total': 0}}

        def batch_analyze():
            try:
                from core.models import Story, Entity, Location
                from ai.prompts import PromptTemplates
                from generators import StoryLinker
                import json as json_module

                # Load stories
                stories_data = storage.list_stories(world_id)
                if story_ids:
                    stories_data = [s for s in stories_data if s.get('story_id') in story_ids]
                else:
                    # Default: only stories with no entities AND no locations
                    stories_data = [s for s in stories_data
                                    if not s.get('entities') and not s.get('locations')]

                if not stories_data:
                    gpt_results[task_id] = {
                        'status': 'completed',
                        'result': {
                            'analyzed_stories': [],
                            'total_characters_found': 0,
                            'total_locations_found': 0,
                            'message': 'Không có câu chuyện nào cần phân tích'
                        }
                    }
                    return

                # Sort by time_index (world_time year)
                def get_time_key(s):
                    wt = s.get('metadata', {}).get('world_time', {})
                    return wt.get('year', 0) if wt else 0
                stories_data.sort(key=get_time_key)

                total = len(stories_data)
                gpt_results[task_id] = {
                    'status': 'processing',
                    'result': {'progress': 0, 'total': total, 'current_story': ''}
                }

                # Load existing entities and locations in world
                existing_entities = storage.list_entities(world_id)
                existing_locations = storage.list_locations(world_id)

                # Accumulated context: known characters and locations
                known_chars = [e.get('name', '') for e in existing_entities if e.get('name')]
                known_locs = [l.get('name', '') for l in existing_locations if l.get('name')]

                analyzed_results = []
                total_chars_found = 0
                total_locs_found = 0

                for idx, story_data in enumerate(stories_data):
                    story_title = story_data.get('title', '')
                    story_desc = story_data.get('content', '')
                    story_genre = story_data.get('genre', '')
                    story_id = story_data.get('story_id')

                    # Update progress
                    gpt_results[task_id] = {
                        'status': 'processing',
                        'result': {
                            'progress': idx,
                            'total': total,
                            'current_story': story_title
                        }
                    }

                    # Build prompt with context
                    known_chars_str = ', '.join(known_chars) if known_chars else '(chưa có)'
                    known_locs_str = ', '.join(known_locs) if known_locs else '(chưa có)'

                    prompt = PromptTemplates.BATCH_ANALYZE_STORY_ENTITIES_TEMPLATE.format(
                        story_title=story_title or 'None',
                        story_genre=story_genre or 'Unknown',
                        story_description=story_desc,
                        known_characters=known_chars_str,
                        known_locations=known_locs_str
                    )

                    # Call GPT synchronously
                    response = gpt.client.chat.completions.create(
                        model=gpt.model,
                        messages=[
                            {"role": "system", "content": PromptTemplates.TEXT_ANALYZER_SYSTEM},
                            {"role": "user", "content": prompt}
                        ],
                        max_completion_tokens=500,
                        response_format={"type": "json_object"}
                    )

                    result_text = response.choices[0].message.content.strip()
                    analysis = json_module.loads(result_text)

                    characters = analysis.get('characters', [])
                    locations_found = analysis.get('locations', [])

                    # Link or create entities
                    linked_entity_ids = []
                    for char in characters:
                        char_name = char.get('name', '')
                        char_role = char.get('role', 'nhân vật')
                        if not char_name:
                            continue

                        # Check if entity already exists in world
                        existing = next(
                            (e for e in existing_entities
                             if e.get('name', '').lower() == char_name.lower()),
                            None
                        )

                        if existing:
                            entity_id = existing.get('entity_id')
                        else:
                            # Create new entity
                            new_entity = Entity(
                                name=char_name,
                                entity_type='character',
                                world_id=world_id
                            )
                            new_entity.description = char_role
                            entity_dict = new_entity.to_dict()
                            storage.save_entity(entity_dict)
                            existing_entities.append(entity_dict)
                            entity_id = new_entity.entity_id

                            # Add to known chars for future stories
                            if char_name not in known_chars:
                                known_chars.append(char_name)

                        if entity_id not in linked_entity_ids:
                            linked_entity_ids.append(entity_id)

                    # Link or create locations
                    linked_location_ids = []
                    for loc in locations_found:
                        loc_name = loc.get('name', '')
                        loc_desc = loc.get('description', '')
                        if not loc_name:
                            continue

                        existing = next(
                            (l for l in existing_locations
                             if l.get('name', '').lower() == loc_name.lower()),
                            None
                        )

                        if existing:
                            location_id = existing.get('location_id')
                        else:
                            # Create new location
                            new_location = Location(
                                name=loc_name,
                                world_id=world_id
                            )
                            new_location.description = loc_desc
                            loc_dict = new_location.to_dict()
                            storage.save_location(loc_dict)
                            existing_locations.append(loc_dict)
                            location_id = new_location.location_id

                            if loc_name not in known_locs:
                                known_locs.append(loc_name)

                        if location_id not in linked_location_ids:
                            linked_location_ids.append(location_id)

                    # Update story with linked entities/locations
                    if 'entities' not in story_data:
                        story_data['entities'] = []
                    if 'locations' not in story_data:
                        story_data['locations'] = []

                    for eid in linked_entity_ids:
                        if eid not in story_data['entities']:
                            story_data['entities'].append(eid)
                    for lid in linked_location_ids:
                        if lid not in story_data['locations']:
                            story_data['locations'].append(lid)

                    storage.save_story(story_data)

                    total_chars_found += len(characters)
                    total_locs_found += len(locations_found)

                    analyzed_results.append({
                        'story_id': story_id,
                        'story_title': story_title,
                        'characters': characters,
                        'locations': locations_found,
                        'linked_entity_ids': linked_entity_ids,
                        'linked_location_ids': linked_location_ids
                    })

                # After all stories analyzed, run StoryLinker
                all_stories_data = storage.list_stories(world_id)
                all_stories = [Story.from_dict(s) for s in all_stories_data]
                linker = StoryLinker()
                linker.link_stories(all_stories, link_by_entities=True, link_by_locations=True, link_by_time=False)

                linked_count = 0
                for story in all_stories:
                    if story.linked_stories:
                        linked_count += 1
                        storage.save_story(story.to_dict())

                if flush_data:
                    flush_data()

                gpt_results[task_id] = {
                    'status': 'completed',
                    'result': {
                        'analyzed_stories': analyzed_results,
                        'total_characters_found': total_chars_found,
                        'total_locations_found': total_locs_found,
                        'linked_count': linked_count,
                        'message': f'Đã phân tích {total} câu chuyện, tìm thấy {total_chars_found} nhân vật và {total_locs_found} địa điểm, liên kết {linked_count} câu chuyện'
                    }
                }

            except Exception as e:
                gpt_results[task_id] = {
                    'status': 'error',
                    'result': str(e)
                }

        thread = threading.Thread(target=batch_analyze, daemon=True)
        thread.start()

        return jsonify({'task_id': task_id})

    return gpt_bp
