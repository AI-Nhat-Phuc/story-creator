# Flow Summary — collaborator_routes.py

> **Status**: PENDING APPROVAL
> **File**: api/interfaces/routes/collaborator_routes.py
> **Sub-task**: SUB-2 — Co-Author Permissions
> **Date**: 2026-03-31

---

## Current Flow

**New file — does not exist yet.**

---

## Planned Endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/api/worlds/<world_id>/collaborators` | owner | Invite user as co_author |
| GET | `/api/worlds/<world_id>/collaborators` | required | List co-authors |
| DELETE | `/api/worlds/<world_id>/collaborators/<coauthor_id>` | owner | Revoke co-author |
| GET | `/api/users/me/invitations` | required | List my pending invitations |
| POST | `/api/users/me/invitations/<id>/accept` | invitee | Accept invitation → adds to world.co_authors |
| POST | `/api/users/me/invitations/<id>/decline` | invitee | Decline invitation |

## Execution Steps (invite flow)

1. `@token_required` — validates JWT
2. `@validate_request(AddCollaboratorSchema)` — validates `username_or_email`, `role`
3. Load world → 404 if missing
4. Check `owner_id == current_user` → 403 if not owner (BR-2.1)
5. Resolve invitee by username or email → 404 if not found (EC-2.1)
6. Guard: invitee == owner → 400 (EC-2.2)
7. Guard: already in `co_authors` → 409 (BR-2.4)
8. Guard: pending invitation exists → 409
9. Guard: `len(co_authors) >= 10` → 400 (BR-2.2)
10. Create `Invitation` model, `storage.save_invitation()`, `flush_data()`
11. Return `201 { invitation_id, invitee, world_id }`

## Execution Steps (accept flow)

1. `@token_required`
2. Load invitation → 404 if missing or not for this user
3. Load world → 404 if deleted (EC-2.3)
4. Append `user_id` to `world.co_authors`, save world
5. Set `invitation.status = 'accepted'`, save invitation
6. Return `200`

## Planned Changes

**Will add:** all 6 endpoints above, `create_collaborator_bp(storage, flush_data)` factory.

**Will NOT change:** any existing route file.
