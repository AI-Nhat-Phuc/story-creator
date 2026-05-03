'use client'

import { HelmetProvider } from 'react-helmet-async'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { ThemeProvider } from '../src/contexts/ThemeContext'
import { AuthProvider } from '../src/contexts/AuthContext'
import { GptTaskProvider } from '../src/contexts/GptTaskContext'
import { ToastProvider, useToast } from '../src/contexts/ToastContext'
import Toast from '../src/components/Toast'
import { useKeepAlive } from '../src/hooks/useKeepAlive'
import { WritingModalProvider } from '../src/contexts/WritingModalContext'
import WritingModal from '../src/components/writingModal/WritingModal'
import '../src/i18n'

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

function WritingModalBridge({ children }) {
  const { showToast } = useToast()
  return (
    <WritingModalProvider showToast={showToast}>
      {children}
      <WritingModal />
    </WritingModalProvider>
  )
}

export default function Providers({ children }) {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''
  return (
    <HelmetProvider>
      <ThemeProvider>
        <GoogleOAuthProvider clientId={clientId}>
          <ToastProvider>
            <AuthProvider>
              <GptTaskBridge>
                <WritingModalBridge>
                  <KeepAlive />
                  {children}
                  <ToastOutlet />
                </WritingModalBridge>
              </GptTaskBridge>
            </AuthProvider>
          </ToastProvider>
        </GoogleOAuthProvider>
      </ThemeProvider>
    </HelmetProvider>
  )
}
