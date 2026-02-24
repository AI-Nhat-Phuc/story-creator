import { useState, useEffect, useCallback, useRef } from 'react'
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

  // Use ref for showToast to avoid re-creating callbacks on every render
  const showToastRef = useRef(showToast)
  useEffect(() => { showToastRef.current = showToast }, [showToast])

  // Fetch timeline data — only depends on worldId
  // silent=true suppresses error toast (used for initial auto-load)
  const loadTimeline = useCallback(async (silent = false) => {
    if (!worldId) return
    try {
      setLoading(true)
      const response = await eventsAPI.getWorldTimeline(worldId)
      setTimeline(response.data?.timeline || null)
    } catch (error) {
      console.error('Error loading timeline:', error)
      // Don't show error toast on initial load — world may not have events yet
      if (!silent) {
        showToastRef.current?.('Không thể tải timeline sự kiện', 'error')
      }
      setTimeline(null)
    } finally {
      setLoading(false)
    }
  }, [worldId])

  // Initial load — silent (no error toast)
  useEffect(() => {
    loadTimeline(true)
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
            showToastRef.current?.(`Đã trích xuất ${totalEvents} sự kiện`, 'success')
            loadTimeline()
          }
        }
      })
    } catch (error) {
      setExtracting(false)
      setExtractProgress('')
      console.error('Error extracting events:', error)
      if (error.response?.status === 503) {
        showToastRef.current?.('GPT không khả dụng. Vui lòng kiểm tra API key.', 'error')
      } else {
        showToastRef.current?.('Lỗi khi trích xuất sự kiện', 'error')
      }
    }
  }, [worldId, loadTimeline, registerTask])

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

  // No events yet — show empty state with extract prompt
  if (!hasEvents && !loading) {
    return (
      <div className="flex flex-col justify-center items-center py-12 text-base-content/50">
        <svg xmlns="http://www.w3.org/2000/svg" className="opacity-30 mb-3 w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <p className="mb-1 font-semibold">Chưa có sự kiện nào</p>
        <p className="mb-4 text-sm">Hãy trích xuất sự kiện từ các câu chuyện bằng GPT</p>
        <GptButton
          onClick={() => handleExtractEvents(true)}
          loading={extracting}
          loadingText={extractProgress || 'Đang phân tích...'}
          size="sm"
          variant="primary"
        >
          <BoltIcon className="inline w-4 h-4" /> Trích xuất sự kiện
        </GptButton>
      </div>
    )
  }

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
