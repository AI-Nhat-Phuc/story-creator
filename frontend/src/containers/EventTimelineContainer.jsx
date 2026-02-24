import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { ReactFlowProvider } from '@xyflow/react'
import { eventsAPI, gptAPI } from '../services/api'
import TimelineCanvas from '../components/timeline/TimelineCanvas'
import GptButton from '../components/GptButton'
import LoadingSpinner from '../components/LoadingSpinner'
import { BoltIcon } from '@heroicons/react/24/outline'
import { useGptTasks } from '../contexts/GptTaskContext'

/**
 * EventTimelineContainer - Data fetching and state management
 * for the event timeline section on Dashboard.
 */
function EventTimelineContainer({ worldId, direction, showToast }) {
  const navigate = useNavigate()
  const { registerTask } = useGptTasks()
  const [timeline, setTimeline] = useState(null)
  const [loading, setLoading] = useState(false)
  const [extracting, setExtracting] = useState(false)
  const [extractProgress, setExtractProgress] = useState('')

  // Fetch timeline data
  const loadTimeline = useCallback(async () => {
    if (!worldId) return
    try {
      setLoading(true)
      const response = await eventsAPI.getWorldTimeline(worldId)
      setTimeline(response.data?.timeline || null)
    } catch (error) {
      console.error('Error loading timeline:', error)
      showToast?.('Không thể tải timeline sự kiện', 'error')
    } finally {
      setLoading(false)
    }
  }, [worldId, showToast])

  useEffect(() => {
    loadTimeline()
  }, [loadTimeline])

  // Extract events using GPT
  const handleExtractEvents = useCallback(async (force = false) => {
    if (!worldId) return
    try {
      setExtracting(true)
      setExtractProgress('Đang gửi yêu cầu...')

      const response = await eventsAPI.extractFromWorld(worldId, force)
      const taskId = response.data?.task_id

      if (!taskId) {
        throw new Error('Không nhận được task ID')
      }

      setExtractProgress('Đang phân tích câu chuyện...')

      registerTask(taskId, {
        label: 'Trích xuất sự kiện timeline',
        task_type: 'extract_events',
        onComplete: (taskData) => {
          setExtracting(false)
          setExtractProgress('')
          if (taskData.status === 'completed') {
            const totalEvents = taskData.result?.total_events || 0
            showToast?.(`Đã trích xuất ${totalEvents} sự kiện`, 'success')
            loadTimeline()
          }
        }
      })
    } catch (error) {
      setExtracting(false)
      setExtractProgress('')
      console.error('Error extracting events:', error)
      if (error.response?.status === 503) {
        showToast?.('GPT không khả dụng. Vui lòng kiểm tra API key.', 'error')
      } else {
        showToast?.('Lỗi khi trích xuất sự kiện', 'error')
      }
    }
  }, [worldId, showToast, loadTimeline, registerTask])

  // Navigate to story when event is clicked
  const handleEventClick = useCallback((event) => {
    if (event.story_id) {
      navigate(`/stories/${event.story_id}?event=${event.event_id}&position=${event.story_position || 0}`)
    }
  }, [navigate])

  if (loading) {
    return <LoadingSpinner size="sm" />
  }

  const hasEvents = timeline?.years?.length > 0
  const totalEvents = timeline?.years?.reduce((sum, y) => sum + y.events.length, 0) || 0

  return (
    <div>
      {/* Action bar */}
      <div className="flex flex-wrap justify-between items-center gap-2 mb-3">
        <div className="flex items-center gap-2">
          {hasEvents && (
            <span className="badge-outline badge badge-sm">
              {totalEvents} sự kiện · {timeline.years.length} mốc thời gian
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Refresh button */}
          <button
            onClick={() => loadTimeline()}
            className="btn btn-ghost btn-xs"
            disabled={loading}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Tải lại
          </button>

          {/* Extract events (GPT) */}
          <GptButton
            onClick={() => handleExtractEvents(true)}
            loading={extracting}
            loadingText={extractProgress || 'Đang phân tích...'}
            size="xs"
            variant="primary"
          >
                        <BoltIcon className="inline w-3.5 h-3.5" /> Trích xuất sự kiện
          </GptButton>
        </div>
      </div>

      {/* Timeline Canvas */}
      <ReactFlowProvider>
        <TimelineCanvas
          timeline={timeline}
          direction={direction}
          onEventClick={handleEventClick}
          onToggleDirection={() => {}} // Handled by parent
        />
      </ReactFlowProvider>
    </div>
  )
}

export default EventTimelineContainer
