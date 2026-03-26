"""Admin routes for user and system management."""

from flask import Blueprint, request, g
from core.exceptions import (
    ResourceNotFoundError,
    BusinessRuleError,
    PermissionDeniedError
)
from utils.responses import success_response, paginated_response
from utils.validation import validate_request, validate_query_params
from interfaces.auth_middleware import token_required, admin_required, moderator_required
from core.permissions import Role, Permission, ROLE_INFO, get_role_permissions, get_role_quota
from schemas.admin_schemas import ChangeUserRoleSchema, BanUserSchema, ListUsersQuerySchema


def create_admin_bp(storage, auth_service):
    """Create admin blueprint."""
    admin_bp = Blueprint('admin', __name__)

    @admin_bp.route('/api/admin/users', methods=['GET'])
    @token_required
    @admin_required
    @validate_query_params(ListUsersQuerySchema)
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
            name: page
            type: integer
            default: 1
          - in: query
            name: per_page
            type: integer
            default: 20
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
            description: Paginated list of users
          403:
            description: Not authorized
        """
        params = request.validated_data
        page = params.get('page', 1)
        per_page = params.get('per_page', 20)
        role_filter = params.get('role')
        search = params.get('search', '').lower()

        users = storage.list_users()

        if role_filter:
            users = [u for u in users if u.get('role') == role_filter]
        if search:
            users = [u for u in users if
                     search in u.get('username', '').lower() or
                     search in u.get('email', '').lower()]

        safe_users = [{k: v for k, v in u.items() if k != 'password_hash'} for u in users]

        total = len(safe_users)
        start = (page - 1) * per_page
        page_users = safe_users[start:start + per_page]

        return paginated_response(page_users, page, per_page, total)

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
        user_data = storage.load_user(user_id)
        if not user_data:
            raise ResourceNotFoundError('User', user_id)

        user_data.pop('password_hash', None)
        return success_response({'user': user_data})

    @admin_bp.route('/api/admin/users/<user_id>/role', methods=['PUT'])
    @token_required
    @admin_required
    @validate_request(ChangeUserRoleSchema)
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
        new_role = request.validated_data['role']

        user_data = storage.load_user(user_id)
        if not user_data:
            raise ResourceNotFoundError('User', user_id)

        if user_id == g.current_user.user_id:
            raise BusinessRuleError('Không thể thay đổi role của chính mình')

        old_role = user_data.get('role', 'user')
        user_data['role'] = new_role

        from core.models.user import User
        user = User.from_dict(user_data)
        user._init_role_quotas()
        storage.save_user(user.to_dict())

        return success_response({
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
        }, f'Đã đổi role từ {old_role} sang {new_role}')

    @admin_bp.route('/api/admin/users/<user_id>/ban', methods=['POST'])
    @token_required
    @moderator_required
    @validate_request(BanUserSchema)
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
        data = request.validated_data
        banned = data['banned']
        reason = data['reason']

        user_data = storage.load_user(user_id)
        if not user_data:
            raise ResourceNotFoundError('User', user_id)

        if user_id == g.current_user.user_id:
            raise BusinessRuleError('Không thể ban chính mình')

        if g.current_user.role == 'moderator' and user_data.get('role') == 'admin':
            raise PermissionDeniedError('ban admin users')

        user_data.setdefault('metadata', {})
        user_data['metadata']['banned'] = banned
        user_data['metadata']['ban_reason'] = reason if banned else ''
        user_data['metadata']['banned_by'] = g.current_user.user_id if banned else None

        storage.save_user(user_data)

        action = 'ban' if banned else 'unban'
        return success_response(
            {'banned': banned},
            f'Đã {action} user {user_data.get("username")}'
        )

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

        return success_response({'roles': roles_data})

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
        users = storage.list_users()

        role_counts = {}
        for user in users:
            role = user.get('role', 'user')
            role_counts[role] = role_counts.get(role, 0) + 1

        banned_count = sum(1 for u in users if u.get('metadata', {}).get('banned', False))
        all_worlds = storage.list_worlds()
        all_stories = storage.list_stories()

        return success_response({
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

    return admin_bp
