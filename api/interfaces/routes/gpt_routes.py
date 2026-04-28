"""GPT routes for the API backend."""

import logging
from flask import Blueprint, request, jsonify, g
from core.exceptions import (
    ResourceNotFoundError,
    ValidationError as APIValidationError,
    ExternalServiceError,
    BusinessRuleError,
    PermissionDeniedError,
)
from utils.responses import success_response
from utils.validation import validate_request
from utils.i18n import t
from interfaces.auth_middleware import token_required
from services import BatchAnalyzeService
from schemas.gpt_schemas import (
    GptParaphraseSchema,
    GenerateDescriptionSchema,
    GptAnalyzeSchema,
)
import uuid
import threading

logger = logging.getLogger(__name__)


def create_gpt_bp(backend, gpt_results, storage=None, flush_data=None, limiter=None):
    """Create and configure the GPT blueprint.

    Args:
        backend: Backend instance exposing _ensure_gpt(), has_gpt, gpt, and gpt_service
        gpt_results: Shared dict to store GPT task results
        storage: Storage instance for database access (optional, needed for batch analyze)
        flush_data: Function to flush data to disk (optional)
        limiter: Optional Flask-Limiter instance for rate limiting

    Returns:
        Blueprint: Configured Flask blueprint for GPT routes
    """
    gpt_bp = Blueprint('gpt', __name__)

    # Stricter limit on GPT endpoints to control API costs
    _gpt_limit = limiter.limit("10 per minute") if limiter else (lambda f: f)

    @gpt_bp.route('/api/gpt/generate-description', methods=['POST'])
    @_gpt_limit
    @token_required
    @validate_request(GenerateDescriptionSchema)
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
          400:
            description: Invalid input
          503:
            description: GPT not available
        """
        if not g.current_user.can_use_gpt():
            raise PermissionDeniedError('use_gpt', 'feature')

        backend._ensure_gpt()
        if not backend.has_gpt:
            raise ExternalServiceError('GPT', 'GPT not available')

        data = request.validated_data
        gen_type = data.get('type', 'world')

        task_id = str(uuid.uuid4())
        label = data.get('world_name', '') if gen_type == 'world' else data.get('story_title', '')
        gpt_results[task_id] = {
            'status': 'pending',
            'task_type': f'generate_{gen_type}_description',
            'label': f'Tạo mô tả: {label}'
        }

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

                    from ai.prompts import PromptTemplates
                    prompt = PromptTemplates.API_WORLD_DESCRIPTION_TEMPLATE.format(
                        world_type=world_type,
                        world_name=world_name
                    )

                    response = backend.gpt.client.chat.completions.create(
                        model=backend.gpt.model,
                        messages=[
                            {"role": "system", "content": PromptTemplates.API_WORLD_GENERATOR_SYSTEM},
                            {"role": "user", "content": prompt}
                        ],
                        max_completion_tokens=500
                    )

                    description = response.choices[0].message.content.strip()
                    logger.debug(
                        "Generated world description (%d chars)", len(description)
                    )

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

                    response = backend.gpt.client.chat.completions.create(
                        model=backend.gpt.model,
                        messages=[
                            {"role": "system", "content": PromptTemplates.API_STORY_GENERATOR_SYSTEM},
                            {"role": "user", "content": prompt}
                        ],
                        max_completion_tokens=400
                    )

                    description = response.choices[0].message.content.strip()
                    logger.debug(
                        "Generated story description (%d chars)", len(description)
                    )

                    gpt_results[task_id] = {
                        'status': 'completed',
                        'result': {'story_description': description}
                    }

            except Exception:
                logger.error(
                    "GPT generate-description task failed", exc_info=True
                )
                gpt_results[task_id] = {
                    'status': 'error',
                    'result': 'GPT request failed',
                }

        thread = threading.Thread(target=generate_description)
        thread.daemon = True
        thread.start()

        return jsonify({'task_id': task_id})

    @gpt_bp.route('/api/gpt/analyze', methods=['POST'])
    @_gpt_limit
    @token_required
    @validate_request(GptAnalyzeSchema)
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
          400:
            description: Invalid input
          503:
            description: GPT not available
        """
        if not g.current_user.can_use_gpt():
            raise PermissionDeniedError('use_gpt', 'feature')

        backend._ensure_gpt()
        if not backend.has_gpt:
            raise ExternalServiceError('GPT', 'GPT not available')

        data = request.validated_data
        world_description = data.get('world_description', '')
        # Accept either story_description (frontend) or story_content (legacy).
        story_description = data.get('story_description', '') or data.get('story_content', '')
        world_type = data.get('world_type', '') or 'fantasy'
        story_title = data.get('story_title', '')
        story_genre = data.get('story_genre', '')

        if not world_description and not story_description:
            raise APIValidationError(t('gpt.missing_description'))

        task_id = str(uuid.uuid4())
        label = story_title or 'thế giới'
        gpt_results[task_id] = {
            'status': 'pending',
            'task_type': 'analyze_entities',
            'label': f'Phân tích: {label}'
        }

        def on_success(result):
            gpt_results[task_id] = {'status': 'completed', 'result': result}

        def on_error(error):
            logger.error("GPT analyze task failed: %s", error, exc_info=True)
            gpt_results[task_id] = {
                'status': 'error',
                'result': 'GPT request failed',
            }

        if story_description:
            backend.gpt_service.analyze_story_entities(
                story_description, story_title, story_genre,
                callback_success=on_success, callback_error=on_error
            )
        else:
            backend.gpt_service.analyze_world_entities(
                world_description, world_type,
                callback_success=on_success, callback_error=on_error
            )

        return jsonify({'task_id': task_id})

    @gpt_bp.route('/api/gpt/results/<task_id>', methods=['GET'])
    @_gpt_limit
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
          404:
            description: Task not found
        """
        result = gpt_results.get(task_id)
        if not result:
            raise ResourceNotFoundError('Task', task_id)
        return jsonify(result)

    @gpt_bp.route('/api/gpt/batch-analyze-stories', methods=['POST'])
    @_gpt_limit
    @token_required
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
          400:
            description: Invalid input
          503:
            description: GPT not available
        """
        if not g.current_user.can_use_gpt():
            raise PermissionDeniedError('use_gpt', 'feature')

        backend._ensure_gpt()
        if not backend.has_gpt:
            raise ExternalServiceError('GPT', 'GPT not available')
        if not storage:
            raise BusinessRuleError('Storage not configured for batch operations')

        data = request.json
        world_id = data.get('world_id')
        story_ids = data.get('story_ids', [])

        if not world_id:
            raise APIValidationError(t('gpt.missing_world_id'))

        MAX_BATCH = 3
        if len(story_ids) > MAX_BATCH:
            raise BusinessRuleError(t('gpt.max_batch_exceeded', max=MAX_BATCH))

        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        task_id = str(uuid.uuid4())
        gpt_results[task_id] = {
            'status': 'pending',
            'task_type': 'batch_analyze',
            'label': f'Phân tích hàng loạt ({len(story_ids)} chuyện)',
            'result': {'progress': 0, 'total': 0}
        }

        def batch_analyze():
            try:
                total = len(story_ids) if story_ids else 0
                gpt_results[task_id] = {
                    'status': 'processing',
                    'result': {'progress': 0, 'total': total, 'current_story': ''}
                }

                def progress_callback(idx, total_count, current_title):
                    gpt_results[task_id] = {
                        'status': 'processing',
                        'result': {
                            'progress': idx,
                            'total': total_count,
                            'current_story': current_title
                        }
                    }

                service = BatchAnalyzeService(backend.gpt, storage)
                result = service.run(world_id, story_ids, progress_callback=progress_callback)

                if flush_data:
                    flush_data()

                gpt_results[task_id] = {'status': 'completed', 'result': result}

            except Exception:
                logger.error("GPT batch-analyze task failed", exc_info=True)
                gpt_results[task_id] = {
                    'status': 'error',
                    'result': 'GPT request failed',
                }

        thread = threading.Thread(target=batch_analyze, daemon=True)
        thread.start()

        return jsonify({'task_id': task_id})

    @gpt_bp.route('/api/gpt/tasks', methods=['GET'])
    def gpt_list_tasks():
        """List pending/processing GPT tasks.
        ---
        tags:
          - GPT
        parameters:
          - in: query
            name: task_ids
            type: string
            required: false
            description: Comma-separated list of task IDs to check
        responses:
          200:
            description: List of task statuses
        """
        task_ids_param = request.args.get('task_ids', '')
        if task_ids_param:
            task_ids = [t.strip() for t in task_ids_param.split(',') if t.strip()]
            tasks = [gpt_results[tid] for tid in task_ids if tid in gpt_results]
            return jsonify({'tasks': tasks})
        else:
            if hasattr(storage, 'list_pending_gpt_tasks'):
                tasks = storage.list_pending_gpt_tasks()
                return jsonify({'tasks': tasks})
            return jsonify({'tasks': []})

    @gpt_bp.route('/api/gpt/paraphrase', methods=['POST'])
    @_gpt_limit
    @token_required
    @validate_request(GptParaphraseSchema)
    def gpt_paraphrase():
        """Paraphrase or expand a text selection using GPT.
        ---
        tags:
          - GPT
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
              required:
                - text
              properties:
                text:
                  type: string
                  example: "He walked into the room."
                mode:
                  type: string
                  enum: [paraphrase, expand]
                  default: paraphrase
        responses:
          200:
            description: Three suggestions returned
          400:
            description: Invalid input
          401:
            description: Authentication required
          429:
            description: Quota exceeded
        """
        if not g.current_user.can_use_gpt():
            raise PermissionDeniedError('use_gpt', 'feature')

        data = request.validated_data
        text = data['text']
        mode = data.get('mode', 'paraphrase')

        backend._ensure_gpt()
        if not backend.has_gpt:
            # Deterministic mock for tests without an API key
            suggestions = [
                f"[mock {mode} 1] {text}",
                f"[mock {mode} 2] {text}",
                f"[mock {mode} 3] {text}",
            ]
            return success_response({'suggestions': suggestions})

        if mode == 'expand':
            system_prompt = (
                "You are a creative writing assistant. "
                "Expand the given text into a richer, more detailed version. "
                "IMPORTANT: Always respond in the same language as the input text. "
                "Return exactly 3 numbered alternatives, one per line."
            )
            user_prompt = f"Expand this passage into 3 longer alternatives:\n\n{text}"
        else:
            system_prompt = (
                "You are a creative writing assistant. "
                "Paraphrase the given text in different ways while preserving meaning. "
                "IMPORTANT: Always respond in the same language as the input text. "
                "Return exactly 3 numbered alternatives, one per line."
            )
            user_prompt = f"Paraphrase this passage in 3 different ways:\n\n{text}"

        try:
            response = backend.gpt.client.chat.completions.create(
                model=backend.gpt.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=600
            )
            raw = response.choices[0].message.content.strip()
            # Parse numbered lines: "1. ...", "2. ...", "3. ..."
            lines = [l.strip() for l in raw.splitlines() if l.strip()]
            suggestions = []
            for line in lines:
                # Strip leading number+dot
                cleaned = line.lstrip('0123456789').lstrip('.').lstrip(')').strip()
                if cleaned:
                    suggestions.append(cleaned)
            # Ensure exactly 3
            suggestions = (suggestions + [raw, raw, raw])[:3]
        except Exception:
            logger.error("GPT paraphrase failed", exc_info=True)
            raise ExternalServiceError('GPT', t('gpt.request_failed'))

        return success_response({'suggestions': suggestions})

    return gpt_bp
