'use client'

import StoryReaderPage from '../../../../../src/views/StoryReaderPage'
import { useToast } from '../../../../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <StoryReaderPage showToast={showToast} />
}
