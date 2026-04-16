---
name: story-editor
description: Use this skill when editing the story editor UI — the rich TipTap editor, markdown/HTML content handling, document outline, GPT paraphrase/expand tools, signature insertion, auto-save status, or publish button. Triggers when editing frontend/src/pages/StoryEditorPage.jsx, frontend/src/containers/StoryEditorContainer.jsx, frontend/src/components/NovelEditor.jsx, GptToolsPanel.jsx, DocumentOutline.jsx, MarkdownToolbar.jsx, frontend/src/hooks/useMarkdownEditor.js.
---

# story-editor — Story Writing UI Conventions

The story editor has a rich (TipTap-based) mode as its primary path. An older markdown-textarea implementation may still be referenced in some components — treat rich as canonical.

## Content format

- Story has a `format` field: `"html"` (default for new stories in rich mode), `"markdown"`, or `"plain"`
- Rich editor emits HTML and saves to `story.content`
- On first edit of an old markdown/plain story in the rich editor, re-save as HTML (update `format` to `"html"`)
- Reader pages must branch on `format` to pick the renderer (see `content-export` skill)

## Editor layout

- Two panels. Left = GPT tools + document outline. Right = editor canvas
- Rich editor uses the `novel` / TipTap library: bubble menu for inline formatting (bold, italic, link), slash commands for block formatting (heading, list, quote, code, divider)
- Top bar shows status badge and publish button

## Auto-save

- Debounce 30s after last keystroke (story editor uses 30s; shorter auto-save for general forms is the 500ms debounce from the `autosave-resilience` skill)
- Also flush on `beforeunload`
- Manual save via Ctrl+S / Cmd+S (must `preventDefault` the browser save dialog)
- Status badge states: **Draft** (initial), **Saving…** (in flight), **Saved** (with relative timestamp), **Error** (with retry button)
- Endpoint: `PUT /api/stories/:id` with `{content, format, word_count, chapter_number?}`. Last-write-wins — no version vector

## Document outline

- Extract headings from `editor.getJSON()` (not from raw HTML)
- Show H1/H2/H3 with indentation, click to scroll to node
- Hide the outline panel when there are zero headings (don't show an empty list)
- Re-extract on every `onUpdate` callback (cheap; debounce if needed)

## Word count & reading time

- Compute from `editor.getText()` in a `useMemo` tied to editor state — never separate state
- Word count is also sent to the backend on save (`word_count` field) — backend stores what frontend sends; downstream surfaces (novel list, chapter list) read `story.word_count`

## GPT tools panel

- Buttons: Paraphrase, Expand, Suggest next
- Each action sends the selected text (or full content) to a GPT route, displays suggestions in a panel
- Apply via `editor.chain().focus().insertContent(suggestion).run()` or `replaceRange` for selection
- Disable the action button while in flight; show spinner

## Signature

- Fetched from `user.metadata.signature`. Fallback to username if empty
- "Insert signature" button: appends a block at document end
- Button disabled if signature already present in content (detect via unique marker or class)
- Edit profile route: `PUT /api/auth/profile` with `{signature}` — updates `user.metadata.signature`

## Draft lifecycle

- One active draft per user. `GET /api/stories/my-draft` on "New story" page → redirect/load existing if present
- Response shape: `{story: {...}}` (nested). Read `res.data.story` — this trips people up
- Creating another draft while one exists returns 409 Conflict — handle by loading the existing draft
- **Publish** button changes `visibility` from `draft` to `private` (not public). Confirmation modal first. See `publish-workflow` skill

## Toolbar actions (markdown-mode legacy)

If touching `useMarkdownEditor`:
- All format actions toggleable (apply twice = remove formatting)
- Tab / Shift+Tab must indent / dedent with `preventDefault`
- Cursor repositioned via `requestAnimationFrame` after state update
- Signature button disabled when signature marker already present

## Common pitfalls

- Do NOT store editor state in both React state and TipTap — read from the editor instance on demand
- HTML content on display requires `dangerouslySetInnerHTML` — never from untrusted sources; our own saved content is acceptable
- All user-visible strings in this editor go through i18n (see `i18n` skill)
