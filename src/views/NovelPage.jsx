'use client'

import NovelContainer from '../containers/NovelContainer'
import { useToast } from '../contexts/ToastContext'

function NovelPage({ initialData }) {
  const { showToast } = useToast()
  return <NovelContainer showToast={showToast} initialData={initialData} />
}

export default NovelPage
