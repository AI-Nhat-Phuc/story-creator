# DaisyUI Components Guide
## Hướng Dẫn Sử Dụng Các Component của DaisyUI

*Tài liệu này tổng hợp 65 components có sẵn trong DaisyUI v4.6.0 với ví dụ sử dụng thực tế.*

---

## 📚 **Danh Sách Components**

### **🎛️ ACTIONS (Hành Động)**

#### **Button**
```html
<button class="btn">Button</button>
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-accent">Accent</button>
<button class="btn btn-ghost">Ghost</button>
<button class="btn btn-link">Link</button>

<!-- Sizes -->
<button class="btn btn-xs">Extra small</button>
<button class="btn btn-sm">Small</button>
<button class="btn btn-md">Normal</button>
<button class="btn btn-lg">Large</button>

<!-- States -->
<button class="btn btn-active">Active</button>
<button class="btn btn-disabled">Disabled</button>
<button class="btn loading">Loading</button>
```

#### **Dropdown**
```html
<div class="dropdown">
  <div tabindex="0" role="button" class="btn m-1">Click</div>
  <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
    <li><a>Item 1</a></li>
    <li><a>Item 2</a></li>
  </ul>
</div>
```

#### **Modal**
```html
<button class="btn" onclick="my_modal_1.showModal()">open modal</button>
<dialog id="my_modal_1" class="modal">
  <div class="modal-box">
    <h3 class="font-bold text-lg">Hello!</h3>
    <p class="py-4">Press ESC key or click the button below to close</p>
    <div class="modal-action">
      <form method="dialog">
        <button class="btn">Close</button>
      </form>
    </div>
  </div>
</dialog>
```

#### **Swap**
```html
<label class="swap">
  <input type="checkbox" />
  <div class="swap-on">ON</div>
  <div class="swap-off">OFF</div>
</label>
```

---

### **📊 DATA DISPLAY (Hiển Thị Dữ Liệu)**

#### **Accordion**
```html
<div class="collapse collapse-arrow bg-base-200">
  <input type="radio" name="my-accordion-2" checked="checked" />
  <div class="collapse-title text-xl font-medium">
    Click to open this one and close others
  </div>
  <div class="collapse-content">
    <p>hello</p>
  </div>
</div>
```

#### **Avatar**
```html
<div class="avatar">
  <div class="w-24 rounded-full">
    <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg" />
  </div>
</div>

<!-- Avatar Group -->
<div class="avatar-group -space-x-6 rtl:space-x-reverse">
  <div class="avatar">
    <div class="w-12">
      <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg" />
    </div>
  </div>
  <!-- More avatars -->
</div>
```

#### **Badge**
```html
<div class="badge">neutral</div>
<div class="badge badge-primary">primary</div>
<div class="badge badge-secondary">secondary</div>
<div class="badge badge-accent">accent</div>
<div class="badge badge-ghost">ghost</div>

<!-- Sizes -->
<div class="badge badge-lg">Large</div>
<div class="badge badge-md">Medium</div>
<div class="badge badge-sm">Small</div>
<div class="badge badge-xs">Tiny</div>
```

#### **Card**
```html
<div class="card w-96 bg-base-100 shadow-xl">
  <figure><img src="https://img.daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.jpg" alt="Shoes" /></figure>
  <div class="card-body">
    <h2 class="card-title">Shoes!</h2>
    <p>If a dog chews shoes whose shoes does he choose?</p>
    <div class="card-actions justify-end">
      <button class="btn btn-primary">Buy Now</button>
    </div>
  </div>
</div>
```

#### **Carousel**
```html
<div class="carousel w-full">
  <div id="slide1" class="carousel-item relative w-full">
    <img src="https://img.daisyui.com/images/stock/photo-1625726411847-8cbb60cc71e6.jpg" class="w-full" />
    <div class="absolute flex justify-between transform -translate-y-1/2 left-5 right-5 top-1/2">
      <a href="#slide4" class="btn btn-circle">❮</a>
      <a href="#slide2" class="btn btn-circle">❯</a>
    </div>
  </div>
</div>
```

#### **Chat Bubble**
```html
<div class="chat chat-start">
  <div class="chat-image avatar">
    <div class="w-10 rounded-full">
      <img alt="Avatar" src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg" />
    </div>
  </div>
  <div class="chat-header">
    Obi-Wan Kenobi
    <time class="text-xs opacity-50">12:45</time>
  </div>
  <div class="chat-bubble">You were the Chosen One!</div>
  <div class="chat-footer opacity-50">
    Delivered
  </div>
</div>
```

#### **Countdown**
```html
<span class="countdown font-mono text-6xl">
  <span style="--value:15;"></span>:
  <span style="--value:10;"></span>:
  <span style="--value:24;"></span>
</span>
```

#### **Stat**
```html
<div class="stats shadow">
  <div class="stat">
    <div class="stat-figure text-primary">
      <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
        <!-- SVG icon -->
      </svg>
    </div>
    <div class="stat-title">Total Page Views</div>
    <div class="stat-value">89,400</div>
    <div class="stat-desc">21% more than last month</div>
  </div>
</div>
```

#### **Table**
```html
<div class="overflow-x-auto">
  <table class="table">
    <thead>
      <tr>
        <th></th>
        <th>Name</th>
        <th>Job</th>
        <th>Favorite Color</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>1</th>
        <td>Cy Ganderton</td>
        <td>Quality Control Specialist</td>
        <td>Blue</td>
      </tr>
    </tbody>
  </table>
</div>
```

---

### **🎨 DATA INPUT (Nhập Liệu)**

#### **Checkbox**
```html
<div class="form-control">
  <label class="label cursor-pointer">
    <span class="label-text">Remember me</span>
    <input type="checkbox" checked="checked" class="checkbox" />
  </label>
</div>
```

#### **File Input**
```html
<input type="file" class="file-input file-input-bordered w-full max-w-xs" />
<input type="file" class="file-input file-input-bordered file-input-primary w-full max-w-xs" />
```

#### **Text Input**
```html
<input type="text" placeholder="Type here" class="input input-bordered w-full max-w-xs" />
<input type="text" placeholder="Type here" class="input input-bordered input-primary w-full max-w-xs" />

<!-- With Label -->
<label class="form-control w-full max-w-xs">
  <div class="label">
    <span class="label-text">What is your name?</span>
  </div>
  <input type="text" placeholder="Type here" class="input input-bordered w-full max-w-xs" />
</label>
```

#### **Radio**
```html
<div class="form-control">
  <label class="label cursor-pointer">
    <span class="label-text">Red pill</span>
    <input type="radio" name="radio-10" class="radio checked:bg-red-500" checked />
  </label>
</div>
```

#### **Range**
```html
<input type="range" min="0" max="100" value="40" class="range" />
<input type="range" min="0" max="100" value="25" class="range range-primary" />
```

#### **Rating**
```html
<div class="rating">
  <input type="radio" name="rating-2" class="mask mask-star-2 bg-orange-400" />
  <input type="radio" name="rating-2" class="mask mask-star-2 bg-orange-400" checked />
  <input type="radio" name="rating-2" class="mask mask-star-2 bg-orange-400" />
  <input type="radio" name="rating-2" class="mask mask-star-2 bg-orange-400" />
  <input type="radio" name="rating-2" class="mask mask-star-2 bg-orange-400" />
</div>
```

#### **Select**
```html
<select class="select select-bordered w-full max-w-xs">
  <option disabled selected>Who shot first?</option>
  <option>Han Solo</option>
  <option>Greedo</option>
</select>
```

#### **Textarea**
```html
<textarea class="textarea textarea-bordered" placeholder="Bio"></textarea>
<textarea class="textarea textarea-bordered textarea-primary" placeholder="Bio"></textarea>
```

#### **Toggle**
```html
<input type="checkbox" class="toggle" checked />
<input type="checkbox" class="toggle toggle-primary" checked />
<input type="checkbox" class="toggle toggle-secondary" checked />
```

---

### **🧭 LAYOUT (Bố Cục)**

#### **Breadcrumbs**
```html
<div class="text-sm breadcrumbs">
  <ul>
    <li><a>Home</a></li>
    <li><a>Documents</a></li>
    <li>Add Document</li>
  </ul>
</div>
```

#### **Divider**
```html
<div class="divider">OR</div>
<div class="divider divider-horizontal">OR</div>
```

#### **Drawer**
```html
<div class="drawer">
  <input id="my-drawer" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">
    <!-- Page content here -->
    <label for="my-drawer" class="btn btn-primary drawer-button">Open drawer</label>
  </div>
  <div class="drawer-side">
    <label for="my-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu p-4 w-80 min-h-full bg-base-200 text-base-content">
      <!-- Sidebar content here -->
      <li><a>Sidebar Item 1</a></li>
      <li><a>Sidebar Item 2</a></li>
    </ul>
  </div>
</div>
```

#### **Footer**
```html
<footer class="footer p-10 bg-neutral text-neutral-content">
  <nav>
    <h6 class="footer-title">Services</h6>
    <a class="link link-hover">Branding</a>
    <a class="link link-hover">Design</a>
    <a class="link link-hover">Marketing</a>
    <a class="link link-hover">Advertisement</a>
  </nav>
</footer>
```

#### **Hero**
```html
<div class="hero min-h-screen bg-base-200">
  <div class="hero-content text-center">
    <div class="max-w-md">
      <h1 class="text-5xl font-bold">Hello there</h1>
      <p class="py-6">Provident cupiditate voluptatem et in. Quaerat fugiat ut assumenda excepturi exercitationem quasi.</p>
      <button class="btn btn-primary">Get Started</button>
    </div>
  </div>
</div>
```

#### **Indicator**
```html
<div class="indicator">
  <span class="indicator-item badge badge-secondary">new</span>
  <div class="grid w-32 h-32 bg-base-300 place-items-center">content</div>
</div>
```

#### **Join**
```html
<div class="join">
  <button class="join-item btn">Button</button>
  <button class="join-item btn">Button</button>
  <button class="join-item btn">Button</button>
</div>
```

#### **Menu**
```html
<ul class="menu bg-base-200 w-56 rounded-box">
  <li><a>Item 1</a></li>
  <li>
    <details>
      <summary>Parent</summary>
      <ul>
        <li><a>Submenu 1</a></li>
        <li><a>Submenu 2</a></li>
      </ul>
    </details>
  </li>
  <li><a>Item 3</a></li>
</ul>
```

#### **Navbar**
```html
<div class="navbar bg-base-100">
  <div class="navbar-start">
    <div class="dropdown">
      <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
        <!-- Hamburger icon -->
      </div>
      <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
        <li><a>Item 1</a></li>
        <li><a>Item 3</a></li>
      </ul>
    </div>
    <a class="btn btn-ghost text-xl">daisyUI</a>
  </div>
  <div class="navbar-center hidden lg:flex">
    <ul class="menu menu-horizontal px-1">
      <li><a>Item 1</a></li>
      <li><a>Item 3</a></li>
    </ul>
  </div>
  <div class="navbar-end">
    <a class="btn">Button</a>
  </div>
</div>
```

#### **Steps**
```html
<ul class="steps">
  <li class="step step-primary">Register</li>
  <li class="step step-primary">Choose plan</li>
  <li class="step">Purchase</li>
  <li class="step">Receive Product</li>
</ul>
```

#### **Tabs**
```html
<div role="tablist" class="tabs tabs-bordered">
  <input type="radio" name="my_tabs_1" role="tab" class="tab" aria-label="Tab 1" checked />
  <div role="tabpanel" class="tab-content p-10">Tab content 1</div>

  <input type="radio" name="my_tabs_1" role="tab" class="tab" aria-label="Tab 2" />
  <div role="tabpanel" class="tab-content p-10">Tab content 2</div>

  <input type="radio" name="my_tabs_1" role="tab" class="tab" aria-label="Tab 3" />
  <div role="tabpanel" class="tab-content p-10">Tab content 3</div>
</div>
```

---

### **🔔 FEEDBACK (Phản Hồi)**

#### **Alert**
```html
<div class="alert">
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-info shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
  <span>New software update available.</span>
</div>

<div class="alert alert-success">
  <span>Your purchase has been confirmed!</span>
</div>

<div class="alert alert-warning">
  <span>Warning: Invalid email address!</span>
</div>

<div class="alert alert-error">
  <span>Error! Task failed successfully.</span>
</div>
```

#### **Loading**
```html
<span class="loading loading-spinner loading-xs"></span>
<span class="loading loading-spinner loading-sm"></span>
<span class="loading loading-spinner loading-md"></span>
<span class="loading loading-spinner loading-lg"></span>

<!-- Different types -->
<span class="loading loading-dots loading-lg"></span>
<span class="loading loading-ring loading-lg"></span>
<span class="loading loading-ball loading-lg"></span>
<span class="loading loading-bars loading-lg"></span>
<span class="loading loading-infinity loading-lg"></span>
```

#### **Progress**
```html
<progress class="progress w-56"></progress>
<progress class="progress progress-primary w-56" value="0" max="100"></progress>
<progress class="progress progress-primary w-56" value="10" max="100"></progress>
<progress class="progress progress-primary w-56" value="40" max="100"></progress>
```

#### **Radial Progress**
```html
<div class="radial-progress" style="--value:70;" role="progressbar">70%</div>
<div class="radial-progress text-primary" style="--value:70;" role="progressbar">70%</div>
<div class="radial-progress bg-primary text-primary-content border-4 border-primary" style="--value:70;" role="progressbar">70%</div>
```

#### **Skeleton**
```html
<div class="flex flex-col gap-4 w-52">
  <div class="skeleton h-32 w-full"></div>
  <div class="skeleton h-4 w-28"></div>
  <div class="skeleton h-4 w-full"></div>
  <div class="skeleton h-4 w-full"></div>
</div>
```

#### **Toast**
```html
<div class="toast">
  <div class="alert alert-info">
    <span>New mail arrived.</span>
  </div>
  <div class="alert alert-success">
    <span>Message sent successfully.</span>
  </div>
</div>
```

#### **Tooltip**
```html
<div class="tooltip" data-tip="hello">
  <button class="btn">Hover me</button>
</div>

<div class="tooltip tooltip-open tooltip-top" data-tip="hello">
  <button class="btn">Force open</button>
</div>
```

---

### **🎭 MOCKUP (Mô Phỏng)**

#### **Browser Mockup**
```html
<div class="mockup-browser border bg-base-300">
  <div class="mockup-browser-toolbar">
    <div class="input">https://daisyui.com</div>
  </div>
  <div class="flex justify-center px-4 py-16 bg-base-200">Hello!</div>
</div>
```

#### **Code Mockup**
```html
<div class="mockup-code">
  <pre data-prefix="$"><code>npm i daisyui</code></pre>
  <pre data-prefix=">" class="text-warning"><code>installing...</code></pre>
  <pre data-prefix=">" class="text-success"><code>Done!</code></pre>
</div>
```

#### **Phone Mockup**
```html
<div class="mockup-phone">
  <div class="camera"></div>
  <div class="display">
    <div class="artboard artboard-demo phone-1">Hi.</div>
  </div>
</div>
```

#### **Window Mockup**
```html
<div class="mockup-window border bg-base-300">
  <div class="flex justify-center px-4 py-16 bg-base-200">Hello!</div>
</div>
```

---

## 🎨 **Themes và Customization**

### **Theme Controller**
```html
<!-- Theme switcher with checkbox -->
<input type="checkbox" value="synthwave" class="toggle theme-controller"/>

<!-- Theme switcher with radio buttons -->
<input type="radio" name="theme-buttons" class="btn theme-controller" aria-label="Default" value="default"/>
<input type="radio" name="theme-buttons" class="btn theme-controller" aria-label="Retro" value="retro"/>
<input type="radio" name="theme-buttons" class="btn theme-controller" aria-label="Cyberpunk" value="cyberpunk"/>
```

### **Available Themes**
```javascript
// Top themes in DaisyUI
const themes = [
  'light', 'dark', 'cupcake', 'bumblebee', 'emerald',
  'corporate', 'synthwave', 'retro', 'cyberpunk',
  'valentine', 'halloween', 'garden', 'forest',
  'aqua', 'lofi', 'pastel', 'fantasy', 'wireframe',
  'black', 'luxury', 'dracula', 'cmyk', 'autumn',
  'business', 'acid', 'lemonade', 'night', 'coffee',
  'winter', 'dim', 'nord', 'sunset'
];
```

---

## 🔧 **Best Practices**

### **1. Responsive Design**
```html
<!-- Mobile-first responsive classes -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="card bg-base-100 shadow-xl">...</div>
</div>

<!-- Responsive navbar -->
<div class="navbar bg-base-100">
  <div class="navbar-start">
    <div class="dropdown lg:hidden">...</div>
  </div>
  <div class="navbar-center hidden lg:flex">...</div>
</div>
```

### **2. Form Validation**
```html
<div class="form-control w-full max-w-xs">
  <label class="label">
    <span class="label-text">Email</span>
  </label>
  <input type="email" placeholder="your@email.com" class="input input-bordered input-error w-full max-w-xs" />
  <label class="label">
    <span class="label-text-alt text-error">Invalid email format</span>
  </label>
</div>
```

### **3. Loading States**
```html
<!-- Button loading state -->
<button class="btn btn-primary" onclick="this.classList.add('loading')">
  <span class="loading loading-spinner"></span>
  Loading...
</button>

<!-- Card skeleton -->
<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <div class="skeleton h-4 w-3/4 mb-4"></div>
    <div class="skeleton h-4 w-1/2"></div>
  </div>
</div>
```

### **4. Accessibility**
```html
<!-- Proper ARIA labels -->
<button class="btn" aria-label="Close modal" onclick="modal.close()">✕</button>

<!-- Screen reader friendly -->
<div class="alert alert-error" role="alert" aria-live="assertive">
  <span>Error occurred!</span>
</div>

<!-- Keyboard navigation -->
<div class="dropdown">
  <div tabindex="0" role="button" class="btn">Menu</div>
  <ul tabindex="0" class="dropdown-content menu">...</ul>
</div>
```

---

## 💡 **Integration Tips**

### **1. Với React/Vue/Angular**
```javascript
// Example với React
import React from 'react';

const DaisyButton = ({ children, variant = 'primary', size = 'md' }) => (
  <button className={`btn btn-${variant} btn-${size}`}>
    {children}
  </button>
);

export default DaisyButton;
```

### **2. JavaScript Integration**
```javascript
// Modal control
function openModal(modalId) {
  document.getElementById(modalId).showModal();
}

function closeModal(modalId) {
  document.getElementById(modalId).close();
}

// Toast notifications
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `alert alert-${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  document.getElementById('toast-container').appendChild(toast);

  setTimeout(() => toast.remove(), 3000);
}

// Theme switching
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}
```

### **3. CSS Customization**
```css
/* Custom component variations */
.btn-gradient {
  @apply btn;
  background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
}

.btn-gradient:hover {
  background: linear-gradient(45deg, #5a6fd8 0%, #6a4190 100%);
}

/* Custom theme colors */
:root {
  --p: 259 94% 51%;  /* Primary */
  --s: 314 100% 47%; /* Secondary */
  --a: 174 60% 51%;  /* Accent */
}
```

---

## 📱 **Common Patterns**

### **Admin Dashboard Layout**
```html
<div class="drawer lg:drawer-open">
  <input id="drawer-toggle" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">
    <!-- Navbar -->
    <div class="navbar bg-base-100">...</div>
    <!-- Main content -->
    <div class="p-6">...</div>
  </div>
  <div class="drawer-side">
    <aside class="min-h-full w-64 bg-base-100">
      <ul class="menu">...</ul>
    </aside>
  </div>
</div>
```

### **Form Layout**
```html
<div class="card bg-base-100 shadow-xl max-w-lg mx-auto">
  <div class="card-body">
    <h2 class="card-title">Login</h2>
    <div class="form-control">
      <label class="label">
        <span class="label-text">Email</span>
      </label>
      <input type="email" class="input input-bordered" required />
    </div>
    <div class="form-control">
      <label class="label">
        <span class="label-text">Password</span>
      </label>
      <input type="password" class="input input-bordered" required />
    </div>
    <div class="form-control mt-6">
      <button class="btn btn-primary">Login</button>
    </div>
  </div>
</div>
```

---

**🚀 Happy Coding với DaisyUI!**

*Tài liệu này được cập nhật cho DaisyUI v4.6.0. Để biết thêm chi tiết và ví dụ mới nhất, vui lòng tham khảo [daisyui.com](https://daisyui.com)*
