"""Admin routes for user and system management."""

from flask import Blueprint, request, jsonify, g
from interfaces.auth_middleware import token_required, admin_required, moderator_required
from core.permissions import Role, Permission, ROLE_INFO, get_role_permissions, get_role_quota


def create_admin_bp(storage, auth_service):
    """Create admin blueprint."""
    admin_bp = Blueprint('admin', __name__)

    @admin_bp.route('/api/admin/users', methods=['GET'])
    @token_required
    @admin_required
    def get_all_users():
        """Get all users (admin only).
        ---
        tags:
          - Admin
        parameters:
          - in: header
            name: Authorization
            type: string
            required: true
            description: "Bearer {admin_token}"
          - in: query
            name: role
            type: string
            description: Filter by role
          - in: query
            name: search
            type: string
            description: Search by username or email
        responses:
          200:
            description: List of users
          403:
            description: Not authorized
        """
        try:
            # Get query params
            role_filter = request.args.get('role')
            search = request.args.get('search', '').lower()

            # Get all users
            users = storage.list_users()

            # Filter by role
            if role_filter:
                users = [u for u in users if u.get('role') == role_filter]

            # Search
            if search:
                users = [u for u in users if
                        search in u.get('username', '').lower() or
                        search in u.get('email', '').lower()]

            # Remove password hashes from response
            safe_users = []
            for user in users:
                user_copy = user.copy()
                user_copy.pop('password_hash', None)
                safe_users.append(user_copy)

            return jsonify({
                'success': True,
                'users': safe_users,
                'total': len(safe_users)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Lỗi: {str(e)}'
            }), 500

    @admin_bp.route('/api/admin/users/<user_id>', methods=['GET'])
    @token_required
    @moderator_required
    def get_user_detail(user_id):
        """Get user details (moderator+ only).
        ---
        tags:
          - Admin
        parameters:
          - in: path
            name: user_id
            type: string
            required: true
          - in: header
            name: Authorization
            type: string
            required: true
        responses:
          200:
            description: User details
          404:
            description: User not found
        """
        try:
            user_data = storage.load_user(user_id)
            if not user_data:
                return jsonify({
                    'success': False,
                    'message': 'Không tìm thấy user'
                }), 404

            # Remove password hash
            user_data.pop('password_hash', None)

            return jsonify({
                'success': True,
                'user': user_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Lỗi: {str(e)}'
            }), 500

    @admin_bp.route('/api/admin/users/<user_id>/role', methods=['PUT'])
    @token_required
    @admin_required
    def change_user_role(user_id):
        """Change user role (admin only).
        ---
        tags:
          - Admin
        parameters:
          - in: path
            name: user_id
            type: string
            required: true
          - in: header
            name: Authorization
            type: string
            required: true
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                role:
                  type: string
                  enum: [admin, moderator, premium, user, guest]
        responses:
          200:
            description: Role changed successfully
          400:
            description: Invalid role
          404:
            description: User not found
        """
        try:
            data = request.json
            new_role = data.get('role')

            # Validate role
            valid_roles = ['admin', 'moderator', 'premium', 'user', 'guest']
            if new_role not in valid_roles:
                return jsonify({
                    'success': False,
                    'message': f'Role không hợp lệ. Chọn: {", ".join(valid_roles)}'
                }), 400

            # Load user
            user_data = storage.load_user(user_id)
            if not user_data:
                return jsonify({
                    'success': False,
                    'message': 'Không tìm thấy user'
                }), 404

            # Prevent changing own role
            if user_id == g.current_user.user_id:
                return jsonify({
                    'success': False,
                    'message': 'Không thể thay đổi role của chính mình'
                }), 400

            # Update role
            old_role = user_data.get('role', 'user')
            user_data['role'] = new_role

            # Update quotas based on new role
            from core.models.user import User
            user = User.from_dict(user_data)
            user._init_role_quotas()

            # Save
            storage.save_user(user.to_dict())

            return jsonify({
                'success': True,
                'message': f'Đã đổi role từ {old_role} sang {new_role}',
                'user': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'role': user.role,
                    'quotas': {
                        'public_worlds_limit': user.metadata.get('public_worlds_limit'),
                        'public_stories_limit': user.metadata.get('public_stories_limit'),
                        'gpt_requests_per_day': user.metadata.get('gpt_requests_per_day')
                    }
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Lỗi: {str(e)}'
            }), 500

    @admin_bp.route('/api/admin/users/<user_id>/ban', methods=['POST'])
    @token_required
    @moderator_required
    def ban_user(user_id):
        """Ban/unban user (moderator+ only).
        ---
        tags:
          - Admin
        parameters:
          - in: path
            name: user_id
            type: string
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                banned:
                  type: boolean
                reason:
                  type: string
        responses:
          200:
            description: User ban status updated
        """
        try:
            data = request.json
            banned = data.get('banned', True)
            reason = data.get('reason', '')

            user_data = storage.load_user(user_id)
            if not user_data:
                return jsonify({
                    'success': False,
                    'message': 'Không tìm thấy user'
                }), 404

            # Prevent banning self
            if user_id == g.current_user.user_id:
                return jsonify({
                    'success': False,
                    'message': 'Không thể ban chính mình'
                }), 400

            # Prevent banning admin (moderator cannot ban admin)
            if g.current_user.role == 'moderator' and user_data.get('role') == 'admin':
                return jsonify({
                    'success': False,
                    'message': 'Moderator không thể ban admin'
                }), 403

            # Update ban status
            if 'metadata' not in user_data:
                user_data['metadata'] = {}

            user_data['metadata']['banned'] = banned
            user_data['metadata']['ban_reason'] = reason if banned else ''
            user_data['metadata']['banned_by'] = g.current_user.user_id if banned else None

            storage.save_user(user_data)

            return jsonify({
                'success': True,
                'message': f'Đã {"ban" if banned else "unban"} user {user_data.get("username")}',
                'banned': banned
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Lỗi: {str(e)}'
            }), 500

    @admin_bp.route('/api/admin/roles', methods=['GET'])
    @token_required
    @moderator_required
    def get_roles_info():
        """Get all role definitions and permissions.
        ---
        tags:
          - Admin
        responses:
          200:
            description: Role information
        """
        try:
            roles_data = []
            for role in Role:
                permissions = get_role_permissions(role.value)
                quotas = {
                    'public_worlds': get_role_quota(role.value, 'public_worlds_limit'),
                    'public_stories': get_role_quota(role.value, 'public_stories_limit'),
                    'gpt_per_day': get_role_quota(role.value, 'gpt_requests_per_day')
                }

                role_info = ROLE_INFO.get(role, {})

                roles_data.append({
                    'role': role.value,
                    'label': role_info.get('label', role.value),
                    'icon': role_info.get('icon', ''),
                    'badge_color': role_info.get('badge_color', 'badge-info'),
                    'description': role_info.get('description', ''),
                    'permissions': [p.value for p in permissions],
                    'quotas': quotas
                })

            return jsonify({
                'success': True,
                'roles': roles_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Lỗi: {str(e)}'
            }), 500

    @admin_bp.route('/api/admin/stats', methods=['GET'])
    @token_required
    @moderator_required
    def get_admin_stats():
        """Get admin statistics.
        ---
        tags:
          - Admin
        responses:
          200:
            description: Admin statistics
        """
        try:
            users = storage.list_users()

            # Count by role
            role_counts = {}
            for user in users:
                role = user.get('role', 'user')
                role_counts[role] = role_counts.get(role, 0) + 1

            # Count banned users
            banned_count = sum(1 for u in users if u.get('metadata', {}).get('banned', False))

            # Get all content counts
            all_worlds = storage.list_worlds()
            all_stories = storage.list_stories()

            return jsonify({
                'success': True,
                'stats': {
                    'total_users': len(users),
                    'role_breakdown': role_counts,
                    'banned_users': banned_count,
                    'total_worlds': len(all_worlds),
                    'total_stories': len(all_stories),
                    'public_worlds': len([w for w in all_worlds if w.get('visibility') == 'public']),
                    'private_worlds': len([w for w in all_worlds if w.get('visibility') == 'private']),
                    'public_stories': len([s for s in all_stories if s.get('visibility') == 'public']),
                    'private_stories': len([s for s in all_stories if s.get('visibility') == 'private'])
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Lỗi: {str(e)}'
            }), 500

    return admin_bp
