'use client'

import UserPermissionsPage from '../../../src/views/UserPermissionsPage'
import { useToast } from '../../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <UserPermissionsPage showToast={showToast} />
}
