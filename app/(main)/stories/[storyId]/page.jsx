'use client'

import StoryDetailPage from '../../../../src/views/StoryDetailPage'
import { useToast } from '../../../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <StoryDetailPage showToast={showToast} />
}
