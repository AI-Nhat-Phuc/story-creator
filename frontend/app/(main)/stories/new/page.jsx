'use client'

import StoryEditorPage from '../../../../src/views/StoryEditorPage'
import { useToast } from '../../../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <StoryEditorPage showToast={showToast} />
}
