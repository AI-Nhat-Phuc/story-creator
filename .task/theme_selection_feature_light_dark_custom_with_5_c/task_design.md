# DESIGN — Theme Selection Feature (light/dark/custom with 5 colors)

> **Status**: DRAFT
> **Phase**: DESIGN
> **Date**: 2026-03-22

---

## Changed Files

| File | Change Type | Maps to Spec Clause |
|------|-------------|---------------------|
| `frontend/tailwind.config.js` | MODIFY | B-3, B-4, B-8 |
| `frontend/src/contexts/ThemeContext.jsx` | NEW | B-1, B-2, B-5, B-7, B-8, EC-1–4 |
| `frontend/src/components/ThemeSelector.jsx` | NEW | B-6 |
| `frontend/src/components/Navbar.jsx` | MODIFY | B-6, BR-5 |
| `frontend/src/App.jsx` | MODIFY | B-7, B-8 |

---

## tailwind.config.js — New Theme Definitions

Add two named DaisyUI themes alongside the existing `storyCreator` theme:

```js
// sc-light (maps to B-3)
"sc-light": {
  "primary":   "#4A90D9",
  "secondary": "#6BA3BE",
  "accent":    "#F5A623",
  "base-100":  "#FFFFFF",
  "base-200":  "#F2F4F6",
}

// sc-dark (maps to B-4)
"sc-dark": {
  "primary":   "#E2E8F0",
  "secondary": "#94A3B8",
  "accent":    "#F59E0B",
  "base-100":  "#1E293B",
  "base-200":  "#0F172A",
}
```

No other DaisyUI color slots (`success`, `error`, `warning`, `info`, `neutral`) are set — they inherit DaisyUI defaults. Maps to BR-1.

---

## ThemeContext.jsx — Interface Contract

### Shape of state

```js
{
  mode: "light" | "dark" | "custom",   // B-1
  primaryColor: "#rrggbb",             // B-5, BR-2
  colors: {                            // computed 5-color palette
    primary:   "#rrggbb",
    secondary: "#rrggbb",
    accent:    "#rrggbb",
    base100:   "#rrggbb",
    base200:   "#rrggbb",
  }
}
```

### Exported from context

```js
// Hook
useTheme() => { mode, primaryColor, colors, setMode, setPrimaryColor }

// Provider
<ThemeProvider>...</ThemeProvider>
```

### localStorage schema (B-7)

```json
{ "mode": "light" | "dark" | "custom", "primaryColor": "#rrggbb" }
```

Key: `"sc_theme"`

### Custom palette algorithm — function signature (B-5)

```js
// Pure function, no side effects
function deriveCustomPalette(primaryHex: string): {
  primary:   string,  // = primaryHex
  secondary: string,  // hue same, sat-20, light+15
  accent:    string,  // hue+30, same sat+light
  base100:   string,  // #FFFFFF or #1E293B
  base200:   string,  // hue same, sat 20%, light 95% or 10%
}
```

### applyTheme side effect (B-8)

```js
function applyTheme(mode, palette):
  if mode == "light"  → html[data-theme="sc-light"], clear inline vars
  if mode == "dark"   → html[data-theme="sc-dark"],  clear inline vars
  if mode == "custom" → html[data-theme="sc-light"], inject --p --s --a --b1 --b2 as oklch/hsl
```

---

## ThemeSelector.jsx — Interface Contract

```jsx
// Props: none — reads from useTheme()
function ThemeSelector(): JSX.Element

// Renders:
// - 3 mode buttons (light / dark / custom)
// - 5 color swatch circles (from context.colors)
// - <input type="color"> shown only when mode === "custom"
```

---

## Navbar.jsx — Modification

- Desktop: add `<ThemeSelector />` inside the `hidden md:flex` div, before the user menu.
- Mobile: add `<ThemeSelector />` inside the mobile dropdown `<ul>`, after the `<div className="divider">`.

No other Navbar logic changes.

---

## App.jsx — Modification

Wrap the existing provider tree with `<ThemeProvider>`:

```jsx
// Before
<GoogleOAuthProvider>
  <AuthProvider>
    ...
  </AuthProvider>
</GoogleOAuthProvider>

// After
<ThemeProvider>          {/* NEW — outermost, applies theme before paint */}
  <GoogleOAuthProvider>
    <AuthProvider>
      ...
    </AuthProvider>
  </GoogleOAuthProvider>
</ThemeProvider>
```

`ThemeProvider` reads `localStorage` and calls `applyTheme` synchronously in its constructor/init effect so no flash occurs on load (B-7).
