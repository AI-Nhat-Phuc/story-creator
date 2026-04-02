# DESIGN — Story Editor Page Frontend (v2 — novel/TipTap)

---

## Changed Files

| File | Change | Spec Clause |
|------|--------|-------------|
| `frontend/src/services/api.js` | MODIFY — add 4 API wrappers | API Contract |
| `frontend/src/App.jsx` | MODIFY — add 2 routes | Routes |
| `api/schemas/story_schemas.py` | MODIFY — add `'html'` to format OneOf | Content format change |
| `frontend/src/pages/StoryEditorPage.jsx` | NEW — thin route shell | Routes |
| `frontend/src/containers/StoryEditorContainer.jsx` | NEW — state, auto-save, GPT | Container state |
| `frontend/src/components/storyEditor/StoryEditorView.jsx` | NEW — pure layout | Component Tree |
| `frontend/src/components/storyEditor/EditorHeader.jsx` | NEW — title, status, publish | Layout → HEADER |
| `frontend/src/components/storyEditor/LeftPanel.jsx` | NEW — GPT + outline wrapper | Layout → LEFT PANEL |
| `frontend/src/components/storyEditor/NovelEditor.jsx` | NEW — novel wrapper | novel integration |
| `frontend/src/components/storyEditor/GptToolsPanel.jsx` | NEW — paraphrase/expand | GPT Tools |
| `frontend/src/components/storyEditor/DocumentOutline.jsx` | NEW — headings from TipTap JSON | Component Tree |

**Total: 3 modified, 8 new**

---

## Dependencies to install

```bash
cd frontend && npm install novel
```

`novel` bundles TipTap + bubble menu + slash commands. No separate `@tiptap/*` packages needed.

No `react-markdown`, `remark-gfm`, `@tailwindcss/typography` needed — novel uses `prose` classes internally.
Add `typography` plugin to `tailwind.config.js` for prose styles:
```js
plugins: [require('@tailwindcss/typography'), require('daisyui')]
```

---

## `api.js` additions

```js
// storiesAPI additions
patch: (id, data) => api.patch(`/stories/${id}`, data),
getMyDraft: () => api.get('/stories/my-draft'),

// gptAPI addition
paraphrase: (text, mode) => api.post('/gpt/paraphrase', { text, mode }),

// authAPI addition
updateProfile: (data) => api.put('/auth/profile', data),
```

---

## Backend schema change

`api/schemas/story_schemas.py` — add `'html'` to both schemas:
```python
# CreateStorySchema
format = fields.Str(
    validate=validate.OneOf(['plain', 'markdown', 'html']),
    load_default='plain'
)

# UpdateStorySchema
format = fields.Str(
    validate=validate.OneOf(['plain', 'markdown', 'html'])
)
```

---

## `StoryEditorPage.jsx`

```jsx
export default function StoryEditorPage({ showToast }) {
  return <StoryEditorContainer showToast={showToast} />
}
```

---

## `StoryEditorContainer` interface

```jsx
// Props
{ showToast }

// State (single useState — React best practice)
{
  title: string,
  content: string,       // HTML string
  saveStatus: 'idle' | 'saving' | 'saved' | 'error',
  isPublished: boolean,
  isLoading: boolean,
}

// GPT state (separate — independent concern)
{
  gptLoading: boolean,
  suggestions: string[],
}

// Refs
storyIdRef        // string | null — persisted ID
lastSavedRef      // { title, content } — change detection (BR-1)
saveTimerRef      // setTimeout handle
editorRef         // TipTap Editor instance (set by NovelEditor)
gptSelectionRef   // { from, to } — TipTap position for Apply

// Derived (useMemo)
wordCount   = useMemo(() => {
  const text = editorRef.current?.getText() ?? content.replace(/<[^>]+>/g, ' ')
  return text.trim() ? text.trim().split(/\s+/).length : 0
}, [content])
readTime    = useMemo(() => Math.ceil(wordCount / 200), [wordCount])
headings    = useMemo(() => {
  const json = editorRef.current?.getJSON()
  if (!json) return []
  return (json.content ?? [])
    .filter(n => n.type === 'heading')
    .map(n => ({ level: n.attrs.level, text: n.content?.[0]?.text ?? '' }))
}, [content])
```

---

## `NovelEditor` interface

```jsx
// Props
{
  initialContent: string,   // HTML or plain text
  format: string,           // 'plain' | 'markdown' | 'html'
  onUpdate: ({ html, editor, selectionLength }) => void,
  editorRef: RefObject,     // container sets editorRef.current = editor instance
}

// Implementation
import { Editor } from 'novel'

function NovelEditor({ initialContent, format, onUpdate, editorRef }) {
  // For plain/markdown stories, load as plain text
  const defaultValue = (format === 'html') ? initialContent : { type: 'doc', content: [
    { type: 'paragraph', content: [{ type: 'text', text: initialContent }] }
  ]}

  return (
    <Editor
      defaultValue={defaultValue}
      disableLocalStorage={true}
      onUpdate={({ editor }) => {
        editorRef.current = editor
        const { from, to } = editor.state.selection
        const selectionLength = editor.state.doc.textBetween(from, to, ' ').length
        onUpdate({ html: editor.getHTML(), editor, selectionLength })
      }}
      className="min-h-full"
    />
  )
}
```

---

## `StoryEditorView` props

```jsx
{
  editor: { title, content, saveStatus, isPublished, isLoading },
  wordCount: number,
  readTime: number,
  headings: Array<{ level: 1|2|3, text: string }>,
  editorRef: RefObject,
  gpt: {
    isLoading: boolean,
    suggestions: string[],
    selectionLength: number,
    onParaphrase: () => void,
    onExpand: () => void,
    onApply: (s: string) => void,
    onClear: () => void,
  },
  onTitleChange: (v: string) => void,
  onContentUpdate: ({ html, editor, selectionLength }) => void,
  onSave: () => void,
  onPublish: () => void,
  onBack: () => void,
}
```

---

## `EditorHeader` props

```jsx
{
  title: string,
  saveStatus: 'idle' | 'saving' | 'saved' | 'error',
  isPublished: boolean,
  wordCount: number,
  readTime: number,
  onTitleChange: (v: string) => void,
  onSave: () => void,
  onPublish: () => void,
  onBack: () => void,
}
```

Layout (single row):
```
[← Back]  [title input]  [status badge]  [word · time]  [Publish btn]
```

Save status badge:
| saveStatus | class | label |
|------------|-------|-------|
| `'idle'`   | `badge-warning` | Draft |
| `'saving'` | `badge-info` | Saving… |
| `'saved'`  | `badge-success` | Saved |
| `'error'`  | `badge-error` | Error |

---

## `GptToolsPanel` props

```jsx
{
  selectionLength: number,   // from editor selection update
  isLoading: boolean,
  suggestions: string[],
  onParaphrase: () => void,
  onExpand: () => void,
  onApply: (s: string) => void,
  onClear: () => void,
}
```

Buttons enabled when `selectionLength >= 10` (BR-2).

---

## `DocumentOutline` props

```jsx
{
  headings: Array<{ level: 1|2|3, text: string }>,
  // clicking a heading scrolls editor to that block (optional enhancement)
}
```

Render as indented list:
```
# Chapter One
  ## Scene 1
  ## Scene 2
# Chapter Two
```

---

## `LeftPanel` props

```jsx
{
  gpt: { ... },            // passed through to GptToolsPanel
  headings: [...],         // passed through to DocumentOutline
  userSignature: string,   // for signature insert button
  onInsertSignature: () => void,
}
```

---

## View modes

**None.** The novel editor is always the editing surface. Content is rendered inline:
- H1/H2/H3 appear as styled headings
- Bold/italic rendered in-place
- Lists, HR, links rendered
- Bubble menu appears on selection

---

## Theme notes

- `novel` renders inside a `prose` wrapper — inherits DaisyUI typography
- Override novel's default light background by wrapping in `bg-base-100 text-base-content`
- Bubble menu and slash command menu: novel injects its own popover UI — may need CSS overrides for dark theme compatibility
- All our custom components (Header, LeftPanel, etc.): DaisyUI tokens only

---

## StoryDetailPage — content rendering (update needed)

Wherever `story.content` is displayed outside the editor:
```jsx
{story.format === 'html' && (
  <div
    className="prose prose-sm max-w-none"
    dangerouslySetInnerHTML={{ __html: story.content }}
  />
)}
{story.format === 'markdown' && <ReactMarkdown>{story.content}</ReactMarkdown>}
{story.format === 'plain' && <pre className="whitespace-pre-wrap">{story.content}</pre>}
```
