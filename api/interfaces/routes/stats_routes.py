"""Stats routes for the API backend."""

from flask import Blueprint, jsonify


def create_stats_bp(storage, has_gpt):
    """Create and configure the stats blueprint.

    Args:
        storage: Storage instance for data access
        has_gpt: Boolean indicating if GPT is available

    Returns:
        Blueprint: Configured Flask blueprint for stats routes
    """
    stats_bp = Blueprint('stats', __name__)

    @stats_bp.route('/api/stats', methods=['GET'])
    def stats():
        """Get system statistics.
        ---
        tags:
          - Stats
        responses:
          200:
            description: System statistics
            schema:
              type: object
              properties:
                total_worlds:
                  type: integer
                total_stories:
                  type: integer
                total_entities:
                  type: integer
                total_locations:
                  type: integer
                has_gpt:
                  type: boolean
                storage_type:
                  type: string
        """
        stats_data = storage.get_stats()
        # Map storage keys to frontend expected keys
        return jsonify({
            'total_worlds': stats_data.get('worlds', 0),
            'total_stories': stats_data.get('stories', 0),
            'total_entities': stats_data.get('entities', 0),
            'total_locations': stats_data.get('locations', 0),
            'linked_stories': 0,  # TODO: Calculate linked stories
            'has_gpt': has_gpt,
            'storage_type': type(storage).__name__
        })

    return stats_bp
