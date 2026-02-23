---
name: color
description: Color palette, DaisyUI theme configuration, and styling guidelines for the Story Creator app. Use when working with colors, themes, buttons, cards, badges, or any UI styling decisions.
---

# Skill: Color Palette & DaisyUI Theme

## Main Color Palette (LaFlo Records inspired)

| Name | Hex | DaisyUI Class | Used for |
|------|-----|---------------|----------|
| **Gold** | `#D79922` | `primary` | Main action buttons, highlights, brand |
| **Cream** | `#EFE2BA` | `secondary`, `base-200` | Card backgrounds, section backgrounds |
| **Coral** | `#F13C20` | `accent` | GPT features, call-to-action, emphasis |
| **Navy** | `#4056A1` | `info` | Navigation, headers, links, primary text |
| **Periwinkle** | `#C5CBE3` | `neutral`, `base-300` | Borders, dividers, subtle backgrounds |

## Custom Tailwind Colors

```jsx
// Use when you need colors outside DaisyUI semantic classes
className="text-laflo-gold"
className="bg-laflo-cream"
className="border-laflo-navy"
```

## Component Styling Cheat Sheet

```jsx
// Buttons
<button className="btn btn-primary">Gold action</button>
<button className="btn btn-accent">GPT/Coral action</button>
<button className="btn btn-info">Navy info</button>
<button className="btn btn-ghost">Ghost</button>

// Cards
<div className="card bg-base-200">Cream background</div>
<div className="card border-2 border-info">Navy border</div>

// Badges
<span className="badge badge-primary">Fantasy</span>
<span className="badge badge-accent">GPT</span>
<span className="badge badge-info">Story</span>

// Text
<h1 className="text-primary">Gold heading</h1>
<h2 className="text-info">Navy heading</h2>
<p className="text-accent">Coral emphasis</p>

// Backgrounds
<div className="bg-base-100">White</div>
<div className="bg-base-200">Cream</div>
<div className="bg-base-300">Periwinkle</div>
<div className="bg-primary text-white">Gold</div>
<div className="bg-info text-white">Navy</div>

// Navigation
<nav className="navbar bg-info text-white">...</nav>
```

## Theme Setup

```html
<!-- frontend/index.html -->
<html lang="vi" data-theme="storyCreator">
```

Theme defined in `frontend/tailwind.config.js` under `daisyui.themes`.

## Accessibility

- Gold on White: 4.8:1 (AA)
- Navy on White: 5.2:1 (AA)
- White on Navy: 6.8:1 (AAA)
- Always use `text-white` with `bg-info` or `bg-primary`

## Anti-patterns

- ❌ Hardcode hex colors in className → use DaisyUI semantic classes
- ❌ Inline `style={{ color: '...' }}` → use Tailwind classes
- ❌ Forget `text-white` on dark backgrounds (primary, info, accent)

Full details: see `docs/COLOR_PALETTE.md`
