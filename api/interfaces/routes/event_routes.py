"""Event timeline routes for the API backend."""

from flask import Blueprint, request, jsonify
import uuid
import threading


def create_event_bp(storage, event_service, gpt_results, has_gpt):
    """Create and configure the Event blueprint.

    Args:
        storage: Storage instance
        event_service: EventService instance
        gpt_results: Shared dict to store GPT task results
        has_gpt: Boolean indicating if GPT is available

    Returns:
        Blueprint: Configured Flask blueprint for event routes
    """
    event_bp = Blueprint('events', __name__)

    @event_bp.route('/api/worlds/<world_id>/events', methods=['GET'])
    def get_world_timeline(world_id):
        """Get timeline events for a world.
        ---
        tags:
          - Events
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
            description: World ID
        responses:
          200:
            description: Timeline data with events grouped by year
          404:
            description: World not found
        """
        world = storage.load_world(world_id)
        if not world:
            return jsonify({'error': 'World not found'}), 404

        timeline = event_service.build_timeline(world_id)
        return jsonify(timeline)

    @event_bp.route('/api/worlds/<world_id>/events/extract', methods=['POST'])
    def extract_world_events(world_id):
        """Extract events from all stories in a world using GPT.
        ---
        tags:
          - Events
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - in: query
            name: force
            type: boolean
            required: false
            description: Force re-analysis (bypass cache)
        responses:
          200:
            description: Extraction task created
          404:
            description: World not found
          503:
            description: GPT not available
        """
        if not has_gpt:
            return jsonify({'error': 'GPT not available'}), 503

        world = storage.load_world(world_id)
        if not world:
            return jsonify({'error': 'World not found'}), 404

        force = request.args.get('force', 'false').lower() == 'true'

        # Get all stories for this world
        stories = storage.list_stories(world_id)
        if not stories:
            return jsonify({'error': 'No stories found in this world'}), 400

        task_id = str(uuid.uuid4())
        gpt_results[task_id] = {
            'status': 'pending',
            'total_stories': len(stories)
        }

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

        # Use new combined extraction method
        event_service.extract_events_from_world(
            world_id,
            force=force,
            callback_success=on_success,
            callback_error=on_error
        )

        return jsonify({
            'task_id': task_id,
            'status': 'pending',
            'message': f'Đang phân tích {len(stories)} câu chuyện trong 1 prompt...'
        })

    @event_bp.route('/api/stories/<story_id>/events/extract', methods=['POST'])
    def extract_story_events(story_id):
        """Extract events from a single story using GPT.
        ---
        tags:
          - Events
        parameters:
          - name: story_id
            in: path
            type: string
            required: true
          - in: query
            name: force
            type: boolean
            required: false
            description: Force re-analysis (bypass cache)
        responses:
          200:
            description: Extraction task created
          404:
            description: Story not found
          503:
            description: GPT not available
        """
        if not has_gpt:
            return jsonify({'error': 'GPT not available'}), 503

        story = storage.load_story(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404

        force = request.args.get('force', 'false').lower() == 'true'

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

        event_service.extract_events_from_story(
            story_id,
            force=force,
            callback_success=on_success,
            callback_error=on_error
        )

        return jsonify({
            'task_id': task_id,
            'status': 'pending',
            'message': f'Đang phân tích câu chuyện...'
        })

    @event_bp.route('/api/stories/<story_id>/events/cache', methods=['DELETE'])
    def clear_story_event_cache(story_id):
        """Clear GPT analysis cache for a story.
        ---
        tags:
          - Events
        parameters:
          - name: story_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Cache cleared
          404:
            description: Story not found
        """
        story = storage.load_story(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404

        deleted = event_service.clear_story_cache(story_id)
        return jsonify({
            'success': True,
            'cache_cleared': deleted,
            'message': 'Cache đã được xóa' if deleted else 'Không có cache để xóa'
        })

    @event_bp.route('/api/events/<event_id>', methods=['PUT'])
    def update_event(event_id):
        """Update an event.
        ---
        tags:
          - Events
        parameters:
          - name: event_id
            in: path
            type: string
            required: true
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                title:
                  type: string
                description:
                  type: string
                year:
                  type: integer
                era:
                  type: string
        responses:
          200:
            description: Event updated
          404:
            description: Event not found
        """
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        existing = storage.load_event(event_id)
        if not existing:
            return jsonify({'error': 'Event not found'}), 404

        # Only allow updating specific fields
        allowed_fields = ['title', 'description', 'year', 'era', 'story_position',
                          'characters', 'locations', 'connections', 'metadata']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        success = storage.update_event(event_id, update_data)
        if success:
            updated = storage.load_event(event_id)
            if hasattr(storage, 'flush'):
                storage.flush()
            return jsonify({'success': True, 'event': updated})
        return jsonify({'error': 'Failed to update event'}), 500

    @event_bp.route('/api/events/<event_id>', methods=['DELETE'])
    def delete_event(event_id):
        """Delete an event.
        ---
        tags:
          - Events
        parameters:
          - name: event_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Event deleted
          404:
            description: Event not found
        """
        existing = storage.load_event(event_id)
        if not existing:
            return jsonify({'error': 'Event not found'}), 404

        success = storage.delete_event(event_id)
        if success:
            if hasattr(storage, 'flush'):
                storage.flush()
            return jsonify({'success': True, 'message': 'Event đã được xóa'})
        return jsonify({'error': 'Failed to delete event'}), 500

    @event_bp.route('/api/events/<event_id>/connections', methods=['POST'])
    def add_event_connection(event_id):
        """Add a connection between events.
        ---
        tags:
          - Events
        parameters:
          - name: event_id
            in: path
            type: string
            required: true
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                target_event_id:
                  type: string
                  required: true
                relation_type:
                  type: string
                  enum: [character, location, causation, temporal]
                relation_label:
                  type: string
        responses:
          200:
            description: Connection added
          400:
            description: Invalid input
          404:
            description: Event not found
        """
        data = request.json
        if not data or 'target_event_id' not in data:
            return jsonify({'error': 'target_event_id is required'}), 400

        existing = storage.load_event(event_id)
        if not existing:
            return jsonify({'error': 'Source event not found'}), 404

        target = storage.load_event(data['target_event_id'])
        if not target:
            return jsonify({'error': 'Target event not found'}), 404

        # Add connection
        connections = existing.get('connections', [])
        new_conn = {
            'target_event_id': data['target_event_id'],
            'relation_type': data.get('relation_type', 'temporal'),
            'relation_label': data.get('relation_label', '')
        }

        # Avoid duplicates
        for c in connections:
            if (c.get('target_event_id') == new_conn['target_event_id'] and
                    c.get('relation_type') == new_conn['relation_type']):
                return jsonify({'success': True, 'message': 'Connection already exists'})

        connections.append(new_conn)
        storage.update_event(event_id, {'connections': connections})

        if hasattr(storage, 'flush'):
            storage.flush()

        return jsonify({'success': True, 'connection': new_conn})

    return event_bp
