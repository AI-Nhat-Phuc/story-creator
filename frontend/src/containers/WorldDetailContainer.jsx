import React, { useState, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'
import { usePageTitle } from '../hooks/usePageTitle'
import { worldsAPI, gptAPI, collaboratorsAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import WorldDetailView from '../components/worldDetail/WorldDetailView'
import { useAuth } from '../contexts/AuthContext'
import { useGptTasks } from '../contexts/GptTaskContext'

const STORIES_PER_PAGE = 20

function WorldDetailContainer({ showToast }) {
  const { t } = useTranslation()
  const { worldId } = useParams()
  const { user, loading: authLoading } = useAuth()
  const { registerTask } = useGptTasks()
  const [world, setWorld] = useState(null)
  const [stories, setStories] = useState([])
  const [storiesTotalPages, setStoriesTotalPages] = useState(0)
  const [storiesPage, setStoriesPage] = useState(1)
  const [loadingMoreStories, setLoadingMoreStories] = useState(false)
  const [characters, setCharacters] = useState([])
  const [locations, setLocations] = useState([])
  const [activeTab, setActiveTab] = useState('stories')
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState({ name: '', description: '', visibility: '' })
  const [autoLinking, setAutoLinking] = useState(false)

  // Collaborators state
  const [collaborators, setCollaborators] = useState([])
  const [inviteLoading, setInviteLoading] = useState(false)

  // Unlinked stories modal state
  const [showUnlinkedModal, setShowUnlinkedModal] = useState(false)
  const [unlinkedStories, setUnlinkedStories] = useState([])
  const [batchAnalyzing, setBatchAnalyzing] = useState(false)
  const [batchProgress, setBatchProgress] = useState(null)
  const [batchResult, setBatchResult] = useState(null)
  const pageTitle = usePageTitle('worldDetail', world?.name)

  useEffect(() => {
    loadWorldDetails()
  }, [worldId])

  const loadWorldDetails = async () => {
    try {
      setLoading(true)
      const [worldRes, storiesRes, charsRes, locsRes, collabRes] = await Promise.all([
        worldsAPI.getById(worldId),
        worldsAPI.getStories(worldId, { page: 1, perPage: STORIES_PER_PAGE }),
        worldsAPI.getCharacters(worldId),
        worldsAPI.getLocations(worldId),
        collaboratorsAPI.list(worldId).catch(() => ({ data: [] })),
      ])

      setWorld(worldRes.data)
      setStories(storiesRes.data)
      setStoriesPage(1)
      setStoriesTotalPages(storiesRes.pagination?.total_pages ?? 1)
      setCharacters(charsRes.data)
      setLocations(locsRes.data)
      setCollaborators(collabRes.data || [])
      setEditForm({ name: worldRes.data.name, description: worldRes.data.description, visibility: worldRes.data.visibility || 'draft' })
    } catch (error) {
      showToast(t('pages.worldDetail.loadError'), 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleLoadMoreStories = useCallback(async () => {
    const nextPage = storiesPage + 1
    if (nextPage > storiesTotalPages || loadingMoreStories) return
    try {
      setLoadingMoreStories(true)
      const res = await worldsAPI.getStories(worldId, { page: nextPage, perPage: STORIES_PER_PAGE })
      setStories(prev => [...prev, ...res.data])
      setStoriesPage(nextPage)
      setStoriesTotalPages(res.pagination?.total_pages ?? storiesTotalPages)
    } catch (error) {
      showToast(t('pages.worldDetail.loadError'), 'error')
    } finally {
      setLoadingMoreStories(false)
    }
  }, [worldId, storiesPage, storiesTotalPages, loadingMoreStories, showToast, t])

  const computeWorldTimeFromIndex = (timeIndex) => {
    if (!world) return null
    if (timeIndex === undefined || timeIndex === null) return null
    const calendar = world.metadata?.calendar
    if (!calendar) return null

    if (timeIndex === 0) {
      return { year: 0, era: '', year_name: '', description: t('common.timeNotSet') }
    }

    const currentYear = calendar.current_year || 1
    const yearRange = 100
    const offset = Math.floor((timeIndex / 100) * yearRange) - Math.floor(yearRange / 2)
    const year = Math.max(1, currentYear + offset)
    const yearLabel = calendar.year_name || t('common.year')

    return {
      year,
      era: calendar.current_era || '',
      year_name: yearLabel,
      description: `${yearLabel} ${year}${calendar.current_era ? `, ${calendar.current_era}` : ''}`.trim()
    }
  }

  const getStoryWorldTime = (story) => {
    if (!story) return null
    if (story.metadata?.world_time) return story.metadata.world_time
    return computeWorldTimeFromIndex(story.time_index)
  }

  const getTimelineLabel = (story) => {
    const worldTime = getStoryWorldTime(story)
    if (worldTime) {
      return worldTime.year === 0
        ? t('common.timeNotSet')
        : worldTime.description || `${worldTime.year_name || t('common.year')} ${worldTime.year}`
    }
    if (story.time_index !== undefined && story.time_index !== null && story.time_index !== 0) {
      return t('common.timeIndexLabel', { index: story.time_index })
    }
    return t('common.timelineUnknown')
  }

  const handleAutoLinkStories = async () => {
    try {
      setAutoLinking(true)
      const response = await worldsAPI.autoLinkStories(worldId)
      const { linked_count, links, unlinked_stories } = response.data

      if (linked_count > 0) {
        showToast(t('pages.worldDetail.autoLinkSuccess', { count: linked_count, links: links.length }), 'success')
        loadWorldDetails()
      } else if (unlinked_stories && unlinked_stories.length > 0) {
        setUnlinkedStories(unlinked_stories)
        setBatchResult(null)
        setBatchProgress(null)
        setShowUnlinkedModal(true)
      } else {
        showToast(t('pages.worldDetail.autoLinkNone'), 'info')
      }
    } catch (error) {
      showToast(t('pages.worldDetail.autoLinkError') + ': ' + (error.response?.data?.error || error.message), 'error')
    } finally {
      setAutoLinking(false)
    }
  }

  const handleBatchAnalyze = async (storyIds) => {
    if (!user) {
      showToast(t('pages.worldDetail.loginRequired'), 'warning')
      return
    }
    try {
      setBatchAnalyzing(true)
      setBatchProgress({ progress: 0, total: storyIds.length, current_story: '' })

      const response = await gptAPI.batchAnalyzeStories({
        world_id: worldId,
        story_ids: storyIds
      })
      const taskId = response.data.task_id

      registerTask(taskId, {
        label: `Batch analyze ${storyIds.length} stories`,
        task_type: 'batch_analyze',
        onComplete: (taskData) => {
          if (taskData.status === 'completed') {
            setBatchResult(prev => {
              if (!prev) return taskData.result
              const prevStories = prev.analyzed_stories || []
              const newStories = taskData.result.analyzed_stories || []
              return {
                ...taskData.result,
                analyzed_stories: [...prevStories, ...newStories],
                total_characters_found: (prev.total_characters_found || 0) + (taskData.result.total_characters_found || 0),
                total_locations_found: (prev.total_locations_found || 0) + (taskData.result.total_locations_found || 0),
              }
            })
            showToast(taskData.result.message || t('pages.worldDetail.batchDone'), 'success')
          }
          setBatchAnalyzing(false)
        }
      })
    } catch (error) {
      showToast(t('pages.worldDetail.batchError') + ': ' + (error.response?.data?.error || error.message), 'error')
      setBatchAnalyzing(false)
    }
  }

  const handleCloseUnlinkedModal = () => {
    setShowUnlinkedModal(false)
    if (batchResult) {
      // Reload data after batch analysis completed
      loadWorldDetails()
    }
  }

  const handleDeleteEntity = async (entityId, entityName) => {
    if (!confirm(t('common.deleteConfirm', { name: entityName }))) return

    try {
      await worldsAPI.deleteEntity(worldId, entityId)
      setCharacters(prev => prev.filter(c => c.entity_id !== entityId))
      showToast(t('pages.worldDetail.deleteEntitySuccess', { name: entityName }), 'success')
    } catch (error) {
      showToast(t('pages.worldDetail.deleteEntityError') + ': ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handleUpdateEntity = async (entityId, updatedData) => {
    try {
      const response = await worldsAPI.updateEntity(worldId, entityId, updatedData)
      setCharacters(prev => prev.map(c => c.entity_id === entityId ? { ...c, ...response.data } : c))
      showToast(t('pages.worldDetail.updateEntitySuccess'), 'success')
    } catch (error) {
      showToast(t('pages.worldDetail.updateEntityError') + ': ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handleDeleteLocation = async (locationId, locationName) => {
    if (!confirm(t('common.deleteConfirm', { name: locationName }))) return

    try {
      await worldsAPI.deleteLocation(worldId, locationId)
      setLocations(prev => prev.filter(l => l.location_id !== locationId))
      showToast(t('pages.worldDetail.deleteLocationSuccess', { name: locationName }), 'success')
    } catch (error) {
      showToast(t('pages.worldDetail.deleteLocationError') + ': ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handleDeleteStory = async (storyId, storyTitle) => {
    if (!confirm(t('common.deleteConfirm', { name: storyTitle }))) return

    try {
      await storiesAPI.delete(storyId)
      setStories(prev => prev.filter(s => s.story_id !== storyId))
      showToast(t('pages.worldDetail.deleteStorySuccess', { name: storyTitle }), 'success')
    } catch (error) {
      showToast(t('pages.worldDetail.deleteStoryError') + ': ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handlePublish = async (newVisibility) => {
    try {
      await worldsAPI.update(worldId, { visibility: newVisibility })
      setWorld(prev => ({ ...prev, visibility: newVisibility }))
      setEditForm(prev => ({ ...prev, visibility: newVisibility }))
      showToast(t('pages.worldDetail.publishSuccess', { visibility: t(newVisibility === 'public' ? 'common.public' : 'common.private') }), 'success')
    } catch (error) {
      showToast(t('pages.worldDetail.publishError') + ': ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handleEdit = () => setEditing(true)

  const handleCancelEdit = () => {
    setEditing(false)
    if (world) {
      setEditForm({ name: world.name, description: world.description, visibility: world.visibility || 'draft' })
    }
  }

  const handleEditFormChange = (field, value) => {
    setEditForm(prev => ({ ...prev, [field]: value }))
  }

  const handleSaveEdit = async () => {
    try {
      await worldsAPI.update(worldId, editForm)
      setWorld(prev => ({ ...prev, ...editForm }))
      setEditing(false)
      showToast(t('pages.worldDetail.updateSuccess'), 'success')
    } catch (error) {
      showToast(t('pages.worldDetail.updateError') + ': ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handleInviteCollaborator = async (usernameOrEmail) => {
    setInviteLoading(true)
    try {
      const res = await collaboratorsAPI.invite(worldId, usernameOrEmail)
      const newCollaborator = res.data?.collaborator
      if (newCollaborator) {
        setCollaborators(prev => [...prev, newCollaborator])
      }
      showToast(t('pages.worldDetail.inviteSent', { name: usernameOrEmail }), 'success')
    } catch (err) {
      const status = err.response?.status
      if (status === 404) showToast(t('pages.worldDetail.inviteNotFound'), 'error')
      else if (status === 409) showToast(t('pages.worldDetail.invitePending'), 'warning')
      else showToast(t('pages.worldDetail.inviteError'), 'error')
    } finally {
      setInviteLoading(false)
    }
  }

  const handleRemoveCollaborator = async (userId) => {
    try {
      await collaboratorsAPI.remove(worldId, userId)
      setCollaborators(prev => prev.filter(c => c.user_id !== userId))
      showToast(t('pages.worldDetail.removeCollabSuccess'), 'success')
    } catch {
      showToast(t('pages.worldDetail.removeCollabError'), 'error')
    }
  }

  if (loading) return <LoadingSpinner />
  if (!world) return <div>{t('pages.worldDetail.notFound')}</div>

  const canEdit = !!(user && world && user.user_id === world.owner_id)

  return (
    <>
      <Helmet>
        <title>{pageTitle}</title>
        <meta name="description" content={t('meta.worldDetail.description')} />
      </Helmet>
      <WorldDetailView
      world={world}
      stories={stories}
      characters={characters}
      locations={locations}
      activeTab={activeTab}
      canEdit={canEdit}
      editing={editing}
      editForm={editForm}
      user={user}
      onChangeTab={setActiveTab}
      onEdit={handleEdit}
      onPublish={handlePublish}
      onCancelEdit={handleCancelEdit}
      onSaveEdit={handleSaveEdit}
      onChangeField={handleEditFormChange}
      getStoryWorldTime={getStoryWorldTime}
      getTimelineLabel={getTimelineLabel}
      // Auto-link props
      autoLinking={autoLinking}
      onAutoLinkStories={handleAutoLinkStories}
      authLoading={authLoading}
      // Unlinked stories modal props
      showUnlinkedModal={showUnlinkedModal}
      unlinkedStories={unlinkedStories}
      batchAnalyzing={batchAnalyzing}
      batchProgress={batchProgress}
      batchResult={batchResult}
      onBatchAnalyze={handleBatchAnalyze}
      onCloseUnlinkedModal={handleCloseUnlinkedModal}
      // Delete entity/location/story props
      onDeleteEntity={handleDeleteEntity}
      onUpdateEntity={handleUpdateEntity}
      onDeleteLocation={handleDeleteLocation}
      onDeleteStory={handleDeleteStory}
      // Collaborators props
      collaborators={collaborators}
      inviteLoading={inviteLoading}
      onInviteCollaborator={handleInviteCollaborator}
      onRemoveCollaborator={handleRemoveCollaborator}
      // Pagination props
      hasMoreStories={storiesPage < storiesTotalPages}
      loadingMoreStories={loadingMoreStories}
      onLoadMoreStories={handleLoadMoreStories}
    />
    </>
  )
}

export default WorldDetailContainer
