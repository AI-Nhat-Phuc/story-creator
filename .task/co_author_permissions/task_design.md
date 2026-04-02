# DESIGN — Co-Author Permissions (Frontend)

---

## Changed Files

| File | Change | Spec Clause |
|------|--------|-------------|
| `frontend/src/services/api.js` | MODIFY — add collaboratorsAPI + invitationsAPI | API Contract |
| `frontend/src/containers/WorldDetailContainer.jsx` | MODIFY — load collaborators, invite/remove handlers | Behavior → World Detail |
| `frontend/src/components/worldDetail/WorldDetailView.jsx` | MODIFY — add CollaboratorsPanel, pass props | Component Tree |
| `frontend/src/components/worldDetail/CollaboratorsPanel.jsx` | NEW | Component Tree |
| `frontend/src/components/Navbar.jsx` | MODIFY — add bell icon + InvitationsDropdown | Behavior → Navbar |
| `frontend/src/components/InvitationsDropdown.jsx` | NEW | Component Tree |

---

## `api.js` additions

```js
export const collaboratorsAPI = {
  list:   (worldId)              => api.get(`/worlds/${worldId}/collaborators`),
  invite: (worldId, usernameOrEmail) => api.post(`/worlds/${worldId}/collaborators`, { username_or_email: usernameOrEmail, role: 'co_author' }),
  remove: (worldId, userId)      => api.delete(`/worlds/${worldId}/collaborators/${userId}`),
}

export const invitationsAPI = {
  list:    ()             => api.get('/users/me/invitations'),
  accept:  (id)           => api.post(`/users/me/invitations/${id}/accept`),
  decline: (id)           => api.post(`/users/me/invitations/${id}/decline`),
}
```

---

## `CollaboratorsPanel` props

```jsx
{
  collaborators: [{ user_id, username, role }],
  canEdit: boolean,          // world owner only
  inviteLoading: boolean,
  onInvite: (usernameOrEmail) => void,
  onRemove: (userId) => void,
}
```

Render:
- Section header "Collaborators"
- List of co-authors: username + "Remove" button (owner only, behind window.confirm)
- Empty state if no co-authors
- Inline invite form (owner only): text input + "Invite" button

---

## `InvitationsDropdown` props

```jsx
{
  invitations: [{ invitation_id, world_title, invited_by, created_at }],
  onAccept: (id) => void,
  onDecline: (id) => void,
}
```

Renders as DaisyUI `dropdown dropdown-end` anchored to a bell icon in the Navbar.
Badge count shown when `invitations.length > 0`.

---

## `WorldDetailContainer` additions

New state:
```js
const [collaborators, setCollaborators] = useState([])
const [inviteLoading, setInviteLoading] = useState(false)
```

Load in `loadWorldDetails()`:
```js
const collabRes = await collaboratorsAPI.list(worldId)
setCollaborators(collabRes.data || [])
```

Handlers: `handleInvite(usernameOrEmail)`, `handleRemoveCollaborator(userId)`

---

## `Navbar` additions

New state:
```js
const [invitations, setInvitations] = useState([])
```

`useEffect` on mount (only when `isAuthenticated`) → `invitationsAPI.list()` → sets state.
Renders `<InvitationsDropdown>` between theme selector and user avatar (desktop) and in mobile dropdown.
