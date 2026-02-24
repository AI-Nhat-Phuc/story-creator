import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { worldsAPI, storiesAPI, gptAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import WorldDetailView from '../components/worldDetail/WorldDetailView'
import { useAuth } from '../contexts/AuthContext'
import { useGptTasks } from '../contexts/GptTaskContext'

const initialStoryForm = {
  title: '',
  description: '',
  genre: 'adventure',
  time_index: 0,
  visibility: ''
}

function WorldDetailContainer({ showToast }) {
  const { worldId } = useParams()
  const { user, loading: authLoading } = useAuth()
  const { registerTask } = useGptTasks()
  const [world, setWorld] = useState(null)
  const [stories, setStories] = useState([])
  const [characters, setCharacters] = useState([])
  const [locations, setLocations] = useState([])
  const [activeTab, setActiveTab] = useState('stories')
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState({ name: '', description: '', visibility: '' })

  // Story creation state
  const [showStoryModal, setShowStoryModal] = useState(false)
  const [storyForm, setStoryForm] = useState(initialStoryForm)
  const [gptGenerating, setGptGenerating] = useState(false)
  const [gptAnalyzing, setGptAnalyzing] = useState(false)
  const [analyzedEntities, setAnalyzedEntities] = useState(null)
  const [showAnalyzedModal, setShowAnalyzedModal] = useState(false)
  const [autoLinking, setAutoLinking] = useState(false)

  // Unlinked stories modal state
  const [showUnlinkedModal, setShowUnlinkedModal] = useState(false)
  const [unlinkedStories, setUnlinkedStories] = useState([])
  const [batchAnalyzing, setBatchAnalyzing] = useState(false)
  const [batchProgress, setBatchProgress] = useState(null)
  const [batchResult, setBatchResult] = useState(null)

  useEffect(() => {
    loadWorldDetails()
  }, [worldId])

  const loadWorldDetails = async () => {
    try {
      setLoading(true)
      const [worldRes, storiesRes, charsRes, locsRes] = await Promise.all([
        worldsAPI.getById(worldId),
        worldsAPI.getStories(worldId),
        worldsAPI.getCharacters(worldId),
        worldsAPI.getLocations(worldId)
      ])

      setWorld(worldRes.data)
      setStories(storiesRes.data)
      setCharacters(charsRes.data)
      setLocations(locsRes.data)
      setEditForm({ name: worldRes.data.name, description: worldRes.data.description, visibility: worldRes.data.visibility || 'private' })
    } catch (error) {
      showToast('Không thể tải chi tiết thế giới', 'error')
    } finally {
      setLoading(false)
    }
  }

  const computeWorldTimeFromIndex = (timeIndex) => {
    if (!world) return null
    if (timeIndex === undefined || timeIndex === null) return null
    const calendar = world.metadata?.calendar
    if (!calendar) return null

    if (timeIndex === 0) {
      return {
        year: 0,
        era: '',
        year_name: '',
        description: 'Không xác định'
      }
    }

    const currentYear = calendar.current_year || 1
    const yearRange = 100
    const offset = Math.floor((timeIndex / 100) * yearRange) - Math.floor(yearRange / 2)
    const year = Math.max(1, currentYear + offset)

    return {
      year,
      era: calendar.current_era || '',
      year_name: calendar.year_name || 'Năm',
      description: `${calendar.year_name || 'Năm'} ${year}${calendar.current_era ? `, ${calendar.current_era}` : ''}`.trim()
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
        ? worldTime.description || 'Không xác định'
        : worldTime.description || `${worldTime.year_name || 'Năm'} ${worldTime.year}`
    }
    if (story.time_index !== undefined && story.time_index !== null && story.time_index !== 0) {
      return `Chỉ số ${story.time_index}`
    }
    return 'Mốc thời gian chưa xác định'
  }

  const handleAutoLinkStories = async () => {
    try {
      setAutoLinking(true)
      const response = await worldsAPI.autoLinkStories(worldId)
      const { message, linked_count, links, unlinked_stories } = response.data

      if (linked_count > 0) {
        showToast(`${message}. Tìm thấy ${links.length} liên kết mới!`, 'success')
        loadWorldDetails() // Reload to show updated links
      } else if (unlinked_stories && unlinked_stories.length > 0) {
        // Show unlinked stories modal for batch analysis
        setUnlinkedStories(unlinked_stories)
        setBatchResult(null)
        setBatchProgress(null)
        setShowUnlinkedModal(true)
      } else {
        showToast(message || 'Không tìm thấy liên kết nào', 'info')
      }
    } catch (error) {
      showToast('Lỗi khi liên kết câu chuyện: ' + (error.response?.data?.error || error.message), 'error')
    } finally {
      setAutoLinking(false)
    }
  }

  const handleBatchAnalyze = async (storyIds) => {
    if (!user) {
      showToast('Vui lòng đăng nhập để sử dụng tính năng phân tích GPT', 'warning')
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
        label: `Phân tích batch ${storyIds.length} truyện`,
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
            showToast(taskData.result.message || 'Phân tích hoàn tất!', 'success')
          }
          setBatchAnalyzing(false)
        }
      })
    } catch (error) {
      showToast('Lỗi phân tích batch: ' + (error.response?.data?.error || error.message), 'error')
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
    if (!confirm(`Bạn có chắc muốn xóa nhân vật "${entityName}"? Hành động này không thể hoàn tác.`)) {
      return
    }

    try {
      await worldsAPI.deleteEntity(worldId, entityId)
      setCharacters(prev => prev.filter(c => c.entity_id !== entityId))
      showToast(`Đã xóa nhân vật "${entityName}"`, 'success')
    } catch (error) {
      showToast('Lỗi khi xóa nhân vật: ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handleDeleteLocation = async (locationId, locationName) => {
    if (!confirm(`Bạn có chắc muốn xóa địa điểm "${locationName}"? Hành động này không thể hoàn tác.`)) {
      return
    }

    try {
      await worldsAPI.deleteLocation(worldId, locationId)
      setLocations(prev => prev.filter(l => l.location_id !== locationId))
      showToast(`Đã xóa địa điểm "${locationName}"`, 'success')
    } catch (error) {
      showToast('Lỗi khi xóa địa điểm: ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handleDeleteStory = async (storyId, storyTitle) => {
    if (!confirm(`Bạn có chắc muốn xóa câu chuyện "${storyTitle}"? Hành động này không thể hoàn tác.`)) {
      return
    }

    try {
      await storiesAPI.delete(storyId)
      setStories(prev => prev.filter(s => s.story_id !== storyId))
      showToast(`Đã xóa câu chuyện "${storyTitle}"`, 'success')
    } catch (error) {
      showToast('Lỗi khi xóa câu chuyện: ' + (error.response?.data?.error || error.message), 'error')
    }
  }

  const handleEdit = () => setEditing(true)

  const handleCancelEdit = () => {
    setEditing(false)
    if (world) {
      setEditForm({ name: world.name, description: world.description, visibility: world.visibility || 'private' })
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
      showToast('Đã cập nhật thế giới!', 'success')
    } catch (error) {
      showToast(`Lỗi cập nhật thế giới: ${error.response?.data?.error || error.message}`, 'error')
    }
  }

  // Story creation handlers
  const handleOpenStoryModal = () => {
    if (!user) {
      showToast('Vui lòng đăng nhập để tạo câu chuyện', 'warning')
      return
    }
    setShowStoryModal(true)
  }

  const handleCloseStoryModal = () => {
    setShowStoryModal(false)
    setStoryForm(initialStoryForm)
    setAnalyzedEntities(null)
    setShowAnalyzedModal(false)
    setGptGenerating(false)
    setGptAnalyzing(false)
  }

  const handleStoryFormChange = (e) => {
    const { name, value } = e.target
    setStoryForm(prev => ({
      ...prev,
      [name]: name === 'time_index' ? Number(value) : value
    }))
  }

  const handleGenerateStoryDescription = async () => {
    if (!user) {
      showToast('Vui lòng đăng nhập để sử dụng tính năng GPT', 'warning')
      return
    }
    if (!storyForm.title) {
      showToast('Vui lòng nhập tiêu đề trước', 'warning')
      return
    }

    try {
      setGptGenerating(true)
      const response = await gptAPI.generateDescription({
        type: 'story',
        story_title: storyForm.title,
        story_genre: storyForm.genre,
        world_description: world.description,
        characters: characters?.map(c => c.name).join(', ') || ''
      })

      const taskId = response.data.task_id

      registerTask(taskId, {
        label: `Tạo mô tả: ${storyForm.title}`,
        task_type: 'generate_story_description',
        onComplete: (taskData) => {
          if (taskData.status === 'completed') {
            const resultData = taskData.result
            const generatedDesc = 'story_description' in resultData
              ? resultData.story_description
              : (typeof resultData === 'string' ? resultData : '')
            setStoryForm(prev => ({ ...prev, description: generatedDesc }))
          }
          setGptGenerating(false)
        }
      })
    } catch (error) {
      showToast('Lỗi tạo mô tả GPT', 'error')
      setGptGenerating(false)
    }
  }

  const handleAnalyzeStory = async () => {
    if (!user) {
      showToast('Vui lòng đăng nhập để sử dụng tính năng phân tích GPT', 'warning')
      return
    }
    if (!storyForm.description) {
      showToast('Vui lòng nhập mô tả câu chuyện', 'warning')
      return
    }

    try {
      setGptAnalyzing(true)
      const response = await gptAPI.analyze({
        story_description: storyForm.description,
        story_title: storyForm.title,
        story_genre: storyForm.genre
      })

      const taskId = response.data.task_id

      registerTask(taskId, {
        label: `Phân tích: ${storyForm.title}`,
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
      showToast('Lỗi phân tích GPT', 'error')
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

  const handleOpenAnalyzedModal = () => {
    setShowAnalyzedModal(true)
  }

  const handleUpdateAnalyzedEntities = (updated) => {
    setAnalyzedEntities(updated)
  }

  const handleCreateStory = async (e) => {
    e.preventDefault()

    if (!user) {
      showToast('Vui lòng đăng nhập để tạo câu chuyện', 'warning')
      return
    }

    if (!storyForm.title || !storyForm.description) {
      showToast('Vui lòng điền đầy đủ thông tin', 'warning')
      return
    }

    try {
      const submitData = { ...storyForm, world_id: worldId }
      if (!submitData.visibility) delete submitData.visibility
      const response = await storiesAPI.create(submitData)
      const createdStory = response.data.story

      // If we have analyzed entities, link them
      if (analyzedEntities && createdStory?.story_id) {
        const hasEntities = analyzedEntities.characters?.length > 0 || analyzedEntities.locations?.length > 0
        if (hasEntities) {
          const linkRes = await storiesAPI.linkEntities(createdStory.story_id, {
            characters: analyzedEntities.characters || [],
            locations: analyzedEntities.locations || [],
            auto_create: true
          })
          const createdCount = (linkRes.data.created_entities?.length || 0) + (linkRes.data.created_locations?.length || 0)
          if (createdCount > 0) {
            showToast(`Tạo câu chuyện, liên kết và tạo mới ${linkRes.data.created_entities?.length || 0} nhân vật, ${linkRes.data.created_locations?.length || 0} địa điểm!`, 'success')
          } else {
            showToast('Tạo câu chuyện và liên kết thành công!', 'success')
          }
        } else {
          showToast('Tạo câu chuyện thành công!', 'success')
        }
      } else {
        showToast('Tạo câu chuyện thành công!', 'success')
      }

      handleCloseStoryModal()
      loadWorldDetails() // Reload to show new story
    } catch (error) {
      showToast('Không thể tạo câu chuyện: ' + (error.message || error), 'error')
    }
  }

  if (loading) return <LoadingSpinner />
  if (!world) return <div>Không tìm thấy thế giới</div>

  const canEdit = !!(user && world && user.user_id === world.owner_id)

  return (
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
      onDeleteLocation={handleDeleteLocation}
      onDeleteStory={handleDeleteStory}
      // Story creation props
      showStoryModal={showStoryModal}
      storyForm={storyForm}
      gptGenerating={gptGenerating}
      gptAnalyzing={gptAnalyzing}
      analyzedEntities={analyzedEntities}
      onOpenStoryModal={handleOpenStoryModal}
      onCloseStoryModal={handleCloseStoryModal}
      onStoryFormChange={handleStoryFormChange}
      onGenerateStoryDescription={handleGenerateStoryDescription}
      onAnalyzeStory={handleAnalyzeStory}
      showAnalyzedModal={showAnalyzedModal}
      onCloseAnalyzedModal={handleCloseAnalyzedModal}
      onOpenAnalyzedModal={handleOpenAnalyzedModal}
      onClearAnalyzedEntities={handleClearAnalyzedEntities}
      onUpdateAnalyzedEntities={handleUpdateAnalyzedEntities}
      onCreateStory={handleCreateStory}
    />
  )
}

export default WorldDetailContainer
