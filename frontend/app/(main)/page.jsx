'use client'

import HomePage from '../../src/views/HomePage'
import { useToast } from '../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <HomePage showToast={showToast} />
}
