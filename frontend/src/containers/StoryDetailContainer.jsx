import React, { useState, useEffect } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'
import { storiesAPI, worldsAPI, gptAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import StoryDetailView from '../components/storyDetail/StoryDetailView'
import { useGptTasks } from '../contexts/GptTaskContext'
import { useAuth } from '../contexts/AuthContext'

function StoryDetailContainer({ showToast }) {
  const { t } = useTranslation()
  const { storyId } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { registerTask } = useGptTasks()
  const [searchParams] = useSearchParams()
  const highlightEventId = searchParams.get('event')
  const highlightPosition = parseInt(searchParams.get('position') || '-1', 10)
  const [story, setStory] = useState(null)
  const [world, setWorld] = useState(null)
  const [linkedCharacters, setLinkedCharacters] = useState([])
  const [linkedLocations, setLinkedLocations] = useState([])
  const [loading, setLoading] = useState(true)
  const [gptAnalyzing, setGptAnalyzing] = useState(false)
  const [analyzedEntities, setAnalyzedEntities] = useState(null)
  const [showAnalyzedModal, setShowAnalyzedModal] = useState(false)

  useEffect(() => {
    loadStoryDetails()
  }, [storyId])

  const loadStoryDetails = async () => {
    try {
      setLoading(true)
      const storyRes = await storiesAPI.getById(storyId)
      const storyData = storyRes.data
      setStory(storyData)

      if (storyData.world_id) {
        const worldRes = await worldsAPI.getById(storyData.world_id)
        setWorld(worldRes.data)

        // Load characters and locations linked to this story
        const storyEntityIds = storyData.entities || []
        const storyLocationIds = storyData.locations || []

        if (storyEntityIds.length > 0) {
          const charsRes = await worldsAPI.getCharacters(storyData.world_id)
          const allChars = charsRes.data || []
          setLinkedCharacters(allChars.filter(c => storyEntityIds.includes(c.entity_id)))
        } else {
          setLinkedCharacters([])
        }

        if (storyLocationIds.length > 0) {
          const locsRes = await worldsAPI.getLocations(storyData.world_id)
          const allLocs = locsRes.data || []
          setLinkedLocations(allLocs.filter(l => storyLocationIds.includes(l.location_id)))
        } else {
          setLinkedLocations([])
        }
      } else {
        setWorld(null)
        setLinkedCharacters([])
        setLinkedLocations([])
      }
    } catch (error) {
      showToast(t('pages.storyDetail.loadError'), 'error')
    } finally {
      setLoading(false)
    }
  }

  const normalizeTimeIndex = (value) => {
    if (value === undefined || value === null) return null
    const numeric = Number(value)
    return Number.isFinite(numeric) ? numeric : null
  }

  const computeWorldTimeFromIndex = (worldData, timeIndex) => {
    if (!worldData) return null
    const normalizedIndex = normalizeTimeIndex(timeIndex)
    if (normalizedIndex === null) return null
    const calendar = worldData.metadata?.calendar
    if (!calendar) return null

    if (normalizedIndex === 0) {
      return {
        year: 0,
        era: '',
        year_name: '',
        description: 'Không xác định'
      }
    }

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

  const getStoryWorldTime = (currentStory) => {
    if (!currentStory) return null
    if (currentStory.metadata?.world_time) return currentStory.metadata.world_time
    return computeWorldTimeFromIndex(world, currentStory.time_index)
  }

  const formatWorldTime = (currentStory) => {
    const worldTime = getStoryWorldTime(currentStory)
    const normalizedIndex = normalizeTimeIndex(currentStory.time_index)
    if (worldTime) {
      if (worldTime.year === 0) {
        return worldTime.description || 'Không xác định'
      }
      return worldTime.description || `Năm ${worldTime.year}`
    }
    if (normalizedIndex !== null && normalizedIndex !== 0) {
      return `Chỉ số: ${normalizedIndex}`
    }
    return 'Mốc chưa xác định'
  }

  const handleAnalyzeStory = async () => {
    if (!user) {
      showToast(t('pages.storyDetail.loginRequired'), 'warning')
      return
    }
    if (!story?.content) {
      showToast(t('pages.storyDetail.noContent'), 'warning')
      return
    }

    try {
      setGptAnalyzing(true)
      const response = await gptAPI.analyze({
        story_description: story.content,
        story_title: story.title,
        story_genre: story.genre
      })

      const taskId = response.data.task_id

      registerTask(taskId, {
        label: `Phân tích: ${story.title}`,
        task_type: 'analyze_entities',
        onComplete: (taskData) => {
          if (taskData.status === 'completed') {
            setAnalyzedEntities(taskData.result)
            setShowAnalyzedModal(true)
          }
          setGptAnalyzing(false)
        }
      })
    } catch (error) {
      showToast(t('pages.storyDetail.gptError'), 'error')
      setGptAnalyzing(false)
    }
  }

  const handleClearAnalyzedEntities = () => {
    setAnalyzedEntities(null)
    setShowAnalyzedModal(false)
  }

  const handleCloseAnalyzedModal = () => {
    setShowAnalyzedModal(false)
  }

  const handleUpdateAnalyzedEntities = (updated) => {
    setAnalyzedEntities(updated)
  }

  const handleLinkEntities = async () => {
    if (!analyzedEntities) {
      showToast(t('pages.storyDetail.noAnalysis'), 'warning')
      return
    }

    try {
      const response = await storiesAPI.linkEntities(storyId, {
        characters: analyzedEntities.characters || [],
        locations: analyzedEntities.locations || [],
        auto_create: true
      })

      const { created_entities, created_locations } = response.data
      const createdCount = (created_entities?.length || 0) + (created_locations?.length || 0)

      // Update story with linked entities and reload to get character/location details
      setStory(response.data.story)
      setAnalyzedEntities(null)
      setShowAnalyzedModal(false)

      if (createdCount > 0) {
        showToast(t('pages.storyDetail.linkSuccessWithCount', { chars: created_entities?.length || 0, locs: created_locations?.length || 0 }), 'success')
      } else {
        showToast(t('pages.storyDetail.linkSuccess'), 'success')
      }

      // Reload to get full character/location data
      loadStoryDetails()
    } catch (error) {
      showToast(t('pages.storyDetail.linkError') + ': ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handleReanalyzeStory = async () => {
    if (!user) {
      showToast(t('pages.storyDetail.loginRequired'), 'warning')
      return
    }
    if (!story?.content) {
      showToast(t('pages.storyDetail.noContent'), 'warning')
      return
    }

    try {
      // Step 1: Clear existing links
      await storiesAPI.clearLinks(storyId)
      setLinkedCharacters([])
      setLinkedLocations([])
      setStory(prev => ({ ...prev, entities: [], locations: [] }))
      showToast(t('pages.storyDetail.clearingLinks'), 'info')

      // Step 2: Run GPT analysis
      setGptAnalyzing(true)
      const response = await gptAPI.analyze({
        story_description: story.content,
        story_title: story.title,
        story_genre: story.genre
      })

      const taskId = response.data.task_id

      registerTask(taskId, {
        label: `Phân tích lại: ${story.title}`,
        task_type: 'analyze_entities',
        onComplete: (taskData) => {
          if (taskData.status === 'completed') {
            setAnalyzedEntities(taskData.result)
            setShowAnalyzedModal(true)
          }
          setGptAnalyzing(false)
        }
      })
    } catch (error) {
      showToast(t('pages.storyDetail.reanalyzeError') + ': ' + (error.response?.data?.error || error.message), 'error')
      setGptAnalyzing(false)
    }
  }

  const handleDeleteStory = async () => {
    if (!confirm(t('pages.storyDetail.deleteConfirm', { name: story.title }))) {
      return
    }

    try {
      await storiesAPI.delete(storyId)
      showToast(t('pages.storyDetail.deleteSuccess', { name: story.title }), 'success')
      // Navigate back to world or stories list
      if (story.world_id) {
        navigate(`/worlds/${story.world_id}`)
      } else {
        navigate('/stories')
      }
    } catch (error) {
      showToast(t('pages.storyDetail.deleteError') + ': ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  if (loading) return <LoadingSpinner />
  if (!story) return <div>{t('pages.storyDetail.notFound')}</div>

  const displayWorldTime = getStoryWorldTime(story)
  const normalizedTimelineIndex = normalizeTimeIndex(story.time_index)
  const formattedWorldTime = formatWorldTime(story)

  const canEdit = !!(user && story && user.user_id === story.owner_id)
  const pageTitle = story.title
    ? t('meta.storyDetail.titleTemplate', { name: story.title })
    : t('meta.storyDetail.titleFallback')

  return (
    <>
      <Helmet>
        <title>{pageTitle}</title>
        <meta name="description" content={t('meta.storyDetail.description')} />
      </Helmet>
      <StoryDetailView
      story={story}
      world={world}
      linkedCharacters={linkedCharacters}
      linkedLocations={linkedLocations}
      canEdit={canEdit}
      formattedWorldTime={formattedWorldTime}
      displayWorldTime={displayWorldTime}
      normalizedTimelineIndex={normalizedTimelineIndex}
      gptAnalyzing={gptAnalyzing}
      analyzedEntities={analyzedEntities}
      onAnalyzeStory={handleAnalyzeStory}
      showAnalyzedModal={showAnalyzedModal}
      onCloseAnalyzedModal={handleCloseAnalyzedModal}
      onClearAnalyzedEntities={handleClearAnalyzedEntities}
      onUpdateAnalyzedEntities={handleUpdateAnalyzedEntities}
      onLinkEntities={handleLinkEntities}
      onReanalyzeStory={handleReanalyzeStory}
      onDeleteStory={handleDeleteStory}
      highlightEventId={highlightEventId}
      highlightPosition={highlightPosition}
    />
    </>
  )
}

export default StoryDetailContainer
