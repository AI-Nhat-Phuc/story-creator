---
name: frontend-react
description: React frontend development patterns for Container/View architecture, Heroicons, DaisyUI styling, GPT polling, and code-splitting. Use when creating or editing components, containers, or pages in frontend/src/.
---

# Skill: React Frontend Development

## When to Apply
When creating or editing components, containers, or pages in `frontend/src/`.

## Architecture: Container → View Pattern

```
pages/           → Route components (receive showToast prop)
containers/      → Data fetching + state + handlers
components/      → Presentation UI (props only, no API calls)
services/api.js  → All HTTP calls (do NOT use fetch/axios directly in components)
```

### Pattern: Creating a New Feature

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
      showToast('Failed to load data', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id, name) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return
    try {
      await myAPI.delete(id)
      setData(prev => prev.filter(item => item.id !== id))
      showToast(`Deleted "${name}"`, 'success')
    } catch (error) {
      showToast('Error: ' + (error.response?.data?.error || error.message), 'error')
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
              <TrashIcon className="inline w-4 h-4" /> Delete
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
// Inside <Routes>:
<Route path="/my-feature" element={<MyFeaturePage showToast={showToast} />} />
```

## Icons: Heroicons (REQUIRED)

All icons must use `@heroicons/react`. Do NOT use emoji or text icons.

```jsx
// ✅ CORRECT
import { TrashIcon, PencilIcon, PlusIcon } from '@heroicons/react/24/outline'
<TrashIcon className="inline w-4 h-4" />

// ❌ WRONG
<span>🗑️</span>
<span>✏️</span>
```

Commonly used icons:
| Action | Icon |
|--------|------|
| Delete | `TrashIcon` |
| Edit | `PencilIcon` |
| Add | `PlusIcon` |
| Save | `ArrowDownTrayIcon` (solid) |
| Cancel | `XMarkIcon` |
| Search | `MagnifyingGlassIcon` |
| Link | `LinkIcon` |
| User | `UserIcon` |
| Location | `MapPinIcon` |
| Story | `BookOpenIcon` |
| Clock | `ClockIcon` |
| Check | `CheckCircleIcon` |
| Warning | `ExclamationTriangleIcon` |

**Note:** `<option>` HTML elements do NOT support JSX children → use plain text.

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

// Toast (via showToast prop)
showToast('Success!', 'success')  // success | error | info | warning

// Modal (use Modal.jsx component)
<Modal open={showModal} onClose={() => setShowModal(false)} title="Title">
  <p>Modal content</p>
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
        showToast('Analysis complete!', 'success')
      } else if (result.data.status === 'error') {
        showToast(result.data.result, 'error')
        setAnalyzing(false)
      } else {
        setTimeout(pollResults, 1000) // Poll every 1 second
      }
    }
    pollResults()
  } catch (error) {
    showToast('GPT error', 'error')
    setAnalyzing(false)
  }
}
```

## Code-Splitting

### Route-level Lazy Loading
All page components must be lazy-loaded in `App.jsx`:
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

## Anti-patterns

- ❌ Direct API calls in component → use `services/api.js`
- ❌ Business logic in view component → move to container
- ❌ Inline styles (except dynamic layout/animation) → use Tailwind classes
- ❌ Emoji/text icons → use Heroicons
- ❌ Eager import page components → use `React.lazy()`
- ❌ Complex state management → use React hooks + Context
- ❌ `fetch()` or `axios` directly → use the pre-configured api instance

