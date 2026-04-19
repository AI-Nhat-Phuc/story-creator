'use client'

import { HelmetProvider } from 'react-helmet-async'
import dynamic from 'next/dynamic'
import { ThemeProvider } from '../src/contexts/ThemeContext'
import { AuthProvider } from '../src/contexts/AuthContext'
import { GptTaskProvider } from '../src/contexts/GptTaskContext'
import { ToastProvider, useToast } from '../src/contexts/ToastContext'
import Toast from '../src/components/Toast'
import { useKeepAlive } from '../src/hooks/useKeepAlive'
import '../src/i18n'

// Google OAuth SDK touches `window` at import time — defer to client only.
const GoogleOAuthProvider = dynamic(
  () => import('@react-oauth/google').then((m) => m.GoogleOAuthProvider),
  { ssr: false }
)

function ToastOutlet() {
  const { toast } = useToast()
  return toast ? <Toast message={toast.message} type={toast.type} /> : null
}

function GptTaskBridge({ children }) {
  const { showToast } = useToast()
  return <GptTaskProvider showToast={showToast}>{children}</GptTaskProvider>
}

function KeepAlive() {
  useKeepAlive()
  return null
}

export default function Providers({ children }) {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''
  return (
    <HelmetProvider>
      <ThemeProvider>
        <GoogleOAuthProvider clientId={clientId}>
          <AuthProvider>
            <ToastProvider>
              <GptTaskBridge>
                <KeepAlive />
                {children}
                <ToastOutlet />
              </GptTaskBridge>
            </ToastProvider>
          </AuthProvider>
        </GoogleOAuthProvider>
      </ThemeProvider>
    </HelmetProvider>
  )
}
