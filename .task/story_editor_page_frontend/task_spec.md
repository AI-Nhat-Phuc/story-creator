# Task Spec — Story Editor Page Frontend (v2 — Notion-style editor)

> Backend (model, schemas, routes) already implemented.
> Editor uses `novel` (TipTap-based Notion-like editor). Content stored as HTML.

---

## Routes
- `/stories/new?worldId=<id>` — create mode: blank editor, story not persisted yet
- `/stories/:storyId/edit` — edit mode: loads existing story

---

## Layout

```
┌────────────────────────────────────────────────────────────────┐
│  HEADER                                                        │
│  [←] [Story Title ____________]  — Draft    [1,234w ~6m] [Pub]│
├───────────────────┬────────────────────────────────────────────┤
│  LEFT PANEL       │  EDITOR (novel)                            │
│  ─ GPT Tools ─    │                                            │
│  [Paraphrase]     │  Xưởng viết truyện          ← H1 rendered │
│  [Expand]         │                                            │
│  [suggestions…]   │  Mục tiêu                   ← H2 rendered │
│  ─ Outline ─      │  Dùng canvas này để phát    ← paragraph   │
│  # Heading 1      │  triển truyện…                             │
│    ## Heading 2   │                                            │
│                   │  ───────────────────         ← HR          │
└───────────────────┴────────────────────────────────────────────┘
```

The right panel IS the editor. Formatting is rendered inline while typing (Notion-style):
- Typing `# ` auto-renders as H1 heading (via slash menu or keyboard)
- **Bold**, *italic*, ~~strikethrough~~ rendered in-place
- Bubble toolbar appears on text selection: Bold, Italic, Underline, Strike, Link, H1, H2, H3
- `/` triggers slash command menu: Heading, Bullet list, Numbered list, Quote, Code, Divider, Image

No separate Edit/Split/Preview toggle — one unified editing surface.

---

## Content format change

| Field | Old | New |
|-------|-----|-----|
| `story.format` | `'plain'` \| `'markdown'` | `'plain'` \| `'markdown'` \| `'html'` |
| `story.content` (for new stories) | raw markdown | HTML string from `editor.getHTML()` |

- New stories created from the editor: `format='html'`
- Old stories (`format='plain'` or `format='markdown'`): loaded as plain text into novel, re-saved as `format='html'` on first save
- Backend `CreateStorySchema` and `UpdateStorySchema`: add `'html'` to `format` OneOf validator

---

## API Contract (frontend side)

### New wrappers to add to `api.js`
```js
storiesAPI.patch(id, data)     // PATCH /stories/:id  (auto-save)
storiesAPI.getMyDraft()        // GET   /stories/my-draft
gptAPI.paraphrase(text, mode)  // POST  /gpt/paraphrase
authAPI.updateProfile(data)    // PUT   /auth/profile
```

### Endpoints used
```
POST /api/stories          { world_id, title, content, visibility:'draft', format:'html' }
PATCH /api/stories/:id     { title?, content? }
PUT  /api/stories/:id      { visibility }   ← Publish
GET  /api/stories/my-draft
GET  /api/stories/:id      ← load in edit mode
GET  /api/auth/me          ← get user signature
PUT  /api/auth/profile     { signature }
POST /api/gpt/paraphrase   { text, mode }
```

---

## Component Tree

```
StoryEditorPage
└── StoryEditorContainer          ← state, auto-save, GPT, load/create
    └── StoryEditorView           ← pure layout shell
        ├── EditorHeader          ← title input, status badge, word count, Publish
        ├── LeftPanel             ← GPT tools + outline only (no toolbar)
        │   ├── GptToolsPanel     ← Paraphrase/Expand + suggestions
        │   └── DocumentOutline   ← heading list extracted from editor JSON
        └── NovelEditor           ← wrapper around <Editor> from 'novel'
```

**Removed vs original design:**
- ~~`useMarkdownEditor` hook~~ — novel handles all formatting via bubble menu + slash commands
- ~~`MarkdownToolbar` component~~ — replaced by novel's built-in bubble menu
- ~~`RightPanel` component~~ — replaced by `NovelEditor`
- ~~View mode toggle (Edit/Split/Preview)~~ — no longer needed

---

## `novel` editor integration

```jsx
import { Editor } from 'novel'

// NovelEditor wraps <Editor> and bridges to container state
function NovelEditor({ initialContent, format, onUpdate, editorRef }) {
  return (
    <Editor
      defaultValue={initialContent}   // HTML string or plain text
      onUpdate={({ editor }) => {
        onUpdate(editor.getHTML(), editor)
        editorRef.current = editor
      }}
      className="min-h-full px-8 py-6 prose prose-sm max-w-none ..."
      disableLocalStorage={true}      // we handle persistence ourselves
    />
  )
}
```

`editorRef.current` gives access to the TipTap editor instance for:
- Getting selected text: `editor.state.doc.textBetween(from, to, ' ')`
- Applying GPT suggestion: `editor.chain().focus().deleteSelection().insertContent(suggestion).run()`
- Extracting headings for outline: `editor.getJSON().content.filter(n => n.type === 'heading')`
- Getting word count: `editor.getText().trim().split(/\s+/).filter(Boolean).length`

---

## `StoryEditorContainer` state

```js
const [editor, setEditor] = useState({
  title: '',
  content: '',           // HTML string
  saveStatus: 'idle',    // 'idle' | 'saving' | 'saved' | 'error'
  isPublished: false,
  isLoading: true,
})
```

Refs:
- `storyIdRef` — persisted story ID (null until first save)
- `lastSavedRef` — `{ title, content }` snapshot for change detection
- `saveTimerRef` — 30s debounce timer
- `editorRef` — TipTap editor instance (set by NovelEditor via `onUpdate`)

Derived (useMemo):
- `wordCount` — from `editorRef.current?.getText()` or content text
- `readTime` — `Math.ceil(wordCount / 200)`
- `headings` — from `editorRef.current?.getJSON()`

---

## Auto-save logic

Same as before, content is now HTML string:
```
On title or content change:
  clearTimeout(saveTimerRef.current)
  saveTimerRef.current = setTimeout(doSave, 30_000)

doSave():
  if unchanged → skip (BR-1)
  if empty title in create mode → skip (EC-4)
  POST /api/stories { ..., format: 'html' }  ← first save
  or PATCH /api/stories/:id                   ← subsequent saves
  lastSavedRef.current = { title, content }
```

---

## GPT Tools integration with TipTap

```js
// In StoryEditorContainer
function handleParaphrase() {
  const editor = editorRef.current
  if (!editor) return
  const { from, to } = editor.state.selection
  const selected = editor.state.doc.textBetween(from, to, ' ')
  if (selected.length < 10) return
  // store selection range for Apply
  gptSelectionRef.current = { from, to }
  callGptParaphrase(selected, 'paraphrase')
}

function handleApply(suggestion) {
  const editor = editorRef.current
  const { from, to } = gptSelectionRef.current
  editor.chain().focus().deleteRange({ from, to }).insertContent(suggestion).run()
  clearSuggestions()
}
```

GPT state (separate useState since it's independent of editor state):
```js
const [gpt, setGpt] = useState({
  isLoading: false,
  suggestions: [],
})
const gptSelectionRef = useRef(null)  // { from, to } TipTap positions
```

Selection length for enabling GPT buttons:
- Listen to `editor.on('selectionUpdate', ...)` inside `NovelEditor.onUpdate`
- Pass `selectionLength` up via `onUpdate` callback

---

## Signature insertion

```js
function handleSignature(sig) {
  editorRef.current
    .chain()
    .focus()
    .insertContent(`<p>— ${sig}</p>`)
    .run()
}
```

Button in `GptToolsPanel` (or standalone button above outline):
- Fetches sig from `GET /api/auth/me`
- Disabled if `— {sig}` already in `editor.getText()`

---

## Resume draft flow

On mount (create mode):
```
GET /api/stories/my-draft
  found → navigate /stories/:id/edit + toast "Resuming your draft"
  not found → blank editor
```

---

## Backend change (schema only)

`api/schemas/story_schemas.py` — add `'html'` to format validator in both schemas:
```python
format = fields.Str(validate=validate.OneOf(['plain', 'markdown', 'html']))
```

`StoryDetailPage` / anywhere content is displayed:
- `format='html'` → `<div dangerouslySetInnerHTML={{ __html: content }} className="prose ..." />`
- `format='markdown'` → `<ReactMarkdown>` (existing behavior)
- `format='plain'` → `<pre>` (existing behavior)

---

## Business Rules
- BR-1: Auto-save skipped when title + content unchanged
- BR-2: GPT buttons active only when TipTap selection ≥ 10 chars
- BR-3: No auth token → redirect to `/login`
- BR-4: 403 from backend → toast + editor read-only
- BR-5: `wordCount`, `readTime`, `headings` via `useMemo` — not state
- BR-6: One draft enforced by backend (409 → toast)
- BR-7: Missing `worldId` in create mode → redirect + toast
- BR-8: New stories always `format='html'`
- BR-9: Old `plain`/`markdown` stories loaded as plain text, re-saved as `html` on first edit
- BR-10: Signature button disabled if sig already in `editor.getText()`
- BR-11: ~~Toolbar~~ — novel bubble menu is always available (no disable needed)

## Edge Cases
- EC-1: Story 404 in edit mode → redirect `/stories` + toast
- EC-2: Unmount → flush pending save
- EC-3: GPT error → toast, panel clears, selection preserved
- EC-4: Empty title in create mode → skip auto-save
- EC-6: POST succeeds → storyIdRef holds ID, retry uses PATCH
- EC-7: Draft exists on "New Story" → resume flow
- EC-10: No signature set → prompt modal → `PUT /api/auth/profile`

## Out of Scope
- File upload for images (URL input only via slash command)
- Real-time collaborative editing
- Chapter nav
- Syntax highlighting
- Export PDF/HTML
- Story metadata editing (genre, time index)
