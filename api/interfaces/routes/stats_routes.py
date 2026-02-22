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

        # Get basic stats (already filtered by permissions)
        all_worlds = storage.list_worlds(user_id=user_id)
        all_stories = storage.list_stories(user_id=user_id)

        stats_data = storage.get_stats()

        result = {
            'total_worlds': len(all_worlds),
            'total_stories': len(all_stories),
            'total_entities': stats_data.get('entities', 0),
            'total_locations': stats_data.get('locations', 0),
            'has_gpt': has_gpt,
            'storage_type': type(storage).__name__
        }

        # Add breakdown for authenticated users
        if user_id:
            user_data = storage.load_user(user_id)

            # Worlds breakdown
            worlds_private = [w for w in all_worlds if w.get('visibility') == 'private' and w.get('owner_id') == user_id]
            worlds_shared = [w for w in all_worlds if w.get('visibility') == 'private' and w.get('owner_id') != user_id and user_id in w.get('shared_with', [])]
            worlds_public = [w for w in all_worlds if w.get('visibility') == 'public']

            # Stories breakdown
            stories_private = [s for s in all_stories if s.get('visibility') == 'private' and s.get('owner_id') == user_id]
            stories_shared = [s for s in all_stories if s.get('visibility') == 'private' and s.get('owner_id') != user_id and user_id in s.get('shared_with', [])]
            stories_public = [s for s in all_stories if s.get('visibility') == 'public']

            result['breakdown'] = {
                'worlds': {
                    'private': len(worlds_private),
                    'shared': len(worlds_shared),
                    'public': len(worlds_public)
                },
                'stories': {
                    'private': len(stories_private),
                    'shared': len(stories_shared),
                    'public': len(stories_public)
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
                    'public': len(all_worlds)
                },
                'stories': {
                    'public': len(all_stories)
                }
            }

        return jsonify(result)

    return stats_bp
