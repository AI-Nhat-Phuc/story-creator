import React, { useState, useEffect } from 'react'
import { worldsAPI, storiesAPI, gptAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import StoriesView from '../components/stories/StoriesView'
import { useGptTasks } from '../contexts/GptTaskContext'

const initialFormState = {
  world_id: '',
  title: '',
  description: '',
  genre: 'adventure',
  time_index: 0
}

function StoriesContainer({ showToast }) {
  const { registerTask } = useGptTasks()
  const [worlds, setWorlds] = useState([])
  const [stories, setStories] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [formData, setFormData] = useState(initialFormState)
  const [gptGenerating, setGptGenerating] = useState(false)
  const [gptAnalyzing, setGptAnalyzing] = useState(false)
  const [detectedCharacters, setDetectedCharacters] = useState([])
  const [analyzedEntities, setAnalyzedEntities] = useState(null)
  const [availableCharacters, setAvailableCharacters] = useState([]);
  const [selectedCharacters, setSelectedCharacters] = useState([]);
  // Fetch characters for selected world when modal opens or world changes
  React.useEffect(() => {
    if (showCreateModal && formData.world_id) {
      worldsAPI.getCharacters(formData.world_id).then(res => {
        setAvailableCharacters(res.data || []);
      });
    } else if (!showCreateModal) {
      setAvailableCharacters([]);
      setSelectedCharacters([]);
    }
  }, [showCreateModal, formData.world_id]);

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
      showToast('Không thể tải dữ liệu', 'error')
    } finally {
      setLoading(false)
    }
  }

  const normalizeTimeIndex = (value) => {
    if (value === undefined || value === null) return null
    const numeric = Number(value)
    return Number.isFinite(numeric) ? numeric : null
  }

  const findWorldById = (worldId) => worlds.find(w => w.world_id === worldId)

  const getWorldName = (worldId) => {
    const world = findWorldById(worldId)
    return world ? world.name : 'Unknown World'
  }

  const computeWorldTimeFromIndex = (worldId, timeIndex) => {
    const normalizedIndex = normalizeTimeIndex(timeIndex)
    if (normalizedIndex === null) return null
    const world = findWorldById(worldId)
    if (!world) return null
    const calendar = world.metadata?.calendar
    if (!calendar) return null

    if (normalizedIndex === 0) {
      return {
        year: 0,
        era: '',
        description: 'Không xác định',
        year_name: ''
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

  const getDisplayWorldTime = (story) => {
    if (story.metadata?.world_time) return story.metadata.world_time
    return computeWorldTimeFromIndex(story.world_id, story.time_index)
  }

  const formatWorldTime = (story) => {
    const worldTime = getDisplayWorldTime(story)
    const normalizedIndex = normalizeTimeIndex(story.time_index)
    if (worldTime) {
      if (worldTime.year === 0) {
        return worldTime.description || 'Không xác định'
      }
      return worldTime.description || `${worldTime.year_name || 'Năm'} ${worldTime.year}`
    }
    if (normalizedIndex !== null && normalizedIndex !== 0) {
      return `Chỉ số: ${normalizedIndex}`
    }
    return 'Mốc chưa xác định'
  }

  const detectCharacters = async (description, worldId) => {
    if (!description || !worldId) return

    try {
      const worldResponse = await worldsAPI.getById(worldId)
      const characters = worldResponse.data.characters || []
      const mentioned = characters.filter(char =>
        description.toLowerCase().includes(char.name.toLowerCase())
      )
      setDetectedCharacters(mentioned)
    } catch (error) {
      console.error('Error detecting characters:', error)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'time_index' ? Number(value) : value
    }))

    if (name === 'description' && formData.world_id) {
      detectCharacters(value, formData.world_id)
    }
  }

  const handleGenerateDescription = async () => {
    if (!formData.title || !formData.world_id) {
      showToast('Vui lòng chọn thế giới và nhập tiêu đề trước', 'warning')
      return
    }

    try {
      setGptGenerating(true)
      const worldResponse = await worldsAPI.getById(formData.world_id)
      const world = worldResponse.data
      // Compose character names for GPT
      let characterNames = availableCharacters
        .filter(c => selectedCharacters.includes(c.entity_id))
        .map(c => c.name);
      if (selectedCharacters.includes('__new__')) {
        characterNames.push('NEW_CHARACTER'); // Special marker for GPT to generate a new name
      }
      const response = await gptAPI.generateDescription({
        type: 'story',
        story_title: formData.title,
        story_genre: formData.genre,
        world_description: world.description,
        characters: characterNames.join(', ')
      })

      const taskId = response.data.task_id

      registerTask(taskId, {
        label: `Tạo mô tả: ${formData.title}`,
        task_type: 'generate_story_description',
        onComplete: (taskData) => {
          if (taskData.status === 'completed') {
            const resultData = taskData.result
            const generatedDesc = 'story_description' in resultData
              ? resultData.story_description
              : (typeof resultData === 'string' ? resultData : '')
            setFormData(prev => ({ ...prev, description: generatedDesc }))
            detectCharacters(generatedDesc, formData.world_id)
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
    if (!formData.description) {
      showToast('Vui lòng nhập mô tả câu chuyện', 'warning')
      return
    }

    try {
      setGptAnalyzing(true)
      const response = await gptAPI.analyze({
        story_description: formData.description,
        story_title: formData.title,
        story_genre: formData.genre
      })

      const taskId = response.data.task_id

      registerTask(taskId, {
        label: `Phân tích: ${formData.title}`,
        task_type: 'analyze_entities',
        onComplete: (taskData) => {
          if (taskData.status === 'completed') {
            setAnalyzedEntities(taskData.result)
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
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.world_id || !formData.title || !formData.description) {
      showToast('Vui lòng điền đầy đủ thông tin (có thể dùng GPT để tạo mô tả)', 'warning')
      return
    }

    try {
      const response = await storiesAPI.create(formData)
      const createdStory = response.data.story

      // If we have analyzed entities, link them to the created story
      if (analyzedEntities && createdStory?.story_id) {
        const hasEntities = analyzedEntities.characters?.length > 0 || analyzedEntities.locations?.length > 0
        if (hasEntities) {
          await storiesAPI.linkEntities(createdStory.story_id, {
            characters: analyzedEntities.characters || [],
            locations: analyzedEntities.locations || []
          })
          showToast('Tạo câu chuyện và liên kết thành công!', 'success')
        } else {
          showToast('Tạo câu chuyện thành công!', 'success')
        }
      } else {
        showToast('Tạo câu chuyện thành công!', 'success')
      }

      setShowCreateModal(false)
      setFormData(initialFormState)
      setDetectedCharacters([])
      setAnalyzedEntities(null)
      loadData()
    } catch (error) {
      showToast('Không thể tạo câu chuyện: ' + (error.message || error), 'error')
    }
  }

  const handleOpenModal = () => {
    setShowCreateModal(true);
    setSelectedCharacters([]);
  }

  const handleCloseModal = () => {
    setShowCreateModal(false)
    setFormData(initialFormState)
    setDetectedCharacters([])
    setAnalyzedEntities(null)
    setGptGenerating(false)
    setGptAnalyzing(false)
    setAvailableCharacters([]);
    setSelectedCharacters([]);
  }

  if (loading) return <LoadingSpinner />

  return (
    <StoriesView
      stories={stories}
      worlds={worlds}
      showCreateModal={showCreateModal}
      formData={formData}
      detectedCharacters={detectedCharacters}
      analyzedEntities={analyzedEntities}
      gptGenerating={gptGenerating}
      gptAnalyzing={gptAnalyzing}
      onOpenModal={handleOpenModal}
      onCloseModal={handleCloseModal}
      onInputChange={handleInputChange}
      onSubmit={handleSubmit}
      onGenerateDescription={handleGenerateDescription}
      onAnalyzeStory={handleAnalyzeStory}
      onClearAnalyzedEntities={handleClearAnalyzedEntities}
      formatWorldTime={formatWorldTime}
      getWorldName={getWorldName}
      availableCharacters={availableCharacters}
      selectedCharacters={selectedCharacters}
      setSelectedCharacters={setSelectedCharacters}
    />
  )
}

export default StoriesContainer
