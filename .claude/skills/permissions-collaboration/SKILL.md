---
name: permissions-collaboration
description: Use this skill when editing code related to world ownership, co-authors, invitations, or any per-resource permission checks. Covers the "two-novelist" collaboration model — world owner invites co-authors who can edit stories/entities but cannot delete the world or change visibility. Triggers when editing api/services/permission_service.py, api/core/models/world.py, api/core/models/invitation.py, api/interfaces/routes/world_routes.py, collaborator or invitation routes, and frontend containers/components in worldDetail/ or InvitationsDropdown.
---

# permissions-collaboration — Co-author & Invitation Model

This skill captures the collaboration permission rules. Apply them every time you touch invitation, co-author, or world-level permission logic.

## Roles (per world)

- **owner** — the `world.owner_id`; full control including delete, visibility change, invite/revoke
- **co_author** — listed in `world.co_authors`; can create/edit/delete stories, entities, locations, events, time cones, and the novel within that world. CANNOT delete the world or change its visibility
- **viewer** — any authenticated user when `world.visibility == 'public'`; read-only
- **none** — no access for `visibility in {'draft', 'private'}` unless owner/co_author

## Data model

- `World.owner_id: str` — set on create, never changes
- `World.co_authors: list[str]` — user_ids, max 10 per world
- `Invitation` model (`api/core/models/invitation.py`):
  - `invitation_id`, `world_id`, `inviter_id`, `invitee_email` (or `invitee_id`), `status` in `{pending, accepted, declined, revoked}`, `created_at`, `responded_at`
  - One pending invitation per (world_id, invitee) — enforce uniqueness before insert

## Permission helpers

Always go through `PermissionService` — never write inline `if user_id == world.owner_id` in routes.

- `PermissionService.can_view(user_id, world)` — owner OR co_author OR public
- `PermissionService.can_edit_world_content(user_id, world)` — owner OR co_author (stories, entities, etc.)
- `PermissionService.can_manage_world(user_id, world)` — owner ONLY (delete, visibility, invite, revoke)
- `PermissionService.can_reorder_chapters(user_id, world)` — owner OR co_author

Routes raise `PermissionDeniedError('action', 'resource')` on failure. Never `return jsonify({'error': ...})`.

## API surface

- `POST   /api/worlds/:id/collaborators`         — invite (owner only, body: `{email}`)
- `GET    /api/worlds/:id/collaborators`         — list co-authors + pending invites (owner/co_author)
- `DELETE /api/worlds/:id/collaborators/:userId` — revoke (owner only)
- `GET    /api/users/me/invitations`             — list pending invites for current user
- `POST   /api/invitations/:id/accept`           — accept → adds current user to `co_authors`
- `POST   /api/invitations/:id/decline`          — decline → marks invitation declined

## Frontend pattern

- `CollaboratorsPanel` (in `components/worldDetail/`) — shows co-author list + pending invites. Invite form + remove buttons render only if `currentUser.user_id === world.owner_id`
- `InvitationsDropdown` (in Navbar) — bell icon, polls `/api/users/me/invitations`. Badge shows count; badge hidden when count is 0
- All API calls go through `collaboratorsAPI` and `invitationsAPI` wrappers in `frontend/src/services/api.js` — never call axios directly
- Role-based UI visibility: compute `isOwner`, `isCoAuthor`, `canEdit` once in the container, pass as props

## Common gotchas

- **Owner cannot be added to `co_authors`** — validate before insert
- **Inviting an existing co_author** → return 409 Conflict, don't create dup invitation
- **Invitation must be accepted** before any co-author API call — accepting writes to `world.co_authors` atomically
- **Max 10 co-authors** enforced on accept, not on invite (invites can be pending for revoked slots)
- **Revoke removes user from `co_authors` but does not delete their stories** — authored content persists, owner remains
- **Chapter reorder API silently skips** story_ids not in the target world (no 400) — prevents permission leak via id fishing
- When a world becomes `public`, anonymous users can view but still cannot edit — `can_edit_world_content` always requires authentication

## When adding a new world-scoped action

1. Decide if it's owner-only or co-author-allowed
2. Add/use a method on `PermissionService` — don't inline the check
3. Raise `PermissionDeniedError(action, resource)` on failure
4. Add a test asserting owner can, co_author can/cannot, viewer cannot
