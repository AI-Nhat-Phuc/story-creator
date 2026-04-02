# DESIGN — Novel Structure (Frontend)

---

## Changed Files

| File | Change | Spec Clause |
|------|--------|-------------|
| `frontend/src/services/api.js` | MODIFY — add novelAPI | API Contract |
| `frontend/src/App.jsx` | MODIFY — add `/worlds/:worldId/novel` route | Route |
| `frontend/src/components/worldDetail/WorldDetailView.jsx` | MODIFY — add "Novel" button in header | Assign chapter from WorldDetailPage |
| `frontend/src/pages/NovelPage.jsx` | NEW | Component Tree |
| `frontend/src/containers/NovelContainer.jsx` | NEW | Component Tree |
| `frontend/src/components/novel/NovelView.jsx` | NEW | Component Tree |
| `frontend/src/components/novel/NovelHeader.jsx` | NEW | Component Tree |
| `frontend/src/components/novel/ChapterList.jsx` | NEW — HTML5 drag-and-drop | Component Tree |

---

## `api.js` additions

```js
export const novelAPI = {
  get:             (worldId)        => api.get(`/worlds/${worldId}/novel`),
  update:          (worldId, data)  => api.put(`/worlds/${worldId}/novel`, data),
  reorderChapters: (worldId, order) => api.patch(`/worlds/${worldId}/novel/chapters`, { order }),
}
```

---

## `NovelContainer` state

```js
{
  novel: null,     // { title, description, chapters: [], total_word_count }
  isLoading: true,
  editingMeta: false,       // inline title/description edit
  metaForm: { title: '', description: '' },
  savingMeta: false,
}
// chapters order managed as local state for optimistic drag-and-drop
const [chapters, setChapters] = useState([])
```

---

## `ChapterList` — HTML5 drag-and-drop design

```jsx
// Each row: draggable={isOwner}
// onDragStart: store dragged index in ref
// onDragOver(e): e.preventDefault() to allow drop
// onDrop(targetIndex): reorder chapters array, call onReorder(newOrder)
```

No external library — uses native `draggable`, `onDragStart`, `onDragOver`, `onDrop`.

---

## `NovelHeader` props

```jsx
{
  title: string,
  description: string,
  totalWordCount: number,
  canEdit: boolean,
  editing: boolean,
  metaForm: { title, description },
  saving: boolean,
  onEdit: () => void,
  onCancel: () => void,
  onSave: () => void,
  onFormChange: (field, value) => void,
}
```

---

## Word count helper

```js
function countWords(html) {
  if (!html) return 0
  const text = html.replace(/<[^>]+>/g, ' ').trim()
  return text ? text.split(/\s+/).filter(Boolean).length : 0
}
```

Total word count = sum of `countWords(chapter.content)` for all chapters.
Computed in `NovelContainer` via `useMemo`.

---

## `WorldDetailView` addition

Add a "Novel" button/link in the world header section (visible to all authenticated users):
```jsx
<Link to={`/worlds/${world.world_id}/novel`} className="btn btn-outline btn-sm gap-1">
  <BookOpenIcon className="w-4 h-4" /> Novel
</Link>
```
