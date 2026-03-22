"""Event timeline routes for the API backend."""

from flask import Blueprint, request
from core.exceptions import (
    ResourceNotFoundError,
    ExternalServiceError,
    BusinessRuleError
)
from utils.responses import success_response, deleted_response
from utils.validation import validate_request
from interfaces.auth_middleware import token_required
from schemas.event_schemas import UpdateEventSchema, AddEventConnectionSchema
import uuid


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
            raise ResourceNotFoundError('World', world_id)

        timeline = event_service.build_timeline(world_id)
        return success_response(timeline)

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
            raise ExternalServiceError('GPT', 'GPT not available')

        world = storage.load_world(world_id)
        if not world:
            raise ResourceNotFoundError('World', world_id)

        stories = storage.list_stories(world_id)
        if not stories:
            raise BusinessRuleError('No stories found in this world')

        force = request.args.get('force', 'false').lower() == 'true'

        task_id = str(uuid.uuid4())
        gpt_results[task_id] = {
            'status': 'pending',
            'total_stories': len(stories),
            'task_type': 'extract_world_events',
            'label': f'Trích xuất sự kiện: {world.get("name", "")}'
        }

        def on_success(result):
            gpt_results[task_id] = {'status': 'completed', 'result': result}

        def on_error(error):
            gpt_results[task_id] = {'status': 'error', 'result': str(error)}

        event_service.extract_events_from_world(
            world_id, force=force,
            callback_success=on_success, callback_error=on_error
        )

        return success_response({
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
            raise ExternalServiceError('GPT', 'GPT not available')

        story = storage.load_story(story_id)
        if not story:
            raise ResourceNotFoundError('Story', story_id)

        force = request.args.get('force', 'false').lower() == 'true'

        task_id = str(uuid.uuid4())
        gpt_results[task_id] = {
            'status': 'pending',
            'task_type': 'extract_story_events',
            'label': f'Trích xuất sự kiện: {story.get("title", "")}'
        }

        def on_success(result):
            gpt_results[task_id] = {'status': 'completed', 'result': result}

        def on_error(error):
            gpt_results[task_id] = {'status': 'error', 'result': str(error)}

        event_service.extract_events_from_story(
            story_id, force=force,
            callback_success=on_success, callback_error=on_error
        )

        return success_response({
            'task_id': task_id,
            'status': 'pending',
            'message': 'Đang phân tích câu chuyện...'
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
            raise ResourceNotFoundError('Story', story_id)

        deleted = event_service.clear_story_cache(story_id)
        return success_response(
            {'cache_cleared': deleted},
            'Cache đã được xóa' if deleted else 'Không có cache để xóa'
        )

    @event_bp.route('/api/events/<event_id>', methods=['PUT'])
    @token_required
    @validate_request(UpdateEventSchema)
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
        existing = storage.load_event(event_id)
        if not existing:
            raise ResourceNotFoundError('Event', event_id)

        update_data = {k: v for k, v in request.validated_data.items()}

        success = storage.update_event(event_id, update_data)
        if not success:
            raise BusinessRuleError('Failed to update event')

        updated = storage.load_event(event_id)
        if hasattr(storage, 'flush'):
            storage.flush()

        return success_response(updated, "Event updated successfully")

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
            raise ResourceNotFoundError('Event', event_id)

        success = storage.delete_event(event_id)
        if not success:
            raise BusinessRuleError('Failed to delete event')

        if hasattr(storage, 'flush'):
            storage.flush()

        return deleted_response('Event đã được xóa')

    @event_bp.route('/api/events/<event_id>/connections', methods=['POST'])
    @token_required
    @validate_request(AddEventConnectionSchema)
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
        data = request.validated_data

        existing = storage.load_event(event_id)
        if not existing:
            raise ResourceNotFoundError('Event', event_id)

        target = storage.load_event(data['target_event_id'])
        if not target:
            raise ResourceNotFoundError('Event', data['target_event_id'])

        connections = existing.get('connections', [])
        new_conn = {
            'target_event_id': data['target_event_id'],
            'relation_type': data['relation_type'],
            'relation_label': data['relation_label']
        }

        for c in connections:
            if (c.get('target_event_id') == new_conn['target_event_id'] and
                    c.get('relation_type') == new_conn['relation_type']):
                return success_response({'connection': new_conn}, 'Connection already exists')

        connections.append(new_conn)
        storage.update_event(event_id, {'connections': connections})

        if hasattr(storage, 'flush'):
            storage.flush()

        return success_response({'connection': new_conn}, "Connection added successfully")

    return event_bp
