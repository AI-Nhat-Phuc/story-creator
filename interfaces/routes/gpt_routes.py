"""GPT routes for the API backend."""

from flask import Blueprint, request, jsonify
import uuid
import threading


def create_gpt_bp(gpt, gpt_service, gpt_results, has_gpt):
    """Create and configure the GPT blueprint.

    Args:
        gpt: GPT integration instance
        gpt_service: GPTService instance for async operations
        gpt_results: Shared dict to store GPT task results
        has_gpt: Boolean indicating if GPT is available

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

    return gpt_bp
