---
name: frontend-react
description: React frontend development patterns for Container/View architecture, Heroicons, DaisyUI styling, GPT polling, and code-splitting. Use when creating or editing components, containers, or pages in frontend/src/.
---

# Skill: React Frontend Development

## Khi nào áp dụng
Khi tạo hoặc chỉnh sửa components, containers, hoặc pages trong `frontend/src/`.

## Architecture: Container → View Pattern

```
pages/           → Route components (nhận showToast prop)
containers/      → Data fetching + state + handlers
components/      → Presentation UI (props only, no API calls)
services/api.js  → Tất cả HTTP calls (KHÔNG fetch/axios trực tiếp trong component)
```

### Pattern: Tạo Feature Mới

#### 1. API Client (`services/api.js`)
```javascript
export const myAPI = {
  getAll: () => api.get('/my-resource'),
  create: (data) => api.post('/my-resource', data),
  delete: (id) => api.delete(`/my-resource/${id}`),
}
```

#### 2. Container (data + logic)
```jsx
// containers/MyFeatureContainer.jsx
import React, { useState, useEffect } from 'react'
import { myAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import MyFeatureView from '../components/myFeature/MyFeatureView'

function MyFeatureContainer({ showToast }) {
  const { user } = useAuth()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const res = await myAPI.getAll()
      setData(res.data)
    } catch (error) {
      showToast('Lỗi tải dữ liệu', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id, name) => {
    if (!confirm(`Bạn có chắc muốn xóa "${name}"?`)) return
    try {
      await myAPI.delete(id)
      setData(prev => prev.filter(item => item.id !== id))
      showToast(`Đã xóa "${name}"`, 'success')
    } catch (error) {
      showToast('Lỗi: ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  if (loading) return <LoadingSpinner />

  return <MyFeatureView data={data} user={user} onDelete={handleDelete} />
}

export default MyFeatureContainer
```

#### 3. View Component (UI only)
```jsx
// components/myFeature/MyFeatureView.jsx
import { TrashIcon, PencilIcon } from '@heroicons/react/24/outline'

function MyFeatureView({ data, user, onDelete }) {
  return (
    <div className="gap-4 grid grid-cols-1 md:grid-cols-2">
      {data.map(item => (
        <div key={item.id} className="bg-base-100 shadow card">
          <div className="card-body">
            <h3 className="card-title">{item.name}</h3>
            <button
              onClick={() => onDelete(item.id, item.name)}
              className="btn btn-ghost btn-sm text-error"
            >
              <TrashIcon className="inline w-4 h-4" /> Xóa
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

export default MyFeatureView
```

#### 4. Page Component
```jsx
// pages/MyFeaturePage.jsx
import MyFeatureContainer from '../containers/MyFeatureContainer'
export default function MyFeaturePage({ showToast }) {
  return <MyFeatureContainer showToast={showToast} />
}
```

#### 5. Route (App.jsx — lazy loaded)
```jsx
const MyFeaturePage = lazy(() => import('./pages/MyFeaturePage'))
// Trong <Routes>:
<Route path="/my-feature" element={<MyFeaturePage showToast={showToast} />} />
```

## Icons: Heroicons (BẮT BUỘC)

Tất cả icon phải dùng `@heroicons/react`. KHÔNG dùng emoji hoặc text icon.

```jsx
// ✅ ĐÚNG
import { TrashIcon, PencilIcon, PlusIcon } from '@heroicons/react/24/outline'
<TrashIcon className="inline w-4 h-4" />

// ❌ SAI
<span>🗑️</span>
<span>✏️</span>
```

Các icon thường dùng:
| Action | Icon |
|--------|------|
| Xóa | `TrashIcon` |
| Sửa | `PencilIcon` |
| Thêm | `PlusIcon` |
| Lưu | `ArrowDownTrayIcon` (solid) |
| Hủy | `XMarkIcon` |
| Tìm kiếm | `MagnifyingGlassIcon` |
| Link | `LinkIcon` |
| User | `UserIcon` |
| Location | `MapPinIcon` |
| Story | `BookOpenIcon` |
| Clock | `ClockIcon` |
| Check | `CheckCircleIcon` |
| Warning | `ExclamationTriangleIcon` |

**Lưu ý:** `<option>` HTML elements KHÔNG hỗ trợ JSX children → dùng text thuần.

## Styling: TailwindCSS + DaisyUI

```jsx
// Buttons
<button className="btn btn-primary btn-sm">Primary</button>
<button className="btn btn-ghost btn-sm">Ghost</button>
<button className="btn btn-error btn-sm">Danger</button>
<button className="btn btn-sm loading">Loading</button>

// Cards
<div className="bg-base-100 shadow card">
  <div className="card-body">...</div>
</div>

// Badges
<span className="badge badge-primary">tag</span>
<span className="badge badge-sm badge-outline">small</span>

// Toast (qua showToast prop)
showToast('Thành công!', 'success')  // success | error | info | warning

// Modal (dùng component Modal.jsx)
<Modal open={showModal} onClose={() => setShowModal(false)} title="Tiêu đề">
  <p>Nội dung modal</p>
</Modal>
```

## GPT Integration Pattern (Frontend)

```jsx
const handleGptAnalyze = async () => {
  try {
    setAnalyzing(true)
    const response = await gptAPI.analyze({ story_description: '...' })
    const taskId = response.data.task_id

    const pollResults = async () => {
      const result = await gptAPI.getResults(taskId)
      if (result.data.status === 'completed') {
        setResult(result.data.result)
        setAnalyzing(false)
        showToast('Phân tích hoàn tất!', 'success')
      } else if (result.data.status === 'error') {
        showToast(result.data.result, 'error')
        setAnalyzing(false)
      } else {
        setTimeout(pollResults, 1000) // Poll mỗi 1 giây
      }
    }
    pollResults()
  } catch (error) {
    showToast('Lỗi GPT', 'error')
    setAnalyzing(false)
  }
}
```

## Code-Splitting

### Route-level Lazy Loading
Tất cả page components phải được lazy load trong `App.jsx`:
```jsx
const MyPage = lazy(() => import('./pages/MyPage'))
```

### Vendor Chunks (`vite.config.js`)
```javascript
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'vendor-react': ['react', 'react-dom', 'react-router-dom'],
        'vendor-xyflow': ['@xyflow/react'],
        'vendor-ui': ['@heroicons/react', 'axios'],
      },
    },
  },
}
```

## Anti-patterns (TRÁNH)

- ❌ API calls trực tiếp trong component → dùng `services/api.js`
- ❌ Business logic trong view component → chuyển vào container
- ❌ Inline styles (trừ dynamic layout/animation) → dùng Tailwind classes
- ❌ Emoji/text icons → dùng Heroicons
- ❌ Eager import page components → dùng `React.lazy()`
- ❌ State management phức tạp → dùng React hooks + Context
- ❌ `fetch()` hoặc `axios` trực tiếp → dùng api instance đã config sẵn
