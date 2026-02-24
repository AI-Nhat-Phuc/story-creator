"""Stats routes for the API backend."""

from flask import Blueprint, jsonify, g
from interfaces.auth_middleware import optional_auth


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
    @optional_auth
    def stats():
        """Get system statistics with privacy breakdown.
        ---
        tags:
          - Stats
        parameters:
          - in: header
            name: Authorization
            type: string
            required: false
            description: "Bearer {token} (optional)"
        responses:
          200:
            description: System statistics with privacy breakdown
            schema:
              type: object
              properties:
                total_worlds:
                  type: integer
                  description: Total worlds visible to user
                total_stories:
                  type: integer
                total_entities:
                  type: integer
                total_locations:
                  type: integer
                breakdown:
                  type: object
                  description: Privacy breakdown (only for authenticated users)
                  properties:
                    worlds:
                      type: object
                    stories:
                      type: object
                user_quota:
                  type: object
                  description: User quota info (only for authenticated users)
                has_gpt:
                  type: boolean
                storage_type:
                  type: string
        """
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None

        # Use efficient count methods instead of loading full documents
        worlds_counts = storage.count_visible('worlds', user_id=user_id)
        stories_counts = storage.count_visible('stories', user_id=user_id)

        # Get entity/location counts (lightweight)
        stats_data = storage.get_stats()

        # Get minimal worlds list for dashboard dropdown (avoids extra API call)
        worlds_summary = storage.list_worlds_summary(user_id=user_id)

        result = {
            'total_worlds': worlds_counts['total'],
            'total_stories': stories_counts['total'],
            'total_entities': stats_data.get('entities', 0),
            'total_locations': stats_data.get('locations', 0),
            'has_gpt': has_gpt,
            'storage_type': type(storage).__name__,
            'worlds_summary': worlds_summary
        }

        # Add breakdown for authenticated users
        if user_id:
            user_data = storage.load_user(user_id)

            result['breakdown'] = {
                'worlds': {
                    'private': worlds_counts.get('private', 0),
                    'shared': worlds_counts.get('shared', 0),
                    'public': worlds_counts['public']
                },
                'stories': {
                    'private': stories_counts.get('private', 0),
                    'shared': stories_counts.get('shared', 0),
                    'public': stories_counts['public']
                }
            }

            # Add user quota info
            if user_data:
                result['user_quota'] = {
                    'worlds': {
                        'current': user_data.get('metadata', {}).get('public_worlds_count', 0),
                        'limit': user_data.get('metadata', {}).get('public_worlds_limit', 1)
                    },
                    'stories': {
                        'current': user_data.get('metadata', {}).get('public_stories_count', 0),
                        'limit': user_data.get('metadata', {}).get('public_stories_limit', 20)
                    }
                }
        else:
            # Anonymous user - only public data
            result['breakdown'] = {
                'worlds': {
                    'public': worlds_counts['public']
                },
                'stories': {
                    'public': stories_counts['public']
                }
            }

        return jsonify(result)

    return stats_bp
