'use client'

import WorldDetailPage from '../../../../src/views/WorldDetailPage'
import { useToast } from '../../../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <WorldDetailPage showToast={showToast} />
}
