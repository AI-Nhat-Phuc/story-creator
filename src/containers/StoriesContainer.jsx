'use client'

import React, { useState, useEffect } from 'react'
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'
import { worldsAPI, storiesAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import StoriesView from '../components/stories/StoriesView'
import { useAuth } from '../contexts/AuthContext'

function StoriesContainer({ showToast }) {
  const { t } = useTranslation()
  const { user, loading: authLoading } = useAuth()
  const [worlds, setWorlds] = useState([])
  const [stories, setStories] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
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
      <Helmet>
        <title>{t('meta.stories.title')}</title>
        <meta name="description" content={t('meta.stories.description')} />
      </Helmet>
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
