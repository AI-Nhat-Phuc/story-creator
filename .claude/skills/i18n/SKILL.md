---
name: i18n
description: Use this skill EVERY TIME you add, modify, or write user-facing text in frontend code (JSX/TSX components, pages, containers, alerts, toasts, button labels, headings, placeholders, error messages). Ensures all UI strings go through react-i18next instead of being hardcoded. Triggers when editing files under frontend/src/components/, frontend/src/pages/, frontend/src/containers/.
---

# i18n — react-i18next workflow for story-creator

This project ships in **Vietnamese (vi, default)** and **English (en)**. ALL user-facing text in the frontend MUST go through `react-i18next` — never hardcode strings in JSX.

## When this skill applies

Use this skill whenever you:
- Add a new JSX text node, button label, heading, placeholder, alt text, title attribute
- Add a `showToast(...)` / `alert(...)` / `confirm(...)` call with a string
- Add a new error message string
- Add a Helmet `<title>` or `<meta description>`
- Modify any existing user-facing string

It does NOT apply to:
- Console logs (`console.log`, `console.error`)
- Debug-only messages
- Test fixtures
- Backend Python code (separate concern)
- Code comments
- Variable names / IDs / class names

## Setup files

- Init: `frontend/src/i18n/index.js` (already configured)
- Locales: `frontend/src/i18n/locales/vi.json` and `frontend/src/i18n/locales/en.json`
- Both files MUST stay in sync (every key in one MUST exist in the other)

## Required pattern

```jsx
import { useTranslation } from 'react-i18next'

function MyComponent() {
  const { t } = useTranslation()
  return <button>{t('actions.save')}</button>
}
```

For interpolation:
```jsx
{t('common.deleteConfirm', { name: story.title })}
```

```json
// vi.json
"deleteConfirm": "Bạn có chắc muốn xóa \"{{name}}\"?"
// en.json
"deleteConfirm": "Are you sure you want to delete \"{{name}}\"?"
```

## Forbidden patterns

```jsx
// ❌ Hardcoded Vietnamese
<button>Lưu</button>
showToast('Đã xóa thành công', 'success')
<input placeholder="Nhập tên..." />

// ❌ Hardcoded English
<h1>Welcome</h1>
alert('Failed to load')

// ❌ Mixed
<span>{t('common.year')} 2024 — {story.title}</span>  // OK if "Year" is the only translatable part
```

## Key naming convention

Look at existing keys in `vi.json` first. The current top-level namespaces:

- `common.*` — shared atoms (loading, save, cancel, year, unknown, etc.)
- `actions.*` — verbs (create, edit, delete)
- `pages.*` — per-page strings (`pages.storyDetail.loadError`, etc.)
- `meta.*` — Helmet titles/descriptions
- `nav.*` — navigation items
- `auth.*` — login/register flow

Pattern: `{namespace}.{feature}.{specificString}`. Examples:
- `pages.storyReader.previousChapter`
- `pages.novel.loadingMore`
- `common.readMore`

If the string is reused 2+ times → put under `common.*` or `actions.*`.

## Workflow when adding text

1. **Identify the string** you want to add to a component
2. **Check `vi.json`** — does an existing key already cover it? Reuse if yes
3. **Pick a key** following naming convention
4. **Add to BOTH `vi.json` AND `en.json`** at the same path — never just one
5. **Import `useTranslation`** at top of component if not already imported
6. **Call `const { t } = useTranslation()`** inside the component body
7. **Use `{t('your.key')}`** instead of the literal string
8. **Verify alphabetical / logical order** within the JSON section

## Validation checklist (run mentally before finalizing)

- [ ] No hardcoded VN/EN strings in JSX text content
- [ ] No hardcoded VN/EN in attributes (`title`, `placeholder`, `aria-label`, `alt`)
- [ ] No hardcoded strings in `showToast`, `alert`, `confirm`
- [ ] Every new key exists in BOTH `vi.json` AND `en.json`
- [ ] Translations are accurate (not just "TODO" or copy of VN)
- [ ] Interpolation variables match between the two locales
- [ ] Nested key paths follow existing namespace structure

## Quick reference — common reused keys

| Use case | Key |
|----------|-----|
| Loading state | `t('common.loading')` |
| Generic error | `t('common.error')` |
| Delete button | `t('actions.delete')` |
| Save button | `t('actions.save')` |
| Cancel button | `t('common.cancel')` |
| Confirm delete | `t('common.deleteConfirm', { name })` |
| Not found | `t('common.notFound')` |
| Unknown | `t('common.unknown')` |

Search `vi.json` before inventing a new key.

## Counter-examples — when NOT to translate

- Brand/proper names: "Story Creator", user-typed titles, character names
- Numbers, dates rendered via `Intl.DateTimeFormat`
- IDs (UUIDs, slugs)
- Code blocks / JSON debug output
- ARIA roles (those are standardized strings)

## After-edit verification

When you finish editing, mentally run:
1. Grep the diff for any new string literals in JSX → must be translated
2. Open `vi.json` and `en.json` side by side → keys must match 1:1
3. If you added any `t('foo.bar.baz')` → confirm `foo.bar.baz` exists in both files

If any check fails, fix before declaring the task done.
