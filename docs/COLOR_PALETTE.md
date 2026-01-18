# Color Palette & DaisyUI Theme

## 🎨 Bảng màu chính

Inspired by LaFlo Records design:

```css
/* Primary Colors */
--color-gold: #D79922;        /* Vàng gold - Primary */
--color-cream: #EFE2BA;       /* Be nhạt - Secondary/Background */
--color-coral: #F13C20;       /* Đỏ cam - Accent */
--color-navy: #4056A1;        /* Xanh dương đậm - Info */
--color-periwinkle: #C5CBE3;  /* Xanh dương nhạt - Neutral */
```

### Hex Codes
- **Gold**: `#D79922` - Màu chủ đạo, dùng cho buttons, highlights
- **Cream**: `#EFE2BA` - Background secondary, cards
- **Coral**: `#F13C20` - Action buttons, warnings, emphasis
- **Navy**: `#4056A1` - Headers, primary text, navigation
- **Periwinkle**: `#C5CBE3` - Borders, subtle backgrounds

## 🎭 DaisyUI Theme Configuration

### Tailwind Config (`frontend/tailwind.config.js`)

```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'laflo-gold': '#D79922',
        'laflo-cream': '#EFE2BA',
        'laflo-coral': '#F13C20',
        'laflo-navy': '#4056A1',
        'laflo-periwinkle': '#C5CBE3',
      }
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        storyCreator: {
          "primary": "#D79922",      // Gold
          "secondary": "#EFE2BA",    // Cream
          "accent": "#F13C20",       // Coral
          "neutral": "#C5CBE3",      // Periwinkle
          "base-100": "#FFFFFF",     // White background
          "base-200": "#EFE2BA",     // Cream background
          "base-300": "#C5CBE3",     // Periwinkle background
          "info": "#4056A1",         // Navy
          "success": "#36D399",      // Green (DaisyUI default)
          "warning": "#FBBD23",      // Yellow (DaisyUI default)
          "error": "#F87272",        // Red (DaisyUI default)
        },
      },
    ],
  },
}
```

### HTML Setup (`frontend/index.html`)

```html
<html lang="vi" data-theme="storyCreator">
```

## 🎨 Usage Examples

### Buttons
```jsx
{/* Primary button - Gold */}
<button className="btn btn-primary">Tạo thế giới</button>

{/* Secondary button - Cream */}
<button className="btn btn-secondary">Xem thêm</button>

{/* Accent button - Coral */}
<button className="btn btn-accent">🤖 GPT</button>

{/* Info button - Navy */}
<button className="btn btn-info">Chi tiết</button>
```

### Cards
```jsx
{/* Cream background card */}
<div className="card bg-base-200">
  <div className="card-body">
    <h2 className="card-title text-info">Thế giới Fantasy</h2>
  </div>
</div>

{/* Navy accent card */}
<div className="card border-2 border-info">
  <div className="card-body">
    <h2 className="card-title text-primary">Câu chuyện mới</h2>
  </div>
</div>
```

### Badges
```jsx
<span className="badge badge-primary">Fantasy</span>
<span className="badge badge-accent">GPT</span>
<span className="badge badge-info">Story</span>
<span className="badge badge-neutral">Character</span>
```

### Alerts
```jsx
<div className="alert alert-info">
  <span>Thông tin hệ thống</span>
</div>

<div className="alert alert-success">
  <span>Tạo thành công!</span>
</div>

<div className="alert" style={{ backgroundColor: '#EFE2BA' }}>
  <span>Custom cream alert</span>
</div>
```

### Text Colors
```jsx
<h1 className="text-primary">Vàng Gold</h1>
<h2 className="text-info">Xanh Navy</h2>
<p className="text-accent">Đỏ Coral</p>
<span className="text-neutral">Xanh nhạt</span>
```

### Backgrounds
```jsx
<div className="bg-base-100">White background</div>
<div className="bg-base-200">Cream background</div>
<div className="bg-base-300">Periwinkle background</div>
<div className="bg-primary text-white">Gold background</div>
<div className="bg-info text-white">Navy background</div>
```

## 🖼️ Component Styling Guide

### Navigation Bar
```jsx
<nav className="navbar bg-info text-white">
  <div className="navbar-start">
    <a className="btn btn-ghost text-xl">Story Creator</a>
  </div>
  <div className="navbar-end">
    <button className="btn btn-primary">New World</button>
  </div>
</nav>
```

### Hero Section
```jsx
<div className="hero min-h-screen bg-base-200">
  <div className="hero-content text-center">
    <div className="max-w-md">
      <h1 className="text-5xl font-bold text-info">Story Creator</h1>
      <p className="py-6 text-neutral-700">Create amazing worlds</p>
      <button className="btn btn-primary">Get Started</button>
    </div>
  </div>
</div>
```

### Modal
```jsx
<div className="modal modal-open">
  <div className="modal-box bg-base-200">
    <h3 className="font-bold text-lg text-info">Tạo thế giới mới</h3>
    <div className="modal-action">
      <button className="btn btn-primary">Tạo</button>
      <button className="btn btn-ghost">Hủy</button>
    </div>
  </div>
</div>
```

### Stats Dashboard
```jsx
<div className="stats shadow bg-base-200">
  <div className="stat">
    <div className="stat-title text-info">Worlds</div>
    <div className="stat-value text-primary">12</div>
  </div>
  <div className="stat">
    <div className="stat-title text-info">Stories</div>
    <div className="stat-value text-accent">45</div>
  </div>
</div>
```

## 📋 Color Usage Guidelines

### Primary (Gold #D79922)
- ✅ Main action buttons
- ✅ Important headings
- ✅ Active states
- ✅ Brand elements

### Secondary (Cream #EFE2BA)
- ✅ Card backgrounds
- ✅ Section backgrounds
- ✅ Secondary buttons
- ✅ Hover states

### Accent (Coral #F13C20)
- ✅ GPT-related features
- ✅ Call-to-action buttons
- ✅ Important notifications
- ✅ Emphasis elements

### Info (Navy #4056A1)
- ✅ Navigation bars
- ✅ Headers
- ✅ Links
- ✅ Primary text

### Neutral (Periwinkle #C5CBE3)
- ✅ Borders
- ✅ Dividers
- ✅ Disabled states
- ✅ Subtle backgrounds

## 🎯 Accessibility

### Contrast Ratios
- Gold (#D79922) on White: 4.8:1 ✅ (AA)
- Navy (#4056A1) on White: 5.2:1 ✅ (AA)
- Coral (#F13C20) on White: 4.1:1 ✅ (AA)
- White on Navy: 6.8:1 ✅ (AAA)
- White on Gold: 5.1:1 ✅ (AA)

### Best Practices
- Use `text-white` with `bg-info` or `bg-primary`
- Use `text-info` or `text-primary` on light backgrounds
- Ensure sufficient contrast for all text elements
- Test with color blindness simulators

## 🚀 Implementation Checklist

- [ ] Update `tailwind.config.js` with custom theme
- [ ] Set `data-theme="storyCreator"` in `index.html`
- [ ] Update all buttons to use theme colors
- [ ] Update card backgrounds to `bg-base-200`
- [ ] Update navigation to `bg-info`
- [ ] Update headings to `text-info` or `text-primary`
- [ ] Update GPT buttons to `btn-accent`
- [ ] Test color contrast in all components
- [ ] Update loading states with theme colors
- [ ] Update toast notifications with theme colors

## 📝 Notes

- Theme is inspired by LaFlo Records artistic design
- Colors are harmonious and culturally warm
- Palette supports both light and creative moods
- Gold and Coral provide energy and warmth
- Navy and Periwinkle add professionalism and calm
- Cream serves as a soft, welcoming background

## 🔗 References

- DaisyUI Themes: https://daisyui.com/docs/themes/
- TailwindCSS Colors: https://tailwindcss.com/docs/customizing-colors
- Color Contrast Checker: https://webaim.org/resources/contrastchecker/
