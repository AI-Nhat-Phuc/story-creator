# Task Spec — Novel Structure (SUB-4, Frontend)

> Backend fully implemented in `api/interfaces/routes/world_routes.py`.
> This task is **frontend only**.

---

## Route
`/worlds/:worldId/novel` — Novel Overview page (full-screen)

---

## Behavior

### Novel Overview page
- Loads novel metadata (title, description, chapters) via `GET /api/worlds/:worldId/novel`.
- Displays ordered chapter list: chapter number, story title, word count, last edited.
- Shows total novel word count (sum of all chapter word counts).
- World owner can edit the novel title and description inline.
- Owner and co-authors can drag-and-drop chapters to reorder; order persists immediately via `PATCH /api/worlds/:worldId/novel/chapters`.
- Each chapter row has an "Open in Editor" button → navigates to `/stories/:storyId/edit`.
- Empty state (no chapters assigned): CTA "No chapters yet — open a story to start writing".

### Assign chapter from WorldDetailPage
- "Novel" button in WorldDetailPage header → navigates to `/worlds/:worldId/novel`.

---

## API Contract (frontend additions)

```js
novelAPI.get(worldId)                   // GET  /worlds/:worldId/novel
novelAPI.update(worldId, { title, description })  // PUT  /worlds/:worldId/novel
novelAPI.reorderChapters(worldId, order)  // PATCH /worlds/:worldId/novel/chapters { order: [storyId, ...] }
```

---

## Component Tree

```
NovelPage
└── NovelContainer               ← state, load, reorder, edit
    └── NovelView                ← pure layout
        ├── NovelHeader          ← title (inline edit), description, total word count
        └── ChapterList          ← draggable chapter rows
            └── ChapterRow ×N   ← chapter number, title, word count, last edited, "Edit" btn
```

---

## Business Rules
- BR-1: Only owner can edit novel title/description.
- BR-2: Only owner or co-author can reorder chapters.
- BR-3: Word count per chapter derived client-side: strip HTML tags, split on whitespace.
- BR-4: Reorder fires immediately on drop (no "Save order" button).
- BR-5: Dragging disabled for non-owners/non-co-authors (rows are static).

## Edge Cases
- EC-1: No chapters → empty state with CTA.
- EC-2: Story content is null/empty → 0 words shown.
- EC-3: Reorder API error → toast + revert to previous order.
- EC-4: Novel has no title set → falls back to world name.

## Out of Scope
- Multiple novels per world.
- Export as single document.
- Assigning/unassigning chapter numbers from the novel page (done via story editor).
