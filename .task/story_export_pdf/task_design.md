# DESIGN — Story Export PDF

---

## Changed Files

| File | Change | Spec Clause |
|------|--------|-------------|
| `frontend/src/App.jsx` | MODIFY — add `/stories/:storyId/print` route (outside MainLayout) | Behavior |
| `frontend/src/pages/StoryPrintPage.jsx` | NEW — loads story, renders clean print view, triggers window.print() | Behavior |
| `frontend/src/components/storyDetail/StoryDetailView.jsx` | MODIFY — add "Export PDF" button | Behavior |
| `frontend/src/index.css` | MODIFY — add `@media print` rules | BR-1 |

---

## Route placement

The print route must be **outside** `<MainLayout>` so the navbar is not rendered at all:
```jsx
// In App.jsx — outside the <Route element={<MainLayout />}> wrapper
<Route path="/stories/:storyId/print" element={<StoryPrintPage />} />
```

---

## `StoryPrintPage` design

```jsx
// On mount: fetch story, then window.print()
// Renders: <head><title>{story.title}</title>, clean prose layout
// Content rendering same as StoryDetailView (html/markdown/plain)
// No imports of Navbar, MainLayout, or any interactive UI
```

---

## Print CSS (`index.css` addition)

```css
@media print {
  /* Hide all navigation and interactive chrome */
  nav, .navbar, .btn, .modal, .toast, .dropdown { display: none !important; }
  /* Ensure full-width clean layout */
  body { background: white !important; color: black !important; }
  .prose { max-width: 100% !important; }
}
```

---

## "Export PDF" button placement

In `StoryDetailView`, alongside the existing Edit/Analyze buttons — opens in new tab:
```jsx
<a href={`/stories/${story.story_id}/print`} target="_blank" rel="noopener noreferrer"
   className="btn btn-outline btn-sm gap-1">
  <ArrowDownTrayIcon className="w-4 h-4" /> Export PDF
</a>
```
`ArrowDownTrayIcon` is already imported in `StoryDetailView`.
