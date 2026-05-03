# SSR Auth Task

Goal: forward the JWT token from a cookie into every SSR fetch so authenticated users
receive personalized data (draft/private worlds, owned stories, etc.) on the first render.

## Mechanism

1. **Client** (`AuthContext.jsx`): on login/logout, write/remove the `auth_token` cookie alongside `localStorage`
2. **SSR** (`src/utils/serverAuth.js`): read the cookie via `next/headers`, return an `Authorization` header
3. **Pages**: pass `getServerAuthHeaders()` into every SSR `fetch()`, disable cache when auth is present

---

## Step 0 — Shared infrastructure (do first, unblocks everything else)

- [ ] **`src/hooks/useCookie.js`** — `get/set/remove` utility for `document.cookie`, no library needed
- [ ] **`AuthContext.jsx`** — call `cookie.set(token)` after login, `cookie.remove()` after logout
- [ ] **`src/utils/serverAuth.js`** — export `getServerAuthHeaders()` and `isAuthenticatedOnServer()`
- [ ] **`src/utils/serverFetch.js`** — helper that merges bypass headers + auth headers + cache strategy
- [ ] **`src/components/NavigationProgress.jsx`** — 3px `bg-primary` progress bar at top of page; show on `<a>` click, complete when `usePathname()` changes; mount inside `ThemeProvider` in `Providers.jsx`

---

## Step 1 — Pages that already SSR-fetch, just need the auth header forwarded

These pages already fetch data server-side but send no token → logged-in users still see public data.

| # | File | Endpoints | Cache when authenticated |
|---|------|-----------|--------------------------|
| 1 | `app/(main)/worlds/page.jsx` | `GET /worlds` | `no-store` |
| 2 | `app/(main)/stories/page.jsx` | `GET /stories`, `GET /worlds` | `no-store` |
| 3 | `app/(main)/page.jsx` | `GET /stories`, `GET /worlds` | `no-store` |
| 4 | `app/(main)/worlds/[worldId]/novel/page.jsx` | `GET /worlds/:id/novel`, `GET /worlds/:id/novel/content` | `no-store` |

**Change per page**: add `...getServerAuthHeaders()` to headers, switch cache strategy when a token is present.

---

## Step 2 — Pure `'use client'` pages that need converting to Server Components

These pages currently render entirely client-side. For each one:
1. Remove `'use client'` from the page wrapper
2. Write an `async fetchInitialData(...)` function with the auth header
3. Pass `initialData` as a prop down to the view component

| # | File | Endpoints to prefetch | Notes |
|---|------|----------------------|-------|
| 5 | `app/(main)/stories/[storyId]/page.jsx` | `GET /stories/:id` | View: `StoryDetailPage` |
| 6 | `app/(main)/worlds/[worldId]/page.jsx` | `GET /worlds/:id` | View: `WorldDetailPage` |
| 7 | `app/(main)/stories/[storyId]/read/page.jsx` | `GET /stories/:id`, `GET /stories/:id/neighbors` | View: `StoryReaderPage` |
| 8 | `app/(main)/stories/new/page.jsx` | `GET /worlds` (populate world dropdown) | Auth required; only load user's worlds |
| 9 | `app/(main)/admin/page.jsx` | — | Verify admin role SSR, redirect if unauthorized |
| 10 | `app/(main)/admin/users/page.jsx` | `GET /admin/users` | Admin only |
| 11 | `app/stories/[storyId]/print/page.jsx` | `GET /stories/:id` | View: `StoryPrintPage` |

> **Skip SSR for** `app/(main)/stories/[storyId]/edit/page.jsx` — the TipTap editor is highly
> stateful; prefetching story data adds little value and risks conflicts with auto-save.

---

## Execution order

```
Step 0 → Step 1 (4 pages in parallel) → Step 2 (in order: 5→6→7→8→9→10→11)
```

Step 1 is the safest (no component architecture changes); do it first for quick visible impact.

---

## Technical notes

- Cookie name: `auth_token`, `SameSite=Strict`, `max-age=7d`, `path=/`
- When `isAuthenticatedOnServer() === true`: use `cache: 'no-store'` instead of `revalidate`
- `generateMetadata()` also needs the auth header when it fetches user-dependent data (e.g. title of a private novel)
- View components should accept an `initialData?: T | null` prop — if `null`, fall back to client-side fetching as before (graceful degradation)
