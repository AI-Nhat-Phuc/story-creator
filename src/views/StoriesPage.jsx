'use client'

import { useToast } from '../contexts/ToastContext'
import StoriesContainer from '../containers/StoriesContainer'

function StoriesPage({ initialData }) {
  const { showToast } = useToast()
  return <StoriesContainer showToast={showToast} initialData={initialData} />
}

export default StoriesPage
