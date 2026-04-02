# Task Spec — Co-Author Permissions (Frontend)

> Backend fully implemented in `api/interfaces/routes/collaborator_routes.py` and storage.
> This task is **frontend only**.

---

## Routes / Endpoints used

```
POST   /api/worlds/:worldId/collaborators        { username_or_email, role: 'co_author' }
GET    /api/worlds/:worldId/collaborators
DELETE /api/worlds/:worldId/collaborators/:userId

GET    /api/users/me/invitations
POST   /api/users/me/invitations/:id/accept
POST   /api/users/me/invitations/:id/decline
```

---

## Behavior

### World Detail Page — Collaborators section
- World owner sees a "Collaborators" panel listing all co-authors (username).
- Owner can invite by username/email via a small inline form.
- Owner can remove any co-author with a confirmation prompt.
- Non-owners see the collaborators list read-only (if any co-authors exist).

### Navbar — Invitations badge
- Logged-in users see a bell icon in the Navbar.
- If pending invitations exist, a numeric badge is shown.
- Clicking opens an InvitationsDropdown listing pending invitations with Accept/Decline buttons.
- After accept/decline, the invitation disappears and the badge updates.

---

## Component Tree

```
WorldDetailView
└── CollaboratorsPanel          ← NEW
    ├── collaborator list (username + remove btn for owner)
    └── InviteForm (owner only, inline)

Navbar
└── InvitationsDropdown         ← NEW (bell icon + dropdown)
```

---

## API Contract (frontend additions to api.js)

```js
collaboratorsAPI.list(worldId)                      // GET /worlds/:worldId/collaborators
collaboratorsAPI.invite(worldId, usernameOrEmail)   // POST
collaboratorsAPI.remove(worldId, userId)             // DELETE

invitationsAPI.list()                               // GET /users/me/invitations
invitationsAPI.accept(id)                           // POST /users/me/invitations/:id/accept
invitationsAPI.decline(id)                          // POST /users/me/invitations/:id/decline
```

---

## Business Rules
- BR-1: Only world owner sees the invite form and remove buttons.
- BR-2: Invite form disabled while request is in flight.
- BR-3: Remove triggers `window.confirm` before calling API.
- BR-4: Invitations badge hidden when count is 0.
- BR-5: Badge count refreshes on mount and after each accept/decline.

## Edge Cases
- EC-1: Invite 404 (user not found) → toast error.
- EC-2: Invite 409 (already co-author / pending) → toast warning.
- EC-3: No co-authors → empty state message.
- EC-4: No pending invitations → dropdown shows "No pending invitations".

## Out of Scope
- Email notifications.
- Real-time collaborator presence.
- Per-story co-author assignment.
