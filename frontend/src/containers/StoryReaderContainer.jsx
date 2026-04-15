import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { storiesAPI } from '../services/api'
import StoryReaderView from '../components/storyReader/StoryReaderView'

function StoryReaderContainer({ showToast }) {
  const { t } = useTranslation()
  const { storyId } = useParams()
  const [story, setStory] = useState(null)
  const [neighbors, setNeighbors] = useState({ prev: null, next: null })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setIsLoading(true)
      try {
        const [storyRes, neighborsRes] = await Promise.all([
          storiesAPI.getById(storyId),
          storiesAPI.getNeighbors(storyId),
        ])
        if (cancelled) return
        setStory(storyRes.data)
        setNeighbors(neighborsRes.data)
      } catch {
        if (!cancelled && showToast) {
          showToast(t('pages.storyReader.loadError'), 'error')
        }
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [storyId, showToast, t])

  return (
    <StoryReaderView
      story={story}
      prev={neighbors.prev}
      next={neighbors.next}
      isLoading={isLoading}
    />
  )
}

export default StoryReaderContainer
