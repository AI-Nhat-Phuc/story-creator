'use client'

import React, { useState, useEffect } from 'react'
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'
import { storiesAPI, worldsAPI } from '../services/api'
import DiscoveryView from '../components/discovery/DiscoveryView'

function DiscoveryContainer({ showToast }) {
  const { t } = useTranslation()
  const [stories, setStories] = useState([])
  const [worlds, setWorlds] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        setIsLoading(true)
        const [storiesRes, worldsRes] = await Promise.all([
          storiesAPI.getAll(),
          worldsAPI.getAll(),
        ])
        const worldList = worldsRes.data || []
        const worldMap = Object.fromEntries(worldList.map(w => [w.world_id, w.name]))

        // Sort stories by updated_at DESC, extract plain-text preview, show latest 8
        const sorted = [...(storiesRes.data || [])]
          .sort((a, b) => (b.updated_at || b.created_at || '').localeCompare(a.updated_at || a.created_at || ''))
          .slice(0, 8)
          .map(s => ({
            ...s,
            world_name: worldMap[s.world_id] || null,
            content_preview: s.content_preview
              || (s.content ? s.content.replace(/<[^>]*>/g, '').slice(0, 160) : ''),
          }))
        setStories(sorted)
        setWorlds(worldList.slice(0, 6))
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
