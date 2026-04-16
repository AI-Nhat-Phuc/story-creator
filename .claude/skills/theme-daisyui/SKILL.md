---
name: theme-daisyui
description: Use this skill when editing theme code — DaisyUI color tokens, light/dark/custom theme logic, ThemeSelector UI, ThemeContext, palette derivation utilities, or `data-theme` / CSS-var injection. Triggers when editing frontend/src/contexts/ThemeContext.jsx, frontend/src/components/ThemeSelector.jsx, frontend/src/utils/themeUtils.js, frontend/tailwind.config.js, or any component that hardcodes colors (which it must not).
---

# theme-daisyui — Theme System Conventions

The frontend supports three modes: **light**, **dark**, and **custom**. Every color in the UI routes through DaisyUI semantic tokens — no hardcoded hex values in component styles.

## Five color slots

Every theme defines exactly these 5 tokens:

- `primary`    — brand accent (buttons, links)
- `secondary`  — supporting accent
- `accent`     — highlights, badges
- `base-100`   — main background
- `base-200`   — subtle contrast background

DaisyUI derives the rest (content colors, focus states) automatically.

## Fixed palettes

Light theme: `#4A90D9` / `#6BA3BE` / `#F5A623` / `#FFFFFF` / `#F2F4F6`
Dark theme:  `#E2E8F0` / `#94A3B8` / `#F59E0B` / `#1E293B` / `#0F172A`

Both registered in `frontend/tailwind.config.js` under `daisyui.themes`.

## Custom theme

User picks a single primary color. The other 4 slots derive deterministically in `themeUtils.js`:

- `secondary`: primary HSL with saturation −20%, lightness +15%
- `accent`:    primary HSL with hue +30°
- `base-100`:  light-vs-dark decision by primary luminance (bright primary → dark base; dim primary → light base)
- `base-200`:  base-100 ± 4% lightness

Apply via inline CSS-var injection on `<html>`:

```js
document.documentElement.setAttribute('data-theme', 'custom')
document.documentElement.style.setProperty('--p', hslString)
// ... --s, --a, --b1, --b2
```

Invalid hex → fallback to `#6366F1` (indigo). Validate via `/^#[0-9A-Fa-f]{6}$/`.

## Persistence

- localStorage key: `sc_theme`
- Value: JSON `{mode: 'light' | 'dark' | 'custom', primaryColor: '#hex'}`
- Applied BEFORE first React render — do this in `index.html` inline script or top of `main.jsx` to avoid FOUC
- localStorage unavailable (private mode, quota) → silent fallback to in-memory state

## ThemeContext

- Exposes `{mode, primaryColor, setMode, setPrimaryColor}`
- `setMode('custom')` only applies primary-color CSS vars; switching back to `'light'`/`'dark'` MUST clear the inline vars (`removeProperty`)
- Wrap `<App>` in `<ThemeProvider>` in `main.jsx`

## ThemeSelector UI

- 3 mode buttons (Light / Dark / Custom) — labels through `t(...)` (see `i18n` skill)
- 5 color swatch previews (pure squares rendering the 5 slots) — swatch hex is hardcoded BECAUSE it's a preview of raw palette, NOT a theme-sensitive surface. This is the one allowed exception to "no hardcoded colors"
- Color picker only shown when `mode === 'custom'`
- Integrated into Navbar alongside language toggle

## Forbidden patterns

```jsx
// ❌ Hardcoded color in style or className
<div style={{backgroundColor: '#4A90D9'}}>
<div className="bg-[#4A90D9]">

// ❌ Conditional on mode to pick a color (defeats the theming system)
<div className={mode === 'dark' ? 'bg-gray-900' : 'bg-white'}>

// ✅ Use semantic tokens
<div className="bg-base-100 text-base-content">
<div className="bg-primary text-primary-content">
```

## Testing (Vitest)

- `themeUtils.js` (palette derivation, hex validation, HSL conversions) has unit tests
- Vitest configured in `frontend/vite.config.js` with jsdom
- TDD: write tests red → extract utils → green

## No OS dark-mode auto-detection (intentional)

The theme is explicit user choice. We do NOT observe `prefers-color-scheme` — always respect the stored mode.
