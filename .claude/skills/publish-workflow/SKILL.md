---
name: publish-workflow
description: Use this skill when editing visibility / publishing logic for worlds and stories — default visibility, publish buttons, draft lifecycle, discovery surfaces. Triggers when editing api/schemas/world_schemas.py (visibility default), api/schemas/story_schemas.py, api/services/world_service.py, api/services/story_service.py, frontend/src/pages/WorldsPage.jsx, WorldDetailView.jsx, NewStoryPage.jsx, StoryEditorPage.jsx (publish button).
---

# publish-workflow — Visibility States & Publish Flow

Worlds and stories share a three-state visibility model, but the lifecycles differ slightly.

## States

| Visibility  | World                                           | Story                                     |
|-------------|-------------------------------------------------|-------------------------------------------|
| `draft`     | **Default on create**. Private to owner only    | **Default on create**. One per user       |
| `private`   | Shared with co-authors; not discoverable        | Published but not publicly listed         |
| `public`    | Discoverable in the public worlds list          | Discoverable; readable by anyone          |

## Defaults (breaking change from earlier `private` default)

- New world: `visibility = 'draft'` (see `api/schemas/world_schemas.py`)
- New story: `visibility = 'draft'`
- Frontend create forms DO NOT show a visibility dropdown — always draft on create

## Publish button (world)

- Rendered in `WorldDetailView` **only when** current user is the owner AND `visibility !== 'public'`
- Click → confirmation modal → `PUT /api/worlds/:id` with `{visibility: 'public'}`
- Confirmation copy: warns that the world becomes publicly discoverable (use i18n keys)

## Publish button (story editor)

- Rendered in `StoryEditorPage` top bar when story is in `draft` state
- Click → `PUT /api/stories/:id` with `{visibility: 'private'}` (NOT `public` — one-click publish does not make the story publicly discoverable, user changes it explicitly later)
- After publish, status badge switches from "Draft" to "Published ✓"

## Draft lifecycle (story)

- **Only one active draft per user** — enforced at create time (409 Conflict if another draft exists)
- `GET /api/stories/my-draft` → returns `{story: {...}}` or `{story: null}`
- "New story" button behavior:
  - If a draft exists → navigate straight to editor with that draft
  - Else → create a new draft and open editor
- The nested `{story: ...}` shape is a common source of bugs — always read `res.data.story`, not `res.data`

## Discovery surfaces

- `GET /api/worlds?visibility=public` — public worlds list (pagination, anonymous access allowed)
- `GET /api/stories?visibility=public` — public stories
- Viewers (non-owner, non-co-author) cannot see `draft` or `private` items
- Internal admin routes may expose everything — gate with `@admin_required`

## When adding a new visibility transition

1. Decide target state (draft → private, private → public, public → private, etc.)
2. Implement on the single `PUT /api/{resource}/:id` — don't invent a new endpoint
3. Enforce permission: only owner transitions visibility (see `permissions-collaboration` skill)
4. Update UI to hide the trigger when the transition wouldn't be valid (already at that state, wrong role)
5. Add confirmation modal when the transition increases exposure (private → public)
