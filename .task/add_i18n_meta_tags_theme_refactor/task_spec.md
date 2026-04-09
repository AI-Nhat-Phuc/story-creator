# SPEC — Add i18n, Per-page Meta Tags, and Theme Refactor

> **Status**: DRAFT
> **Phase**: SPEC
> **Date**: 2026-04-09

---

## Behavior

### 1. Internationalization (i18n)

All user-visible text in the React frontend is currently hardcoded Vietnamese.
This feature extracts every UI string into locale files and wires them through
`react-i18next`, so the language can be switched without touching component code.

- Primary locale: `vi` (Vietnamese) — all existing text migrated as-is
- Secondary locale: `en` (English) — full mirror of all keys
- Language is stored in `localStorage` (`sc_lang`) and defaults to `vi`
- A language toggle is added to the `ThemeSelector` dropdown in the Navbar
- All component text — labels, placeholders, buttons, toasts, error messages,
  confirmation dialogs, empty-state messages — must be translated

### 2. Per-page `<title>` and `<meta name="description">`

Each page sets its own HTML `<title>` and `<meta name="description">` using
`react-helmet-async`. A `<HelmetProvider>` wraps the app root. The default
(fallback) title is `Story Creator`.

| Route | Title (vi) | Meta Description (vi) |
|---|---|---|
| `/` (Dashboard) | `Dashboard – Story Creator` | `Tổng quan thống kê thế giới, câu chuyện và hạn mức của bạn.` |
| `/worlds` | `Thế giới – Story Creator` | `Khám phá và quản lý các thế giới hư cấu của bạn.` |
| `/worlds/:id` | `<Tên thế giới> – Story Creator` | `Chi tiết thế giới: nhân vật, địa điểm, câu chuyện liên quan.` |
| `/worlds/:id/novel` | `Tiểu thuyết: <Tên> – Story Creator` | `Đọc tiểu thuyết tổng hợp từ thế giới <Tên>.` |
| `/stories` | `Câu chuyện – Story Creator` | `Danh sách tất cả câu chuyện. Tạo và quản lý tác phẩm của bạn.` |
| `/stories/new` | `Tạo câu chuyện – Story Creator` | `Viết câu chuyện mới với trình soạn thảo tích hợp AI.` |
| `/stories/:id/edit` | `Chỉnh sửa: <Tên> – Story Creator` | `Chỉnh sửa nội dung câu chuyện.` |
| `/stories/:id` | `<Tên câu chuyện> – Story Creator` | `Chi tiết câu chuyện: nội dung, nhân vật, dòng thời gian.` |
| `/stories/:id/print` | `In: <Tên> – Story Creator` | `Xem trước bản in câu chuyện.` |
| `/login` | `Đăng nhập – Story Creator` | `Đăng nhập vào Story Creator để quản lý thế giới và câu chuyện của bạn.` |
| `/register` | `Đăng ký – Story Creator` | `Tạo tài khoản Story Creator miễn phí.` |
| `/admin` | `Quản trị – Story Creator` | `Bảng điều khiển quản trị hệ thống.` |

Dynamic titles (world name, story name) use the resource name once loaded;
while loading, show the static fallback title without the name portion.

### 3. Theme Refactor

The theme system (`ThemeContext`, `ThemeSelector`) is already solid. This refactor:

- Translates all hardcoded English labels in `ThemeSelector`
  (`'Light'`, `'Dark'`, `'Custom'`, `'Primary'`, `'Secondary'`, etc.) via i18n
- Removes any inline `style={{ backgroundColor: hex }}` on interactive elements
  that should instead use DaisyUI semantic classes (`bg-primary`, `btn-primary`, etc.)
- Ensures every page/component references only `bg-base-100 / bg-base-200 /
  bg-primary / text-primary-content` DaisyUI tokens — no raw hex in className or style
  for theme-able colors
- `MainLayout` already uses `bg-base-200 min-h-screen` — no change needed
- Color swatches in `ThemeSelector` are exempt: `style={{ backgroundColor }}` is
  intentional for displaying palette previews

---

## API Contract

No backend changes. All work is frontend-only.

### New files

```
frontend/src/i18n/
├── index.js          ← i18next init (language detection, fallback, namespace)
└── locales/
    ├── vi.json       ← Vietnamese strings (primary)
    └── en.json       ← English strings (mirror)
```

### Modified files

| File | Change |
|---|---|
| `frontend/package.json` | Add `i18next`, `react-i18next`, `react-helmet-async` |
| `frontend/src/main.jsx` | Import `i18n/index.js`; wrap app in `<HelmetProvider>` |
| `frontend/src/pages/*.jsx` (×11) | Add `useTranslation`, `<Helmet>` per-page |
| `frontend/src/components/Navbar.jsx` | Add `useTranslation` for nav labels, logout modal |
| `frontend/src/components/ThemeSelector.jsx` | Add `useTranslation` for mode/swatch labels; add language toggle |
| `frontend/src/components/RoleBadge.jsx` | Translate role labels if hardcoded |
| `frontend/src/containers/*.jsx` (×4) | Add `useTranslation` for inline strings |

---

## Business Rules

1. **Locale key structure**: flat namespaced dot-notation — e.g. `pages.dashboard.title`,
   `nav.worlds`, `common.loading`, `actions.create`.
2. **Missing key fallback**: i18next falls back to `vi` if an `en` key is missing.
3. **Language persistence**: selected language saved to `localStorage` key `sc_lang`.
4. **SSR compatibility**: `react-helmet-async` is used (not deprecated `react-helmet`)
   to support potential future SSR with Vercel.
5. **Dynamic titles**: pages that show a resource name (world, story) use the
   resource's `.name` field once the API response arrives. While `loading === true`,
   the title omits the name: e.g. `Thế giới – Story Creator`.
6. **Theme swatch exemption**: color swatches in `ThemeSelector` keep
   `style={{ backgroundColor }}` — this is intentional display of a color value,
   not a theme anti-pattern.
7. **No functionality removed**: all existing theme modes (light / dark / custom)
   remain. Language toggle is additive only.

---

## Edge Cases

- World/story name contains special HTML characters → `react-helmet-async` escapes
  these automatically in `<title>`.
- Resource not found (404) → title stays as generic page title without name.
- User has `localStorage` blocked (private browsing) → i18n defaults to `vi` silently.
- Both locale files must have identical key sets; missing `en` keys fall back to `vi`.
- `StoryEditorPage` serves both `/stories/new` (create) and `/stories/:id/edit` (edit)
  from the same component — title must differ based on whether `storyId` param exists.

---

## Out of Scope

- Server-side rendering (SSR) / Open Graph meta tags (`og:title`, `og:image`, etc.)
- Language auto-detection from browser `Accept-Language` header
- RTL (right-to-left) language support
- Backend API response translation
- Adding languages beyond `vi` and `en`
- Changing the default language to English
- Modifying the DaisyUI theme palette or adding new DaisyUI themes
- Translating GPT-generated content
