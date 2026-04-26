'use client'

import WorldsPage from '../../../src/views/WorldsPage'
import { useToast } from '../../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <WorldsPage showToast={showToast} />
}
