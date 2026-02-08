"""Health check routes."""

from flask import Blueprint, jsonify, redirect


def create_health_bp(storage_label, has_gpt):
    """Create and configure the health blueprint.

    Args:
        storage_label: Human-readable storage type label
        has_gpt: Boolean indicating if GPT is available

    Returns:
        Blueprint: Configured Flask blueprint for health routes
    """
    health_bp = Blueprint('health', __name__)

    @health_bp.route('/', methods=['GET'])
    def root():
        """Redirect to Swagger UI."""
        return redirect('/api/docs', code=302)

    @health_bp.route('/api', methods=['GET'])
    def api_root():
        """Redirect to Swagger UI."""
        return redirect('/api/docs', code=302)

    @health_bp.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint.
        ---
        tags:
          - Health
        responses:
          200:
            description: Server health status
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: ok
                storage:
                  type: string
                  example: NoSQL Database
                gpt_enabled:
                  type: boolean
                  example: true
        """
        return jsonify({
            'status': 'ok',
            'storage': storage_label,
            'gpt_enabled': has_gpt
        })

    return health_bp
