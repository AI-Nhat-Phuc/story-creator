'use client'

import NovelContainer from '../containers/NovelContainer'
import { useToast } from '../contexts/ToastContext'

function NovelPage({ initialData, locale }) {
  const { showToast } = useToast()
  return <NovelContainer showToast={showToast} initialData={initialData} locale={locale} />
}

export default NovelPage
