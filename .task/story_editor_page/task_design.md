# Task Design — Story Editor Page (v2)

## Changed Files

| File | Change Type | Maps to Spec Clause |
|------|-------------|---------------------|
| `api/core/models/story.py` | MODIFY — add `format` field | SUB-4-A |
| `api/schemas/story_schemas.py` | MODIFY — add `format` to Create + Update schemas | SUB-4-A |
| `api/schemas/auth_schemas.py` | MODIFY — add `signature` to `UpdateProfileSchema` | SUB-4-D |
| `api/interfaces/routes/story_routes.py` | MODIFY — add draft enforcement + `GET /my-draft` | SUB-4-B, SUB-4-C |
| `api/interfaces/routes/auth_routes.py` | MODIFY — add `PUT /api/auth/profile` | SUB-4-E |
| `frontend/src/services/api.js` | MODIFY — add 4 methods | API Contract |
| `frontend/src/App.jsx` | MODIFY — add 2 routes + lazy import | Spec Routes |
| `frontend/src/pages/StoryEditorPage.jsx` | NEW | SUB-1 |
| `frontend/src/containers/StoryEditorContainer.jsx` | NEW | SUB-1, SUB-2, SUB-3, SUB-5 |
| `frontend/src/hooks/useMarkdownEditor.js` | NEW | SUB-2 |
| `frontend/src/components/editor/StoryEditorView.jsx` | NEW | SUB-1, SUB-2, SUB-6 |
| `frontend/src/components/editor/EditorHeader.jsx` | NEW | SUB-1, SUB-3 |
| `frontend/src/components/editor/LeftPanel.jsx` | NEW | SUB-1, SUB-2, SUB-5 |
| `frontend/src/components/editor/RightPanel.jsx` | NEW | SUB-1, SUB-2 |
| `frontend/src/components/editor/MarkdownToolbar.jsx` | NEW | SUB-2 |
| `frontend/src/components/editor/DocumentOutline.jsx` | NEW | SUB-2 |
| `frontend/src/components/editor/GptToolsPanel.jsx` | NEW | SUB-5 |

---

## Backend Schema / Model Changes

### `api/core/models/story.py` — add `format` field

```python
# __init__ signature: add format param after chapter_number
format: str = 'plain'   # 'plain' | 'markdown'

# __init__ body:
self.format = format

# to_dict(): add
"format": self.format,

# from_dict(): add
format=data.get("format", "plain"),
```

Ref: spec SUB-4-A, BR-8, BR-9

---

### `api/schemas/story_schemas.py` — add `format` field

**CreateStorySchema** — add:
```python
format = fields.Str(
    validate=validate.OneOf(['plain', 'markdown']),
    load_default='plain'
)
```

**UpdateStorySchema** — add:
```python
format = fields.Str(
    validate=validate.OneOf(['plain', 'markdown'])
)
```

Ref: spec SUB-4-A, API Contract

---

### `api/schemas/auth_schemas.py` — add `signature` to `UpdateProfileSchema`

```python
# Add to UpdateProfileSchema:
signature = fields.Str(
    validate=validate.Length(max=200),
    load_default=None,
    allow_none=True
)
```

The existing `validate_not_empty` cross-validator already covers this (at least one field required).

Ref: spec SUB-4-D, BR-10

---

## New Backend Endpoints (implemented in IMPLEMENT phase)

These are listed here to complete the interface contract:

### `GET /api/stories/my-draft` (story_routes.py)
```
Auth: @token_required
Logic: storage.list_stories(owner_id=user_id, visibility='draft') → first result or None
200: success_response({ 'story': story_dict | None })
```
**Must be registered BEFORE `GET /api/stories/<story_id>`** to avoid Flask routing conflict with the literal `my-draft`.

### Draft enforcement in `POST /api/stories` (story_routes.py)
```
When visibility == 'draft':
  existing = storage.list_stories(owner_id=user_id, visibility='draft')
  if existing:
      raise ConflictError("You already have a draft story. Finish or publish it first.")
```

### Draft enforcement in `PUT /api/stories/:id` (story_routes.py)
```
When new visibility == 'draft' and old visibility != 'draft':
  existing = [s for s in storage.list_stories(owner_id=user_id, visibility='draft')
              if s['story_id'] != story_id]
  if existing:
      raise ConflictError("You already have a draft story.")
```

### `PUT /api/auth/profile` (auth_routes.py)
```
Auth: @token_required
Validation: @validate_request(UpdateProfileSchema)
Logic:
  data = request.validated_data
  user_data = storage.load_user(g.current_user.user_id)
  if 'username' in data: user_data['username'] = data['username']
  if 'email' in data:    user_data['email'] = data['email']
  if data.get('signature') is not None:
      user_data.setdefault('metadata', {})['signature'] = data['signature']
  storage.save_user(user_data)
200: success_response({ 'user': user_data })
```

---

## Frontend Interface Changes

### `frontend/src/services/api.js`

```js
// storiesAPI — add:
patch:      (id, data) => api.patch(`/stories/${id}`, data),
getMyDraft: ()         => api.get('/stories/my-draft'),

// gptAPI — add:
paraphrase: (text, mode) => api.post('/gpt/paraphrase', { text, mode }),

// authAPI — add:
updateProfile: (data) => api.put('/auth/profile', data),
```

---

### `frontend/src/App.jsx`

```jsx
// New lazy import:
const StoryEditorPage = lazy(() => import('./pages/StoryEditorPage'))

// New routes inside <Route element={<MainLayout />}>:
// NOTE: /stories/new must be BEFORE /stories/:storyId to avoid param capture
<Route path="/stories/new"           element={<StoryEditorPage showToast={showToast} />} />
<Route path="/stories/:storyId/edit" element={<StoryEditorPage showToast={showToast} />} />
```

---

## New Frontend Component Signatures

### `StoryEditorPage.jsx`
```jsx
// Props: { showToast }
// Shell only — no logic
export default function StoryEditorPage({ showToast }) {
  return <StoryEditorContainer showToast={showToast} />
}
```

---

### `StoryEditorContainer.jsx`
```jsx
// All state, refs, data-fetching, and event handling

// ── State (single object — React best practice) ──────────────────
const [state, setState] = useState({
  title:      '',
  content:    '',
  storyId:    null,     // null = create mode
  worldId:    null,
  worldName:  '',
  format:     'markdown',
  saveStatus: 'unsaved',   // 'unsaved'|'saving'|'saved'|'error'
  savedAt:    null,        // ISO string of last successful save
  isLoading:  true,
  error:      null,
  viewMode:   'split',     // 'edit'|'split'|'preview'
  signature:  null,        // loaded from auth/me
})

// ── Refs (NOT state — must not trigger re-renders) ────────────────
const debounceTimer = useRef(null)    // pending 30s save timer
const lastSaved     = useRef({})      // { title, content } snapshot (BR-1)
const storyIdRef    = useRef(null)    // survives async POST→PATCH (EC-6)
const textareaRef   = useRef(null)    // textarea DOM node (passed to hook)

// ── GPT state (separate from editor state — different concern) ────
const [gptState, setGptState] = useState({
  isLoading:    false,
  suggestions:  [],         // string[3] | []
  selectionText: '',
  selectionRange: null,     // { start, end }
})

// ── Derived (useMemo — BR-5) ─────────────────────────────────────
const wordCount   = useMemo(() => countWords(state.content), [state.content])
const readingTime = useMemo(() => Math.max(1, Math.ceil(wordCount / 200)), [wordCount])
const outline     = useMemo(() => extractHeadings(state.content), [state.content])

// ── Toolbar actions (from hook) ──────────────────────────────────
const mdEditor = useMarkdownEditor({
  textareaRef,
  content: state.content,
  onChange: useCallback((content) =>
    setState(s => ({ ...s, content, saveStatus: 'unsaved' })), []),
})

// ── Callbacks (all useCallback) ──────────────────────────────────
const handleTitleChange    // updates title, schedules save
const scheduleSave         // clears old timer, sets 30s timer
const performSave          // POST (create) or PATCH (edit), checks lastSaved
const handleManualSave     // clearTimeout + immediate performSave
const handlePublish        // PUT visibility='private', update saveStatus
const handleViewModeChange // updates state.viewMode
const handleSelectionChange// tracks selected text + range for GPT
const handleParaphraseRequest(mode)  // calls gptAPI.paraphrase
const handleSuggestionApply(suggestion) // replaces selection range
const handleGptDismiss     // resets gptState

// ── Effect: mount ────────────────────────────────────────────────
// If storyId param → fetch story data
// Else → read worldId from searchParams; validate present (BR-7)
// Also fetch auth/me for signature

// ── Effect: unmount cleanup (EC-2) ──────────────────────────────
useEffect(() => () => {
  clearTimeout(debounceTimer.current)
  // flush if pending change exists
  if (storyIdRef.current && hasUnsavedChanges()) performSave()
}, [])

// ── Render ───────────────────────────────────────────────────────
// Passes all state + callbacks to StoryEditorView
```

---

### `hooks/useMarkdownEditor.js`
```js
// Input: { textareaRef, content, onChange }
// Returns: stable object of toolbar action functions (all useCallback)

function useMarkdownEditor({ textareaRef, content, onChange }) {
  // Core: read selection from DOM
  const getSelection = () => ({
    start: textareaRef.current.selectionStart,
    end:   textareaRef.current.selectionEnd,
    text:  content.slice(start, end),
  })

  // Core: replace range, reposition cursor via requestAnimationFrame
  const replaceRange = useCallback((start, end, replacement, newCursorStart, newCursorEnd) => {
    const next = content.slice(0, start) + replacement + content.slice(end)
    onChange(next)
    requestAnimationFrame(() => {
      const el = textareaRef.current
      if (!el) return
      el.setSelectionRange(newCursorStart ?? start + replacement.length,
                           newCursorEnd   ?? newCursorStart ?? start + replacement.length)
      el.focus()
    })
  }, [content, onChange, textareaRef])

  // Inline toggle (bold, italic, strikethrough, code)
  const toggleInline = useCallback((marker) => { ... }, [content, onChange, replaceRange])

  // Line-prefix toggle (headings, bullets, numbering)
  const toggleLinePrefix = useCallback((prefix, type) => { ... }, [content, onChange, replaceRange])

  // Multi-line transform (indent, dedent, bullets, numbering)
  const transformLines = useCallback((transformFn) => { ... }, [content, onChange, replaceRange])

  return {
    bold:          () => toggleInline('**'),
    italic:        () => toggleInline('*'),
    strikethrough: () => toggleInline('~~'),
    inlineCode:    () => toggleInline('`'),
    heading:       (level) => toggleLinePrefix('#'.repeat(level) + ' ', 'heading'),
    horizontalRule:() => { /* insert \n\n---\n\n at cursor */ },
    unorderedList: () => transformLines((line) => `- ${line}`, 'ul'),
    orderedList:   () => transformLines((line, i) => `${i + 1}. ${line}`, 'ol'),
    indent:        () => transformLines((line) => `    ${line}`, 'indent'),
    dedent:        () => transformLines((line) => line.startsWith('    ') ? line.slice(4) : line, 'dedent'),
    insertLink:    (label, url) => { /* [label](url) */ },
    insertImage:   (alt, url)   => { /* ![alt](url) */ },
    insertSignature: (sig)      => { /* append \n\n---\n*— sig* */ },
  }
}
```

---

### `StoryEditorView.jsx`
```jsx
// Pure presentational — no state, no API calls
// Props: all state values + all callbacks from container

function StoryEditorView({
  title, content, format, wordCount, readingTime,
  saveStatus, savedAt, worldName, viewMode, isLoading, error,
  isCreateMode, outline, signature,
  mdEditor, textareaRef,
  gptState,
  onTitleChange, onManualSave, onViewModeChange,
  onPublish, onSelectionChange,
  onParaphraseRequest, onSuggestionApply, onGptDismiss,
}) {
  return (
    <div className="h-screen flex flex-col bg-base-100">
      <EditorHeader ... />
      <div className="flex flex-1 overflow-hidden">
        <LeftPanel ... />
        <RightPanel ... />
      </div>
    </div>
  )
}
```

---

### `EditorHeader.jsx`
```jsx
// Props: title, saveStatus, savedAt, wordCount, readingTime,
//        worldName, viewMode, isCreateMode,
//        onTitleChange, onManualSave, onViewModeChange, onPublish
//
// Layout (all DaisyUI tokens, no hardcoded colors):
// [← Back]  [input: title ___]  [badge: Draft/Saving/Saved/Error]
//           [Edit|Split|Preview tabs]   [N words ~X min]  [Publish btn]
//
// Browser <title> updated via useEffect on title + saveStatus
// Badge colors: badge-warning/badge-info/badge-success/badge-error
```

---

### `LeftPanel.jsx`
```jsx
// Props: mdEditor, outline, gptState, signature,
//        onSelectionChange, onParaphraseRequest,
//        onSuggestionApply, onGptDismiss
//
// Sections (top to bottom):
//   <MarkdownToolbar mdEditor={mdEditor} signature={signature} />
//   <GptToolsPanel gptState={gptState}
//                  onRequest={onParaphraseRequest}
//                  onApply={onSuggestionApply}
//                  onDismiss={onGptDismiss} />
//   <DocumentOutline outline={outline} textareaRef={textareaRef} />
//
// Width: fixed w-56 (224px), scrollable vertically
// Border right: border-r border-base-300
```

---

### `RightPanel.jsx`
```jsx
// Props: content, format, viewMode, textareaRef,
//        onContentChange, onSelectionChange
//
// Renders based on viewMode:
//   'edit':    <textarea> full width
//   'split':   <textarea> w-1/2  |  <MarkdownPreview> w-1/2  (scroll-synced)
//   'preview': <MarkdownPreview> full width (read-only)
//
// Scroll sync (EC-8):
//   onScroll of textarea → compute ratio = scrollTop / (scrollHeight - clientHeight)
//   → set previewRef.current.scrollTop = ratio * (scrollHeight - clientHeight)
//   isScrollSyncing ref prevents infinite loop
//
// <MarkdownPreview>: react-markdown inside div with className="prose max-w-none"
//   Only renders markdown when format === 'markdown' (BR-9)
//   Otherwise: <pre className="whitespace-pre-wrap"> (plain text)
//
// Tab key in textarea → calls mdEditor.indent(), event.preventDefault() (BR-12)
// Shift+Tab → calls mdEditor.dedent(), event.preventDefault()
```

---

### `MarkdownToolbar.jsx`
```jsx
// Props: mdEditor (all action fns), signature (string|null)
//
// Buttons (btn btn-ghost btn-sm, DaisyUI):
//   B  I  S  `  |  H1 H2 H3  |  ─  |  • 1. ⇥  |  🔗  🖼️  ✍
//
// Link button: toggles inline URL <input> popover on click
// Image button: toggles two-field popover (alt + URL)
// Signature (✍):
//   - disabled + tooltip "Already inserted" if signature in content
//   - shows "Set signature" mini-input if user.signature is null
//   - otherwise calls mdEditor.insertSignature(signature)
```

---

### `DocumentOutline.jsx`
```jsx
// Props: outline (array of { level, text, lineIndex }), textareaRef
//
// outline derived in container via useMemo (extractHeadings)
// Click → scroll textarea to line:
//   Compute char offset of heading → measure scrollTop proportionally
//   textareaRef.current.scrollTop = computed value
//
// Renders nothing when outline is empty
```

---

### `GptToolsPanel.jsx`
```jsx
// Props: gptState { isLoading, suggestions, selectionText },
//        onRequest(mode), onApply(suggestion), onDismiss
//
// States:
//   idle (no selection or selection < 10 chars): buttons disabled, hint text
//   active (selection >= 10 chars): Paraphrase + Expand buttons enabled
//   loading: spinner, buttons disabled
//   suggestions: 3 items each with Apply button + Clear button
```

---

## Component Tree

```
App.jsx
└── StoryEditorPage              ← thin shell (new)
    └── StoryEditorContainer     ← all state + data-fetching (new)
        ├── useMarkdownEditor    ← custom hook, toolbar actions (new)
        └── StoryEditorView      ← pure layout (new)
            ├── EditorHeader     ← title + status + controls (new)
            ├── LeftPanel        ← tools column (new)
            │   ├── MarkdownToolbar    ← formatting buttons (new)
            │   ├── GptToolsPanel      ← paraphrase/expand (new)
            │   └── DocumentOutline    ← heading jump list (new)
            └── RightPanel       ← writing area (new)
                ├── <textarea>   ← plain HTML
                └── MarkdownPreview (react-markdown, in split/preview)
```

---

## New Dependencies (frontend)

```json
"react-markdown": "^9.x",
"@tailwindcss/typography": "^0.5.x"
```

`@tailwindcss/typography` must also be added to `tailwind.config.js` plugins array.
