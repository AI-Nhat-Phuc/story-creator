'use client'

import StoriesPage from '../../../src/views/StoriesPage'
import { useToast } from '../../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <StoriesPage showToast={showToast} />
}
