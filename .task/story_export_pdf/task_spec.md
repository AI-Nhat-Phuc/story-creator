# Task Spec — Story Export PDF

> No backend changes. Frontend-only: browser print-to-PDF via `window.print()`.

---

## Behavior

- A "Export PDF" button appears on the StoryDetailPage (visible to all users who can view the story).
- Clicking opens `/stories/:storyId/print` in a new browser tab.
- The print page renders the story (title, author, world name, content) with clean typography and no navigation chrome.
- On mount, `window.print()` is triggered automatically — the browser opens its print dialog where the user can "Save as PDF".
- Content formats handled: `html` (rendered prose), `markdown` (rendered via react-markdown), `plain` (pre-formatted text).
- A `@media print` block in `index.css` hides the navbar, toasts, buttons, and any other UI chrome globally.

---

## API Contract

No new endpoints. Uses existing `GET /api/stories/:id`.

---

## Business Rules
- BR-1: Print page has no navigation, no buttons visible in print output.
- BR-2: Story title is the `<title>` of the print page (appears in PDF filename).
- BR-3: Author's username and world name shown as subtitle.
- BR-4: All three content formats rendered correctly.

## Edge Cases
- EC-1: Story not found → show "Story not found" and no print dialog.
- EC-2: Content is empty → print page shows title/metadata only.

## Out of Scope
- Server-side PDF generation (WeasyPrint, Puppeteer).
- Custom fonts / cover page.
- Batch export of multiple stories.
