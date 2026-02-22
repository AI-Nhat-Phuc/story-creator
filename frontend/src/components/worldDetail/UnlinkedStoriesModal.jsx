import React, { useState } from 'react'
import Modal from '../Modal'
import {
  MagnifyingGlassIcon,
  BookOpenIcon,
  ClockIcon,
  UserIcon,
  MapPinIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import { OpenAILogo } from '../GptButton'

const MAX_BATCH = 3

/**
 * Modal showing unlinked stories with batch analyze option.
 * Groups stories by time period and allows GPT analysis with context carry-over.
 * Max 3 stories per batch. Each story also has an individual analyze button.
 */
export default function UnlinkedStoriesModal({
  open,
  onClose,
  unlinkedStories = [],
  getTimelineLabel,
  batchAnalyzing,
  batchProgress,
  batchResult,
  onBatchAnalyze,
}) {
  const [selected, setSelected] = useState(new Set())

  const toggleSelect = (storyId) => {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(storyId)) {
        next.delete(storyId)
      } else if (next.size < MAX_BATCH) {
        next.add(storyId)
      }
      return next
    })
  }

  const selectAll = () => {
    // Select first MAX_BATCH stories (sorted by time)
    const ids = unlinkedStories.slice(0, MAX_BATCH).map(s => s.story_id)
    setSelected(new Set(ids))
  }

  const clearSelection = () => setSelected(new Set())

  // Group stories by time_index
  const grouped = {}
  for (const story of unlinkedStories) {
    const key = story.time_index ?? 0
    if (!grouped[key]) grouped[key] = []
    grouped[key].push(story)
  }
  const sortedKeys = Object.keys(grouped).sort((a, b) => Number(a) - Number(b))

  // Build a timeline label from a fake story object for grouping display
  const getGroupLabel = (timeIndex) => {
    const num = Number(timeIndex)
    if (num === 0) return 'Không xác định'
    if (getTimelineLabel) {
      return getTimelineLabel({ time_index: num, metadata: { world_time: { year: num } } })
    }
    return `Thời kỳ ${num}`
  }

  const isCompleted = batchResult && !batchAnalyzing
  // Check which stories were already analyzed in this session
  const analyzedIds = new Set(
    (batchResult?.analyzed_stories || []).map(s => s.story_id)
  )

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Câu chuyện chưa liên kết"
      className="max-w-2xl"
    >
      {/* Explanation */}
      <div className="flex items-start gap-2 bg-warning/10 mb-4 p-3 rounded-lg text-warning-content">
        <ExclamationTriangleIcon className="flex-shrink-0 mt-0.5 w-5 h-5 text-warning" />
        <p className="text-sm">
          Các câu chuyện dưới đây chưa có nhân vật hoặc địa điểm nào được liên kết.
          Chọn tối đa {MAX_BATCH} câu chuyện để phân tích cùng lúc, hoặc phân tích từng câu chuyện.
        </p>
      </div>

      {/* Batch analyze result */}
      {batchResult && (
        <div className="bg-success/10 mb-4 p-3 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircleIcon className="w-5 h-5 text-success" />
            <span className="font-semibold text-success">{batchResult.message}</span>
          </div>
          <div className="flex gap-4 text-sm">
            <span className="flex items-center gap-1">
              <UserIcon className="w-4 h-4" /> {batchResult.total_characters_found} nhân vật
            </span>
            <span className="flex items-center gap-1">
              <MapPinIcon className="w-4 h-4" /> {batchResult.total_locations_found} địa điểm
            </span>
            {batchResult.linked_count > 0 && (
              <span className="flex items-center gap-1 font-medium text-primary">
                🔗 {batchResult.linked_count} câu chuyện đã liên kết
              </span>
            )}
          </div>
          {/* Per-story results */}
          {batchResult.analyzed_stories && batchResult.analyzed_stories.length > 0 && (
            <div className="space-y-2 mt-3">
              {batchResult.analyzed_stories.map((s) => (
                <div key={s.story_id} className="bg-base-100 p-2 rounded text-xs">
                  <span className="font-semibold">{s.story_title}</span>
                  <span className="opacity-60 ml-2">
                    {s.characters?.length || 0} nhân vật, {s.locations?.length || 0} địa điểm
                  </span>
                  {s.characters?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {s.characters.map((c, i) => (
                        <span key={i} className="badge-outline badge badge-sm">
                          <UserIcon className="mr-1 w-3 h-3" />{c.name}
                        </span>
                      ))}
                    </div>
                  )}
                  {s.locations?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {s.locations.map((l, i) => (
                        <span key={i} className="badge-outline badge badge-sm badge-secondary">
                          <MapPinIcon className="mr-1 w-3 h-3" />{l.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Progress indicator */}
      {batchAnalyzing && batchProgress && (
        <div className="mb-4">
          <div className="flex justify-between mb-1 text-sm">
            <span>
              Đang phân tích: <span className="font-semibold">{batchProgress.current_story}</span>
            </span>
            <span>{batchProgress.progress}/{batchProgress.total}</span>
          </div>
          <progress
            className="w-full progress progress-primary"
            value={batchProgress.progress}
            max={batchProgress.total}
          />
        </div>
      )}

      {/* Selection controls */}
      {!isCompleted && !batchAnalyzing && (
        <div className="flex justify-between items-center mb-3">
          <div className="opacity-70 text-sm">
            Đã chọn: <span className="font-semibold">{selected.size}/{MAX_BATCH}</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={selectAll}
              className="btn btn-ghost btn-xs"
              disabled={unlinkedStories.length === 0}
            >
              Chọn {Math.min(MAX_BATCH, unlinkedStories.length)}
            </button>
            {selected.size > 0 && (
              <button onClick={clearSelection} className="btn btn-ghost btn-xs">
                Bỏ chọn
              </button>
            )}
          </div>
        </div>
      )}

      {/* Story list grouped by time */}
      {!isCompleted && (
        <div className="space-y-4 pr-1 max-h-[400px] overflow-y-auto">
          {sortedKeys.map((timeKey) => (
            <div key={timeKey}>
              <div className="flex items-center gap-2 mb-2">
                <ClockIcon className="w-4 h-4 text-primary" />
                <h3 className="font-semibold text-primary text-sm">
                  {getGroupLabel(timeKey)}
                </h3>
                <span className="badge badge-sm badge-ghost">
                  {grouped[timeKey].length} câu chuyện
                </span>
              </div>
              <div className="space-y-2 pl-6">
                {grouped[timeKey].map((story) => {
                  const isAnalyzed = analyzedIds.has(story.story_id)
                  const isSelected = selected.has(story.story_id)
                  const canSelect = isSelected || selected.size < MAX_BATCH

                  return (
                    <div
                      key={story.story_id}
                      className={`flex items-start gap-3 p-2 rounded-lg transition-colors
                        ${isAnalyzed ? 'bg-success/10 opacity-60' : isSelected ? 'bg-primary/10 ring-1 ring-primary/30' : 'bg-base-200/50 hover:bg-base-200'}`}
                    >
                      {/* Checkbox */}
                      {!batchAnalyzing && !isAnalyzed && (
                        <input
                          type="checkbox"
                          className="flex-shrink-0 mt-0.5 checkbox checkbox-primary checkbox-sm"
                          checked={isSelected}
                          disabled={!canSelect}
                          onChange={() => toggleSelect(story.story_id)}
                        />
                      )}
                      {isAnalyzed && (
                        <CheckCircleIcon className="flex-shrink-0 mt-0.5 w-5 h-5 text-success" />
                      )}

                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate">{story.title}</p>
                        {story.description && (
                          <p className="opacity-60 mt-0.5 text-xs line-clamp-2">
                            {story.description}
                          </p>
                        )}
                      </div>

                      {/* Per-story analyze button */}
                      {!batchAnalyzing && !isAnalyzed && (
                        <button
                          onClick={() => onBatchAnalyze([story.story_id])}
                          className="flex-shrink-0 gap-1 btn btn-ghost btn-xs"
                          title="Phân tích câu chuyện này"
                        >
                          <OpenAILogo size={14} />
                          <MagnifyingGlassIcon className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end gap-2 mt-5 pt-4 border-base-300 border-t">
        {isCompleted ? (
          <button onClick={onClose} className="btn btn-primary btn-sm">
            Đóng & Làm mới
          </button>
        ) : (
          <>
            <button onClick={onClose} className="btn btn-ghost btn-sm" disabled={batchAnalyzing}>
              {batchResult ? 'Đóng & Làm mới' : 'Hủy'}
            </button>
            {selected.size > 0 && (
              <button
                onClick={() => onBatchAnalyze([...selected])}
                className={`btn btn-primary btn-sm gap-2 ${batchAnalyzing ? 'loading' : ''}`}
                disabled={batchAnalyzing}
              >
                {!batchAnalyzing && (
                  <>
                    <OpenAILogo size={16} />
                    <MagnifyingGlassIcon className="w-4 h-4" />
                  </>
                )}
                {batchAnalyzing
                  ? 'Đang phân tích...'
                  : `Phân tích ${selected.size} câu chuyện`
                }
              </button>
            )}
          </>
        )}
      </div>
    </Modal>
  )
}
