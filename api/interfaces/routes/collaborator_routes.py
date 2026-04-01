"""Collaborator routes — co-author invitations and world collaboration (SUB-2)."""

from flask import Blueprint, request, g
from core.models.invitation import Invitation
from core.exceptions import (
    ResourceNotFoundError,
    PermissionDeniedError,
    ConflictError,
    ValidationError as APIValidationError,
)
from interfaces.auth_middleware import token_required
from utils.responses import success_response, created_response, deleted_response
from utils.validation import validate_request
from schemas.world_schemas import AddCollaboratorSchema


def create_collaborator_bp(storage, flush_data):
    """Create collaborator blueprint."""

    collab_bp = Blueprint('collaborators', __name__)

    @collab_bp.route('/api/worlds/<world_id>/collaborators', methods=['POST'])
    @token_required
    @validate_request(AddCollaboratorSchema)
    def invite_collaborator(world_id):
        """Invite a user as co-author of a world.
        ---
        tags:
          - Collaborators
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [username_or_email]
              properties:
                username_or_email:
                  type: string
                role:
                  type: string
                  enum: [co_author]
        responses:
          201:
            description: Invitation sent
          400:
            description: Cannot invite yourself or quota reached
          404:
            description: World or user not found
          409:
            description: Already a co-author or invitation pending
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        if world_data.get('owner_id') != g.current_user.user_id:
            raise PermissionDeniedError('invite collaborators to', 'world')

        username_or_email = request.validated_data['username_or_email']

        invitee = (
            storage.find_user_by_username(username_or_email)
            or storage.find_user_by_email(username_or_email)
        )
        if not invitee:
            raise ResourceNotFoundError('User', username_or_email)

        invitee_id = invitee['user_id']

        if invitee_id == g.current_user.user_id:
            raise APIValidationError('You cannot invite yourself as a co-author')

        if invitee_id in world_data.get('co_authors', []):
            raise ConflictError('User is already a co-author of this world')

        existing_inv = storage.find_invitation(world_id, invitee_id)
        if existing_inv and existing_inv.get('status') == 'pending':
            raise ConflictError('An invitation for this user is already pending')

        if len(world_data.get('co_authors', [])) >= 10:
            raise APIValidationError('This world has reached the maximum of 10 co-authors')

        invitation = Invitation(
            world_id=world_id,
            invited_by=g.current_user.user_id,
            invitee_id=invitee_id
        )
        storage.save_invitation(invitation.to_dict())
        flush_data()

        return created_response({
            'invitation_id': invitation.invitation_id,
            'invitee': invitee.get('username'),
            'world_id': world_id
        }, "Invitation sent")

    @collab_bp.route('/api/worlds/<world_id>/collaborators', methods=['GET'])
    @token_required
    def list_collaborators(world_id):
        """List co-authors of a world.
        ---
        tags:
          - Collaborators
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: List of co-authors
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        collaborators = []
        for uid in world_data.get('co_authors', []):
            user = storage.load_user(uid)
            if user:
                collaborators.append({
                    'user_id': uid,
                    'username': user.get('username'),
                    'role': 'co_author'
                })

        return success_response(collaborators)

    @collab_bp.route('/api/worlds/<world_id>/collaborators/<coauthor_id>', methods=['DELETE'])
    @token_required
    def remove_collaborator(world_id, coauthor_id):
        """Revoke co-author access.
        ---
        tags:
          - Collaborators
        parameters:
          - name: world_id
            in: path
            type: string
            required: true
          - name: coauthor_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Co-author removed
          403:
            description: Only the owner can revoke co-authors
          404:
            description: World not found
        """
        world_data = storage.load_world(world_id)
        if not world_data:
            raise ResourceNotFoundError('World', world_id)

        if world_data.get('owner_id') != g.current_user.user_id:
            raise PermissionDeniedError('remove collaborators from', 'world')

        co_authors = world_data.get('co_authors', [])
        if coauthor_id in co_authors:
            co_authors.remove(coauthor_id)
            world_data['co_authors'] = co_authors
            storage.save_world(world_data)
            flush_data()

        return deleted_response("Co-author removed")

    @collab_bp.route('/api/users/me/invitations', methods=['GET'])
    @token_required
    def list_my_invitations():
        """List pending invitations for the current user.
        ---
        tags:
          - Collaborators
        responses:
          200:
            description: List of pending invitations
        """
        invitations = storage.list_invitations_for_user(g.current_user.user_id)
        result = []
        for inv in invitations:
            world = storage.load_world(inv.get('world_id'))
            if not world:
                continue  # EC-2.3: world deleted — skip silently
            inviter = storage.load_user(inv.get('invited_by'))
            result.append({
                'invitation_id': inv['invitation_id'],
                'world_id': inv['world_id'],
                'world_title': world.get('name'),
                'invited_by': inviter.get('username') if inviter else 'unknown',
                'created_at': inv.get('created_at')
            })
        return success_response(result)

    @collab_bp.route('/api/users/me/invitations/<invitation_id>/accept', methods=['POST'])
    @token_required
    def accept_invitation(invitation_id):
        """Accept a co-author invitation.
        ---
        tags:
          - Collaborators
        parameters:
          - name: invitation_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Invitation accepted
          404:
            description: Invitation not found
        """
        inv_data = storage.load_invitation(invitation_id)
        if not inv_data or inv_data.get('invitee_id') != g.current_user.user_id:
            raise ResourceNotFoundError('Invitation', invitation_id)

        world_data = storage.load_world(inv_data['world_id'])
        if not world_data:
            raise ResourceNotFoundError('World', inv_data['world_id'])

        co_authors = world_data.get('co_authors', [])
        if g.current_user.user_id not in co_authors:
            co_authors.append(g.current_user.user_id)
            world_data['co_authors'] = co_authors
            storage.save_world(world_data)

        inv_data['status'] = 'accepted'
        storage.save_invitation(inv_data)
        flush_data()

        return success_response({'world_id': inv_data['world_id']}, "Invitation accepted")

    @collab_bp.route('/api/users/me/invitations/<invitation_id>/decline', methods=['POST'])
    @token_required
    def decline_invitation(invitation_id):
        """Decline a co-author invitation.
        ---
        tags:
          - Collaborators
        parameters:
          - name: invitation_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Invitation declined
          404:
            description: Invitation not found
        """
        inv_data = storage.load_invitation(invitation_id)
        if not inv_data or inv_data.get('invitee_id') != g.current_user.user_id:
            raise ResourceNotFoundError('Invitation', invitation_id)

        inv_data['status'] = 'declined'
        storage.save_invitation(inv_data)
        flush_data()

        return success_response({}, "Invitation declined")

    return collab_bp
