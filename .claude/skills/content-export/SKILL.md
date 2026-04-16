---
name: content-export
description: Use this skill when editing story preview truncation, the "See more" flow, story print/PDF export, story reader page, or novel content pagination. Covers how story content is rendered across formats (html/markdown/plain). Triggers when editing frontend/src/pages/StoryDetailPage.jsx, StoryReaderPage.jsx, StoryPrintPage.jsx, NovelPage.jsx (reader pagination), frontend/index.css (@media print rules), and api/interfaces/routes/world_routes.py (/novel/content endpoint).
---

# content-export — Preview, Reader, Print, Pagination

How story content flows from the DB to various surfaces — detail preview, full reader, printable PDF, infinite-scroll novel.

## Content format rendering (applies to all surfaces)

Every surface that renders `story.content` must branch on `story.format`:

- `html`  → `<div dangerouslySetInnerHTML={{ __html: content }} />` (content is our own sanitized HTML)
- `markdown` → `<ReactMarkdown>{content}</ReactMarkdown>`
- `plain` / unknown → `<pre style={{whiteSpace: 'pre-wrap'}}>{content}</pre>`

Extract this into a shared `<StoryContent />` component if touching multiple surfaces.

## Story detail preview (truncation)

- `StoryDetailPage` shows at most **10 lines** by default
- Lines beyond the cap render with a gradient fade + "See more" button
- Button navigates to `/stories/:id/read`
- **Skip truncation** when URL has `?highlightPosition=N` — user arrived from a cross-reference and needs the exact line visible
- Line counting is visual (DOM-based, `ResizeObserver`), not a substring count

## Full reader (`/stories/:id/read`)

- Full content in the chosen format renderer
- Prev/Next buttons use `GET /api/stories/:id/neighbors` — stay within the same world, sorted by `order`
- Top bar: story title + chapter_number (if any), back-to-world link
- Reading progress persisted to localStorage by story_id (scroll position percentage)

## Print-to-PDF (`/stories/:id/print`)

- Dedicated page; no app chrome (navbar/toasts/buttons hidden via `@media print` in `frontend/index.css`)
- On mount, call `window.print()` exactly once (guard with a ref)
- Renders: story title, author display name, world name, chapter number, then content
- No server-side PDF generation — rely on browser print dialog
- User saves as PDF through their browser (Chrome/Safari native "Save as PDF")

## Novel reader pagination (`/worlds/:id/novel`)

- Endpoint: `GET /api/worlds/:id/novel/content?cursor=<opaque>&line_budget=100`
- Response: `{chapters: [{story_id, chapter_number, title, content, format}], next_cursor: str | null, exhausted: bool}`
- Initial page returns **2 chapters** regardless of line count (so the reader has something substantial to scroll)
- Subsequent pages respect `line_budget` (~100 lines), may cut a chapter mid-text — include `content_partial: true` and `continuation_marker` in that case
- Frontend uses `IntersectionObserver` at the bottom sentinel to trigger next fetch
- Show a lightweight "Loading more…" indicator (i18n key)

## @media print rules (in frontend/index.css)

```css
@media print {
  .no-print, nav, .toast, .btn, .drawer, .navbar { display: none !important; }
  body { background: white; color: black; }
  .print-page { padding: 2cm; font-size: 12pt; line-height: 1.6; }
  a { color: inherit; text-decoration: none; }
}
```

## Gotchas

- **Don't** sanitize HTML content client-side on output — it was sanitized on save (if ever needed). Double-escaping breaks rich formatting
- **`highlightPosition` param** from cross-reference flows must bypass the 10-line cap or the highlight target will be hidden behind the fade
- Browser print dialog cannot be customized — don't try to inject headers/footers via JS, use `@page` CSS if truly needed
- Novel pagination cursor is opaque — don't parse it client-side; just echo it back
