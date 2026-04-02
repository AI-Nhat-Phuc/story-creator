# Flow Summary — Co-Author Permissions

> **Status**: APPROVED
> **Files**: frontend/src/services/api.js, WorldDetailContainer, WorldDetailView,
>            CollaboratorsPanel (new), Navbar, InvitationsDropdown (new)

---

## Planned Changes

**Will add/modify:**
- `api.js`: add `collaboratorsAPI` + `invitationsAPI` exports
- `WorldDetailContainer.jsx`: load collaborators on mount, `handleInvite`, `handleRemoveCollaborator`
- `WorldDetailView.jsx`: accept + pass collaborator props, render `<CollaboratorsPanel>`
- NEW `CollaboratorsPanel.jsx`: list + invite form
- `Navbar.jsx`: load invitations on mount, render `<InvitationsDropdown>`
- NEW `InvitationsDropdown.jsx`: bell icon + dropdown

**Will NOT change:**
- Backend routes (already complete)
- Any story/world logic unrelated to collaborators
