'use client'

import NovelPage from '../../../../../src/views/NovelPage'
import { useToast } from '../../../../../src/contexts/ToastContext'

export default function Page() {
  const { showToast } = useToast()
  return <NovelPage showToast={showToast} />
}
