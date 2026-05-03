'use client'

import AdminUsersPage from '../../../../src/views/AdminUsersPage'
import { useToast } from '../../../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <AdminUsersPage showToast={showToast} />
}
