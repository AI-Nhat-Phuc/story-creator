'use client'

import AdminPanel from '../../../src/views/AdminPanel'
import { useToast } from '../../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <AdminPanel showToast={showToast} />
}
