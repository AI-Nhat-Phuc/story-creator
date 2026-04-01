# Task Spec — Story Editor Page (v3)

## Routes
- `/stories/new?worldId=<id>` — create mode: blank editor, story not yet persisted
- `/stories/:storyId/edit` — edit mode: loads existing story

---

## SUB-1: Two-Panel Layout + View Modes + Keyboard Shortcuts

### Layout
```
┌────────────────────────────────────────────────────────────────┐
│  HEADER                                                        │
│  [←] [Story Title ____________] — Draft | Saving… | Saved     │
│  [Edit | Split | Preview]    [1,234 words  ~6 min]  [Publish] │
├───────────────────┬────────────────────────────────────────────┤
│  LEFT PANEL       │  RIGHT PANEL                               │
│  ─ Formatting ─   │  Edit:    <textarea>                       │
│  B I S ` H1H2H3  │  Split:   <textarea> | <preview>           │
│  — • 1. ⇥ 🔗 🖼️ ✍  │  Preview: <react-markdown>                 │
│  ─ GPT Tools ─    │                                            │
│  [Paraphrase]     │                                            │
│  [Expand]         │                                            │
│  [suggestions…]   │                                            │
│  ─ Outline ─      │                                            │
│  # Heading 1      │                                            │
│    ## Heading 2   │                                            │
└───────────────────┴────────────────────────────────────────────┘
```

### View modes (toggle in header)
- **Edit**: right panel = textarea full width
- **Split**: right panel split 50/50 — textarea left, rendered preview right; scroll positions sync via scroll-percentage mirroring
- **Preview**: right panel = rendered markdown only (read-only)

### Keyboard shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+B` | Bold |
| `Ctrl+I` | Italic |
| `Ctrl+K` | Link |
| `Ctrl+1/2/3` | Heading H1/H2/H3 |
| `Ctrl+S` | Manual save (flush debounce immediately) |
| `Tab` (in textarea) | Indent selected lines |
| `Shift+Tab` (in textarea) | Dedent selected lines |
| `Escape` | Close GPT suggestions / link popup |

---

## SUB-2: Markdown Toolbar + Textarea Implementation + Preview

### Textarea implementation approach

The editor uses a **plain `<textarea>` + custom `useMarkdownEditor` hook**.
No WYSIWYG library — full control, lightweight, theme-compatible.

The hook exposes toolbar action functions. Each action:
1. Reads `textareaRef.current.selectionStart` / `selectionEnd`
2. Computes the new content string
3. Calls `onChange(newContent)`
4. After React re-renders, calls `el.setSelectionRange(...)` via `requestAnimationFrame` to reposition cursor

All toolbar actions are **toggleable**: applying the same format twice removes it.

---

### Tool-by-tool behavior

#### Bold — `**text**`
| Condition | Action | Cursor after |
|-----------|--------|-------------|
| Text selected | Wrap: `**{selected}**` | After closing `**` |
| Selection already bold (preceded + followed by `**`) | Remove the `**` markers | Collapsed to end of unwrapped text |
| No selection | Insert `**bold text**`, select `bold text` | Selection on "bold text" |

#### Italic — `*text*`
Same pattern as Bold with single `*`. When checking toggle, checks for `*` but not `**` (to avoid collision with bold).

#### Strikethrough — `~~text~~`
Same pattern as Bold with `~~`.

#### Inline code — `` `text` ``
Same pattern as Bold with single backtick.

#### Heading — `# ` / `## ` / `### ` (H1/H2/H3 buttons)
Operates on the **entire current line** (expands selection to line boundaries).
| Condition | Action |
|-----------|--------|
| Line has no heading prefix | Prepend `# ` (or `## `, `### `) |
| Line has same heading level | Remove the prefix (toggle off) |
| Line has different heading level | Replace with new prefix |
Multi-line selection: apply to **each selected line** independently.

#### Horizontal Rule — `---`
Inserts `\n\n---\n\n` at cursor position. No toggle.

#### Unordered list — `- item`
Operates on all selected lines (or current line if no selection).
| Condition | Action |
|-----------|--------|
| Lines have no list prefix | Prepend `- ` to each line |
| Lines already start with `- ` | Remove `- ` prefix (toggle off) |

#### Ordered list — `1. item`
Same as unordered but with sequential numbers `1.`, `2.`, `3.`…
Toggle: if lines start with `\d+\. `, remove the prefix.

#### Indent (`Tab` key or toolbar `⇥`)
Prepend `    ` (4 spaces) to each selected line (or current line).

#### Dedent (`Shift+Tab`)
Remove up to 4 leading spaces from each selected line.

#### Link — `[text](url)`
| Condition | Action |
|-----------|--------|
| Text selected | Show URL input popover → insert `[{selected}](url)` |
| No selection | Show URL + label popover → insert `[label](url)`, select "label" |
The URL popover is a small inline `<input>` that appears below the toolbar. `Enter` confirms, `Escape` cancels.

#### Image — `![alt](url)`
Shows a two-field popover (Alt text + Image URL).
Inserts `![alt](url)` at cursor. No file upload — URL-based only.

#### Signature — `— Username`
| Condition | Action |
|-----------|--------|
| Signature not yet in content | Append `\n\n---\n*— {signature}*` at end of document |
| Signature already in content | Button disabled with tooltip "Already inserted" |
| User has no signature set | Button shows "Set signature first" → opens a small inline input to set it; saved to backend via `PUT /api/auth/profile` |

Signature format stored in `user.metadata.signature` (defaults to `— {username}` if not set).
Duplicate check: `content.includes(signatureText)` before inserting (BR-10).

---

### How formatting appears per view mode

| Mode | What user sees after applying Bold to "hello" |
|------|-----------------------------------------------|
| **Edit** | Raw text: `**hello**` in the textarea. Cursor repositioned after closing `**`. |
| **Split** | Left: raw `**hello**`. Right: rendered **hello** in preview — updates in real-time. |
| **Preview** | Only rendered output: **hello**. Toolbar buttons hidden (read-only). |

The preview panel uses `react-markdown` + `@tailwindcss/typography`'s `prose` class so rendered output inherits the active DaisyUI theme's typography.

---

### `useMarkdownEditor` hook signature
```js
// frontend/src/hooks/useMarkdownEditor.js
function useMarkdownEditor({ textareaRef, content, onChange }) {
  return {
    bold(),
    italic(),
    strikethrough(),
    inlineCode(),
    heading(level: 1 | 2 | 3),
    horizontalRule(),
    unorderedList(),
    orderedList(),
    indent(),
    dedent(),
    insertLink(label, url),
    insertImage(alt, url),
    insertSignature(signatureText),
  }
}
```

All functions are stable references (`useCallback` with `[content, onChange]` deps).

---

### Document outline (left panel, bottom section)
- Extracts all `# `, `## `, `### ` headings from `content` via `useMemo` (debounced update 300ms)
- Renders as a clickable list; click scrolls the textarea to the corresponding line
- Scroll-to-line: compute character offset of heading in content → set `textarea.scrollTop` proportionally
- Hidden when content has no headings

---

## SUB-3: Auto-save as Draft + Title Status + Resume Draft

### Save timing
- 30 seconds after the user **stops typing** (debounce via `useRef` timer)
- `Ctrl+S` or toolbar save icon: flush immediately
- On unmount (`useEffect` cleanup): flush immediately (EC-2)
- Skip save if content and title unchanged vs `lastSaved` ref snapshot (BR-1)

### Title / browser `<title>` status
```
[Story Name] — Draft     ← local changes not yet saved
[Story Name] — Saving…   ← request in flight
[Story Name] — Saved     ← last save succeeded (shows HH:MM timestamp)
[Story Name] — Error ↺   ← last save failed; ↺ is a retry button
```

### Draft lifecycle
- Stories created from the editor always start with `visibility='draft'`
- **Publish button** (header right) calls `PUT /api/stories/:id` with `{ visibility: 'private' }` → story becomes private (no longer a draft)
- After publishing: status shows `Saved`, Publish button changes to `Published ✓`

### Resume draft flow
- Any "New Story" entry point first calls `GET /api/stories/my-draft`
  - Draft found → navigate to `/stories/:draftId/edit` + toast `"Resuming your draft"`
  - No draft → navigate to `/stories/new?worldId=<id>`

---

## SUB-4: Backend Changes

### A. Story model — `format` field
```python
# api/core/models/story.py
format: str = 'plain'   # 'plain' | 'markdown'
```
- All existing stories default to `'plain'`
- New stories created via the editor: `format='markdown'`
- Added to `to_dict()`, `from_dict()`, `CreateStorySchema`, `UpdateStorySchema`

### B. One-draft-per-user rule
- `POST /api/stories` with `visibility='draft'`: query user's stories for any with `visibility='draft'`
  - Found → 409 ConflictError `"You already have a draft. Finish or publish it first."`
  - Not found → create normally
- `PUT /api/stories/:id` changing `visibility` to `'draft'`: same check (excluding current story)

### C. New endpoint: `GET /api/stories/my-draft`
```
Auth: required
200: { data: { story: StoryDict } }   ← user's current draft
200: { data: { story: null } }        ← no draft exists
```

### D. User model — `signature` field in metadata
```python
# user.metadata['signature']: str | None  (default None)
```
- Displayed as `— {signature}` in the editor when inserting
- Falls back to `— {username}` if not set

### E. New endpoint: `PUT /api/auth/profile`
```
Auth: required
Body: { signature?: string (max 200 chars) }
200:  { data: { user: UserDict } }
400:  validation error
```
Updates `user.metadata['signature']`.

---

## SUB-5: GPT Writing Assistant (Left Panel)

- User selects ≥ 10 chars in textarea → left panel "GPT Tools" section activates: **Paraphrase** and **Expand** buttons become clickable
- Clicking calls `POST /api/gpt/paraphrase` with `{ text: selectedText, mode }`
- While loading: buttons show spinner, selection is preserved
- On success: 3 numbered suggestions appear below buttons in left panel, each with an **Apply** button
- Apply: replaces the selected range in textarea, panel resets to idle
- **Clear** button dismisses suggestions without changing text
- Mock mode: suggestions show `[mock]` prefix
- `Escape` key clears suggestions panel

---

## SUB-6: Theme Compatibility

- All colors: DaisyUI semantic tokens only (`bg-base-100`, `bg-base-200`, `text-base-content`, `border-base-300`, `btn-primary`, etc.)
- No hardcoded hex / Tailwind palette colors (`gray-*`, `slate-*`, etc.)
- Markdown preview: `prose` class from `@tailwindcss/typography` (inherits active theme fonts + colors)
- Toolbar buttons: `btn btn-ghost btn-sm` (active theme styling)
- Save badge: `badge-warning` (Draft), `badge-info` (Saving…), `badge-success` (Saved), `badge-error` (Error)
- Left/right panel divider: `border-base-300`
- Textarea: `bg-base-100 text-base-content` with `focus:outline-none` (no browser default blue ring)

---

## API Contract

### Backend endpoints (new/modified)
```
GET  /api/stories/my-draft
  Auth: required
  200: { data: { story: StoryDict | null } }

POST /api/stories
  Body: { world_id, title, content, visibility, format? }
  409:  ConflictError "You already have a draft story."   ← new

PUT  /api/stories/:id
  Body: { title?, description?, visibility?, format? }
  409:  ConflictError "You already have a draft story."   ← new (when changing to draft)

PUT  /api/auth/profile                                    ← new
  Auth: required
  Body: { signature?: string }
  200:  { data: { user: UserDict } }

PATCH /api/stories/:id     ← already exists, unchanged
POST  /api/gpt/paraphrase  ← already exists, unchanged
```

### New frontend API wrappers
```js
storiesAPI.patch(id, data)    // PATCH /stories/:id
storiesAPI.getMyDraft()       // GET  /stories/my-draft
gptAPI.paraphrase(text, mode) // POST /gpt/paraphrase
authAPI.updateProfile(data)   // PUT  /auth/profile
```

---

## Business Rules
- BR-1: Auto-save fires only when content or title differs from last-saved snapshot (`useRef`)
- BR-2: GPT tools activate only when selected text ≥ 10 characters
- BR-3: Editor requires authentication — redirect to `/login` if no token
- BR-4: 403 from backend → error toast, editor switches to read-only
- BR-5: Word count and reading time via `useMemo` — never separate state variables
- BR-6: One draft per user — enforced by backend (409) + frontend resume flow
- BR-7: `worldId` required in create mode — missing → redirect to `/stories` with error toast
- BR-8: Stories created from editor default to `format='markdown'`
- BR-9: Existing stories with `format='plain'` shown as-is in preview (no markdown parsing)
- BR-10: Signature can appear at most once per story — toolbar button disabled if already present
- BR-11: Toolbar buttons disabled in Preview mode (read-only)
- BR-12: Tab key inside textarea triggers indent (not focus change) — `event.preventDefault()` required

## Edge Cases
- EC-1: Story 404 in edit mode → redirect to `/stories` with error toast
- EC-2: Navigate away → `useEffect` cleanup flushes pending 30s save immediately
- EC-3: GPT request fails → error toast, suggestions panel clears, selection preserved
- EC-4: Title empty → auto-save skipped in create mode until title ≥ 1 char
- EC-5: Content > 50k chars → word count / outline via `useMemo` with content as dep
- EC-6: `POST /api/stories` succeeds but navigate fails → `storyIdRef` holds new ID so retry uses `PATCH`
- EC-7: User opens "New Story" while draft exists → redirect to draft + toast (resume flow)
- EC-8: Split mode scroll sync — mirror `scrollTop / (scrollHeight - clientHeight)` ratio, guarded by `isScrollSyncing` ref to prevent infinite loop
- EC-9: Bold applied to text that is part of bold-italic (`***text***`) — check for `***` before `**` to avoid partial unwrap
- EC-10: Signature not set → inline prompt to set it; do not insert until confirmed

## Out of Scope
- File upload for images (URL input only)
- Real-time collaborative editing
- Chapter prev/next navigation
- WYSIWYG / rich text (ProseMirror, TipTap)
- Syntax highlighting in edit mode
- Export to PDF / HTML
- Offline / service worker
- Story metadata editing (genre, time index) — remains in StoryDetailView
