'use client'

import React, { useState, useEffect } from 'react'
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'
import { storiesAPI, worldsAPI } from '../services/api'
import { useToast } from '../contexts/ToastContext'
import DiscoveryView from '../components/discovery/DiscoveryView'

function processStories(storiesData, worldsData) {
  const worldMap = Object.fromEntries((worldsData || []).map(w => [w.world_id, w.name]))
  return [...(storiesData || [])]
    .sort((a, b) => (b.updated_at || b.created_at || '').localeCompare(a.updated_at || a.created_at || ''))
    .slice(0, 8)
    .map(s => ({
      ...s,
      world_name: worldMap[s.world_id] || null,
      content_preview: s.content_preview
        || (s.content ? s.content.replace(/<[^>]*>/g, '').slice(0, 160) : ''),
    }))
}

function DiscoveryContainer({ initialStories = [], initialWorlds = [] }) {
  const { t } = useTranslation()
  const { showToast } = useToast()

  const hasInitialData = initialStories.length > 0 || initialWorlds.length > 0
  const [stories, setStories] = useState(() => processStories(initialStories, initialWorlds))
  const [worlds, setWorlds] = useState(() => (initialWorlds || []).slice(0, 6))
  const [isLoading, setIsLoading] = useState(!hasInitialData)

  useEffect(() => {
    if (hasInitialData) return
    const load = async () => {
      try {
        setIsLoading(true)
        const [storiesRes, worldsRes] = await Promise.all([
          storiesAPI.getAll(),
          worldsAPI.getAll(),
        ])
        setStories(processStories(storiesRes.data, worldsRes.data))
        setWorlds((worldsRes.data || []).slice(0, 6))
      } catch {
        showToast(t('pages.home.loadError'), 'error')
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [])

  return (
    <>
      <Helmet>
        <title>{t('meta.home.title')}</title>
        <meta name="description" content={t('meta.home.description')} />
      </Helmet>
      <DiscoveryView stories={stories} worlds={worlds} isLoading={isLoading} />
    </>
  )
}

export default DiscoveryContainer
