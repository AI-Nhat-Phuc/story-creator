---
name: autosave-resilience
description: Use this skill when editing auto-save logic, save-status indicators, or authentication token resilience across cold starts / network errors. Covers debounced auto-save with retry, status badges, and the "don't log out on transient errors" rule for AuthContext. Triggers when editing frontend/src/contexts/AuthContext.jsx, any container with auto-save (StoryEditorContainer, NovelContainer, profile forms), or adding a new save-status UI.
---

# autosave-resilience — Auto-save & Session Resilience

This skill applies to every form/editor that auto-saves, plus the auth token lifecycle that must survive transient backend failures.

## Auto-save pattern

### Debounce windows

- **Fast save (typing indicator, small forms)**: 500ms after last keystroke
- **Editor save (story/novel content)**: 30s after last keystroke
- Pick based on the cost of the save and how "chatty" the endpoint tolerates

### Required triggers (in addition to debounce)

- `beforeunload` — flush any pending save synchronously (use `navigator.sendBeacon` if possible)
- Ctrl+S / Cmd+S — immediate save with `preventDefault` on the event
- Route change — flush before navigation (via `useBlocker` or cleanup effect)

### Retry

- Up to 3 attempts, exponential backoff (1s, 2s, 4s)
- Only retry on network errors / 5xx. Never retry 4xx (client error — data is bad)
- Between retries, UI shows "Retrying save…" in the status badge

## Save-status badge

Shared visual vocabulary across all auto-saving surfaces:

| State         | When                                               | Visual                          |
|---------------|----------------------------------------------------|----------------------------------|
| Draft         | Fresh unsaved changes, before first save attempt   | Neutral text                    |
| Saving…       | Request in flight                                  | Spinner + text                  |
| Saved         | Last save succeeded                                | Checkmark + relative time       |
| Unsaved       | Pending save but user just typed (debounce active) | Yellow dot                      |
| Save failed   | 3 retries exhausted                                | Red + "Retry" button            |

Use i18n keys (see `i18n` skill) for all badge labels.

## Conflict handling

- Last-write-wins across all autosave surfaces — no OT/CRDT
- No version field, no "stale save" detection
- Co-author concurrent edit: losing edit is silently overwritten; users see each other's latest content on next load

## Auth token resilience (CRITICAL)

The bug fixed in `fix_session_loss_on_deploy` — Vercel cold-starts were timing out auth verification and logging users out. Never regress this.

**Rule:** `AuthContext` clears the JWT token **only on HTTP 401 responses**. All other errors (network error, timeout, 5xx, CORS failure) must keep the token.

```js
// ✅ CORRECT
if (error.response?.status === 401) {
  localStorage.removeItem('jwt_token')
  setUser(null)
}
// Otherwise: log error, show a toast if appropriate, KEEP the token

// ❌ WRONG
if (error) {
  localStorage.removeItem('jwt_token')  // logs out on network blips
}
```

- On auth verify failure (non-401), display a transient error indicator but keep the user "logged in" — next user action will re-verify against a warm server
- Never call `setUser(null)` on an `AbortError`, timeout, or `error.response === undefined`

## Checklist when adding a new auto-saving form

- [ ] Debounce window picked (500ms vs 30s)
- [ ] Flush on `beforeunload` and on unmount/route-change
- [ ] Manual save shortcut (Ctrl+S) wired with `preventDefault`
- [ ] Retry with exponential backoff on network/5xx only
- [ ] Status badge states all have i18n strings
- [ ] Save endpoint uses `PUT` or `PATCH` (not POST — saves are idempotent)
- [ ] Never call `signOut()` or clear tokens from the save-failure path
