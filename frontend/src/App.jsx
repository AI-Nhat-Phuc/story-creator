import React, { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import WorldsPage from './pages/WorldsPage'
import StoriesPage from './pages/StoriesPage'
import WorldDetailPage from './pages/WorldDetailPage'
import StoryDetailPage from './pages/StoryDetailPage'
import Toast from './components/Toast'

function App() {
  const [toast, setToast] = useState(null)

  const showToast = (message, type = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  return (
    <>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard showToast={showToast} />} />
          <Route path="/worlds" element={<WorldsPage showToast={showToast} />} />
          <Route path="/worlds/:worldId" element={<WorldDetailPage showToast={showToast} />} />
          <Route path="/stories" element={<StoriesPage showToast={showToast} />} />
          <Route path="/stories/:storyId" element={<StoryDetailPage showToast={showToast} />} />
        </Route>
      </Routes>
      {toast && <Toast message={toast.message} type={toast.type} />}
    </>
  )
}

export default App
