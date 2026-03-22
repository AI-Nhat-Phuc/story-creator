# SPEC — Theme Selection Feature (light/dark/custom with 5 colors)

> **Status**: DRAFT
> **Phase**: SPEC
> **Date**: 2026-03-22

---

## Sub-tasks

| # | Sub-task | Files |
|---|----------|-------|
| 0 | Set up Vitest + jsdom for frontend unit testing | `frontend/package.json`, `frontend/vite.config.js` |
| 1 | Add `sc-light` and `sc-dark` DaisyUI theme definitions (5 colors each) | `tailwind.config.js` |
| 2 | Create `ThemeContext` — manages `{mode, primaryColor}`, persists to `localStorage`, applies `data-theme` or injects CSS vars | `src/contexts/ThemeContext.jsx` |
| 2.5 | Extract palette algorithm to `themeUtils.js`, write Vitest tests covering all spec clauses (red state) | `src/utils/themeUtils.js`, `src/utils/themeUtils.test.js` |
| 3 | Custom palette algorithm — implement `themeUtils.js` (make tests green) | `src/utils/themeUtils.js` |
| 4 | Create `ThemeSelector` component — 3 mode buttons, 5 color swatches, conditional color picker | `src/components/ThemeSelector.jsx` |
| 5 | Navbar integration — add ThemeSelector to desktop and mobile layouts | `src/components/Navbar.jsx` |
| 6 | Wrap `App.jsx` with `ThemeProvider`, apply initial theme before first render | `src/App.jsx` |

---

## Behavior

### B-1: Theme Modes
The app supports exactly **3 theme modes**: `light`, `dark`, `custom`.

- **Light**: Fixed palette of 5 colors centered on white and light gray.
- **Dark**: Fixed palette of 5 colors centered on dark navy and near-black.
- **Custom**: User picks a primary color (hex). The remaining 4 colors are derived from a fixed palette algorithm.

### B-2: The 5 Theme Color Slots
Every theme exposes exactly 5 semantic color roles mapped to DaisyUI variables:

| Slot | DaisyUI var | Meaning |
|------|-------------|---------|
| color-1 | `primary` | Main action color (buttons, navbar bg) |
| color-2 | `secondary` | Secondary actions, highlights |
| color-3 | `accent` | Emphasis, tags, badges |
| color-4 | `base-100` | Main page background |
| color-5 | `base-200` | Card / surface background |

No 6th custom color is introduced by the theme. Standard DaisyUI semantic colors (`success`, `error`, `warning`, `info`) retain DaisyUI defaults.

### B-3: Light Theme Colors (fixed)

| Slot | Hex | Description |
|------|-----|-------------|
| primary | `#4A90D9` | Calm blue |
| secondary | `#6BA3BE` | Muted blue-gray |
| accent | `#F5A623` | Warm amber |
| base-100 | `#FFFFFF` | Pure white |
| base-200 | `#F2F4F6` | Light gray |

### B-4: Dark Theme Colors (fixed)

| Slot | Hex | Description |
|------|-----|-------------|
| primary | `#E2E8F0` | Off-white |
| secondary | `#94A3B8` | Cool gray |
| accent | `#F59E0B` | Amber |
| base-100 | `#1E293B` | Dark navy |
| base-200 | `#0F172A` | Near black |

### B-5: Custom Theme Palette Algorithm
Given user-selected `primaryHex`, the other 4 colors are derived deterministically:

1. `primary` = `primaryHex` (user's choice)
2. `secondary` = same hue, saturation reduced by 20 percentage points, lightness increased by 15 percentage points (clamped 0–100)
3. `accent` = hue shifted +30°, same saturation and lightness as primary
4. `base-100` = `#FFFFFF` if primary relative luminance < 0.5, else `#1E293B`
5. `base-200` = same hue as primary, saturation 20%, lightness 95% (when base-100 is white) or lightness 10% (when base-100 is dark)

### B-6: ThemeSelector UI
A ThemeSelector control is accessible from the Navbar on both desktop and mobile.

- Shows **3 mode buttons**: `Light` | `Dark` | `Custom` — active mode is visually highlighted.
- Below the buttons: a row of **5 color swatches** (filled circles) representing the current theme's 5 colors in order.
- When mode = `custom`: a **color picker** (`<input type="color">`) is shown for the primary color. Changing it immediately recomputes and applies the palette.
- When mode = `light` or `dark`: the color picker is hidden.

### B-7: Persistence
Theme preference is persisted in `localStorage` under key `"sc_theme"`:
```json
{ "mode": "light" | "dark" | "custom", "primaryColor": "#rrggbb" }
```
On app load, the stored theme is read and applied synchronously before first paint (no flash).

### B-8: Theme Application Mechanism
- **Light / Dark**: Set `data-theme="sc-light"` or `data-theme="sc-dark"` on `<html>`. These themes are pre-defined in `tailwind.config.js`.
- **Custom**: Set `data-theme="sc-light"` on `<html>` (as base), then inject DaisyUI CSS custom properties in HSL format onto `document.documentElement`:
  - `--p`, `--s`, `--a` (primary, secondary, accent — oklch/hsl values DaisyUI reads)
  - `--b1`, `--b2` (base-100, base-200)
- When switching away from `custom` to a named theme, all injected inline styles are removed from `documentElement`.

---

## API Contract

Frontend-only feature. **No backend API changes.**

---

## Business Rules

- BR-1: Exactly 5 color slots per theme. No additional colors introduced.
- BR-2: Custom primary must be a valid 6-digit hex color (`#rrggbb`). Invalid values fall back to `#6366F1`.
- BR-3: Default theme on first visit (no `localStorage`) is `light`.
- BR-4: Custom palette algorithm is deterministic — same primary always produces same 5 colors.
- BR-5: ThemeSelector must function in both desktop and mobile Navbar.
- BR-6: Switching modes is instant — no loading state, no animation required.

---

## Edge Cases

- EC-1: If `localStorage` is unavailable (private browsing / security error), fall back to `light` in-memory only — no crash.
- EC-2: If stored `primaryColor` is not a valid hex, reset to `#6366F1` (indigo).
- EC-3: Switching from `custom` → `light`/`dark` must clear all inline CSS vars from `document.documentElement.style`.
- EC-4: Color picker default when entering `custom` mode = last saved primary, or `#6366F1` if none.

---

## Out of Scope

- No server-side persistence of theme preference.
- No per-page or per-component theme overrides.
- No transition animation when switching themes.
- No automatic detection of OS dark mode (`prefers-color-scheme`).
- No modification to the existing `storyCreator` DaisyUI theme entry in `tailwind.config.js`.
