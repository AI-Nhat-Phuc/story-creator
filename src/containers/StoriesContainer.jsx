'use client'

import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { worldsAPI, storiesAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import StoriesView from '../components/stories/StoriesView'
import { useAuth } from '../contexts/AuthContext'

function StoriesContainer({ showToast, initialData }) {
  const { t } = useTranslation()
  const { user, loading: authLoading } = useAuth()
  const hasSSRData = initialData != null
  const [worlds, setWorlds] = useState(initialData?.worlds ?? [])
  const [stories, setStories] = useState(initialData?.stories ?? [])
  const [loading, setLoading] = useState(!hasSSRData)

  useEffect(() => {
    if (hasSSRData) return
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [worldsRes, storiesRes] = await Promise.all([
        worldsAPI.getAll(),
        storiesAPI.getAll()
      ])
      setWorlds(worldsRes.data)
      setStories(storiesRes.data)
    } catch (error) {
      showToast(t('pages.stories.loadError'), 'error')
    } finally {
      setLoading(false)
    }
  }

  const findWorldById = (worldId) => worlds.find(w => w.world_id === worldId)

  const getWorldName = (worldId) => {
    const world = findWorldById(worldId)
    return world ? world.name : 'Unknown World'
  }

  const formatWorldTime = (story) => {
    if (story?.order != null) {
      return t('common.chapterLabel', { number: story.order, defaultValue: `Chương ${story.order}` })
    }
    return t('pages.stories.unknownTime')
  }

  if (loading) return <LoadingSpinner />

  return (
    <>
      <StoriesView
      stories={stories}
      worlds={worlds}
      user={user}
      authLoading={authLoading}
      formatWorldTime={formatWorldTime}
      getWorldName={getWorldName}
    />
    </>
  )
}

export default StoriesContainer
