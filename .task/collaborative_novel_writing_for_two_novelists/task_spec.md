# Task Spec — Collaborative Novel Writing for Two Novelists

**Feature slug:** `collaborative_novel_writing_for_two_novelists`
**Complexity:** 9/10
**Phase:** SPEC

---

## Overview

Two novelists want to co-write a fiction novel from anywhere, at any time. This feature set turns the platform into a proper collaborative writing environment. It consists of four ordered sub-tasks, each independently deliverable.

**Delivery order:**
```
SUB-1 (Auto-save)  →  SUB-3 (Story Editor)  →  SUB-2 (Co-author)  →  SUB-4 (Novel Structure)
```

---

## SUB-1 — Auto-save Writing Process

### Behavior
- Every change to a story's text content triggers a debounced save (500ms after the user stops typing).
- A status indicator is always visible in the editor: `Saved`, `Saving…`, or `Unsaved changes`.
- On page load, the latest saved version is loaded automatically.
- If a save fails, the indicator shows `Save failed — retrying` and retries up to 3 times with exponential backoff.
- No explicit "Save" button is required (can remain as an optional shortcut Ctrl+S).

### API Contract
```text
PATCH /api/stories/{story_id}
Body: { "content": "..." }
200:  { status: "success", data: { story_id, updated_at } }
403:  { error: "permission_denied" }
404:  { error: "resource_not_found" }
```

### Business Rules
- BR-1.1: Only the story owner or a world `co_author` may trigger auto-save.
- BR-1.2: Auto-save overwrites the current draft — it does not create a new revision.
- BR-1.3: Debounce interval is 500ms. If the user navigates away mid-debounce, a synchronous save fires on the `beforeunload` event.

### Edge Cases
- EC-1.1: Network offline — queue the save locally and fire when connection is restored.
- EC-1.2: Concurrent save from co-author — last-write-wins (no merge).
- EC-1.3: Story deleted by owner while co-author is editing — save returns 404; show "This story was deleted" banner.

### Out of Scope
- Conflict resolution / diff merging between simultaneous edits.
- Revision history (future feature).

---

## SUB-2 — Co-Author Permissions

### Behavior
- A world owner can invite another registered user as a `co_author` of that world by username or email.
- The invitee receives an in-app invitation they can accept or decline.
- A `co_author` can: read, create, and edit stories and entities within that world.
- A `co_author` cannot: delete the world, change world visibility, or invite other co-authors.
- The owner can revoke co-authorship at any time; access is removed immediately.
- The world detail page shows a "Collaborators" section listing all co-authors.

### API Contract
```text
POST   /api/worlds/{world_id}/collaborators
Body:  { "username_or_email": "...", "role": "co_author" }
201:   { status: "success", data: { invitation_id, invitee, world_id } }
404:   { error: "resource_not_found" }     — user not found
409:   { error: "conflict" }               — already a co-author

GET    /api/worlds/{world_id}/collaborators
200:   { status: "success", data: [ { user_id, username, role, joined_at } ] }

DELETE /api/worlds/{world_id}/collaborators/{user_id}
200:   { status: "success", message: "Co-author removed" }

GET    /api/users/me/invitations
200:   { status: "success", data: [ { invitation_id, world_id, world_title, invited_by, created_at } ] }

POST   /api/users/me/invitations/{invitation_id}/accept
200:   { status: "success" }

POST   /api/users/me/invitations/{invitation_id}/decline
200:   { status: "success" }
```

### Business Rules
- BR-2.1: Only the world owner may invite or revoke co-authors.
- BR-2.2: A world may have at most 10 co-authors.
- BR-2.3: A user may be co-author of unlimited worlds.
- BR-2.4: Owner cannot invite themselves — return `400 Bad Request`.
- BR-2.5: `co_author` role inherits all `editor` permissions on stories and entities within that world only.

### Edge Cases
- EC-2.1: Invited user does not exist → `404`.
- EC-2.2: Owner invites themselves → `400`.
- EC-2.3: World deleted while invitation is pending → invitation is silently invalidated.

### Out of Scope
- Email notifications for invitations.
- Per-story co-author assignment (co-authorship is world-level only).

---

## SUB-3 — Dedicated Story Editor Page

### Behavior
- A new full-screen route `/worlds/{world_id}/stories/{story_id}/edit` replaces the current inline textarea.
- **Rich text editor** (Tiptap): bold, italic, underline, headings H1–H3, bullet list, numbered list, blockquote, horizontal rule.
- **Left sidebar — Chapter Navigator**: all stories in the world listed as chapters in order. Clicking navigates to that story without leaving the editor.
- **Right panel — Writing Tools** (collapsible):
  - **Word & character count** with estimated reading time (live).
  - **Character reference**: searchable list of world entities; click to expand name + description inline.
  - **Location reference**: same pattern for world locations.
  - **GPT Paraphrase**: select text → toolbar button "Paraphrase" → 3 alternatives shown inline; pick one or dismiss.
  - **GPT Expand**: select a short phrase → "Expand" → GPT writes a longer version.
- **Distraction-free mode**: hides both sidebars, shows only editor + save indicator.
- Auto-save indicator (SUB-1) lives in the top bar at all times.

### API Contract
```text
GET  /api/worlds/{world_id}/stories/{story_id}
200: { status: "success", data: { story_id, title, content, chapter_number, updated_at } }

PATCH /api/stories/{story_id}
Body: { "content": "..." }           — used by auto-save (see SUB-1)

POST /api/gpt/paraphrase             — NEW endpoint
Body: { "text": "...", "mode": "paraphrase" | "expand" }
200:  { status: "success", data: { suggestions: ["...", "...", "..."] } }
429:  { error: "quota_exceeded" }
```

### Business Rules
- BR-3.1: Editor route is only accessible to the story owner or a world `co_author`.
- BR-3.2: Viewers (non-co-authors) are redirected to a read-only rendered view.
- BR-3.3: GPT paraphrase/expand consumes the user's existing GPT quota.
- BR-3.4: Paraphrase suggestions are not saved until the user explicitly selects one.

### Edge Cases
- EC-3.1: Story has no content → editor opens with empty state and placeholder text.
- EC-3.2: GPT quota exhausted → paraphrase panel shows "Quota reached" with upgrade message.
- EC-3.3: World has no entities/locations → reference panels show empty state message.
- EC-3.4: User navigates away mid-debounce → `beforeunload` fires sync save.

### Out of Scope
- Real-time collaborative cursors (Google Docs style).
- Inline comment threads.
- Export to PDF/DOCX.
- Spell-check beyond browser native.

---

## SUB-4 — Novel Structure

### Behavior
- Each world can have one **Novel** container grouping its stories as ordered chapters.
- The novel has a title (defaults to world name) and a cover description.
- Stories are assigned a `chapter_number` (1-based integer). Unassigned stories appear in an "Ungrouped" section.
- **Novel Overview page** (`/worlds/{world_id}/novel`) shows:
  - Novel title and cover description.
  - Ordered chapter list with: chapter number, story title, word count, last edited timestamp.
  - Drag-and-drop reordering (persisted immediately).
  - Total novel word count.
  - "Open in Editor" button per chapter → opens SUB-3 editor.

### API Contract
```text
GET  /api/worlds/{world_id}/novel
200: { status: "success", data: { title, description, chapters: [ { story_id, chapter_number, title, word_count, updated_at } ], total_word_count } }

PUT  /api/worlds/{world_id}/novel
Body: { "title": "...", "description": "..." }
200:  { status: "success", data: { title, description } }

PATCH /api/worlds/{world_id}/novel/chapters
Body: { "order": [ story_id, story_id, ... ] }
200:  { status: "success", data: { chapters: [ { story_id, chapter_number } ] } }

PATCH /api/stories/{story_id}
Body: { "chapter_number": 3 }        — extend existing endpoint
```

### Business Rules
- BR-4.1: Only the world owner or a `co_author` may reorder chapters.
- BR-4.2: `chapter_number` values are contiguous integers starting at 1, recomputed server-side after every reorder.
- BR-4.3: Deleting a story removes it from the chapter order; remaining chapters renumber automatically.
- BR-4.4: A story belongs to at most one chapter slot per novel.

### Edge Cases
- EC-4.1: World has no stories → Novel Overview shows empty state with "Create first chapter" CTA.
- EC-4.2: Two users reorder simultaneously → last-write-wins on the full order array.
- EC-4.3: Story has no content → word count shown as "0 words" with a visual cue.

### Out of Scope
- Multiple novels per world.
- Part / Act grouping above chapter level.
- Full novel export as single document.
