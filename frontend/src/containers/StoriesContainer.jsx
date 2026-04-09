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

  const normalizeTimeIndex = (value) => {
    if (value === undefined || value === null) return null
    const numeric = Number(value)
    return Number.isFinite(numeric) ? numeric : null
  }

  const computeWorldTimeFromIndex = (worldId, timeIndex) => {
    const normalizedIndex = normalizeTimeIndex(timeIndex)
    if (normalizedIndex === null) return null
    const world = findWorldById(worldId)
    if (!world) return null
    const calendar = world.metadata?.calendar
    if (!calendar) return null
    if (normalizedIndex === 0) return { year: 0, era: '', description: 'Không xác định', year_name: '' }
    const currentYear = calendar.current_year || 1
    const yearRange = 100
    const offset = Math.floor((normalizedIndex / 100) * yearRange) - Math.floor(yearRange / 2)
    const year = Math.max(1, currentYear + offset)
    return {
      year,
      era: calendar.current_era || '',
      year_name: calendar.year_name || 'Năm',
      description: `${calendar.year_name || 'Năm'} ${year}${calendar.current_era ? `, ${calendar.current_era}` : ''}`.trim()
    }
  }

  const formatWorldTime = (story) => {
    const worldTime = story.metadata?.world_time || computeWorldTimeFromIndex(story.world_id, story.time_index)
    const normalizedIndex = normalizeTimeIndex(story.time_index)
    if (worldTime) {
      if (worldTime.year === 0) return worldTime.description || 'Không xác định'
      return worldTime.description || `${worldTime.year_name || 'Năm'} ${worldTime.year}`
    }
    if (normalizedIndex !== null && normalizedIndex !== 0) return `Chỉ số: ${normalizedIndex}`
    return 'Mốc chưa xác định'
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
