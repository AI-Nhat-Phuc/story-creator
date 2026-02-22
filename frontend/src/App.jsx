import React, { useState, lazy, Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { AuthProvider } from './contexts/AuthContext'
import MainLayout from './layouts/MainLayout'
import Toast from './components/Toast'
import LoadingSpinner from './components/LoadingSpinner'

// Lazy-loaded route pages for code-splitting
const Dashboard = lazy(() => import('./pages/Dashboard'))
const WorldsPage = lazy(() => import('./pages/WorldsPage'))
const StoriesPage = lazy(() => import('./pages/StoriesPage'))
const WorldDetailPage = lazy(() => import('./pages/WorldDetailPage'))
const StoryDetailPage = lazy(() => import('./pages/StoryDetailPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const AdminPanel = lazy(() => import('./pages/AdminPanel'))

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

function App() {
  const [toast, setToast] = useState(null)

  const showToast = (message, type = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthProvider>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route element={<MainLayout />}>
              <Route path="/" element={<Dashboard showToast={showToast} />} />
              <Route path="/worlds" element={<WorldsPage showToast={showToast} />} />
              <Route path="/worlds/:worldId" element={<WorldDetailPage showToast={showToast} />} />
              <Route path="/stories" element={<StoriesPage showToast={showToast} />} />
              <Route path="/stories/:storyId" element={<StoryDetailPage showToast={showToast} />} />
              <Route path="/admin" element={<AdminPanel showToast={showToast} />} />
            </Route>
          </Routes>
        </Suspense>
        {toast && <Toast message={toast.message} type={toast.type} />}
      </AuthProvider>
    </GoogleOAuthProvider>
  )
}

export default App
