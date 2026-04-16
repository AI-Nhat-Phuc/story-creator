import React, { useRef, useState } from 'react'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'
import StoryTimeSelector from './StoryTimeSelector'

const STATUS_BADGE = {
  new:     { cls: 'badge-ghost',    label: 'New'      },
  idle:    { cls: 'badge-warning',  label: 'Draft'    },
  saving:  { cls: '',               label: 'Saving…'  },
  saved:   { cls: '',               label: 'Saved'    },
  error:   { cls: 'badge-error',    label: 'Error'    },
}

function EditorHeader({
  title,
  saveStatus,
  wordCount,
  readTime,
  isPublished,
  timeIndex,
  worldCalendar,
  onTitleChange,
  onSave,
  onPublish,
  onBack,
  onTitleFocus,
  onTimeIndexChange,
}) {
  const titleRef = useRef(null)
  const [titleError, setTitleError] = useState(false)
  const badge = STATUS_BADGE[saveStatus] || STATUS_BADGE.idle

  const handleSave = () => {
    if (!title.trim()) {
      setTitleError(true)
      titleRef.current?.focus()
      return
    }
    setTitleError(false)
    onSave()
  }

  const handleTitleChange = (value) => {
    if (value.trim()) setTitleError(false)
    onTitleChange(value)
  }

  const showTimeSelector = onTimeIndexChange !== undefined

  return (
    <header className="flex flex-col gap-1 px-4 py-2 bg-base-200 border-b border-base-300">
      {/* Row 1: back button + title input */}
      <div className="flex items-center gap-2 min-w-0">
        <button
          onClick={onBack}
          className="btn btn-ghost btn-sm btn-square shrink-0"
          aria-label="Back"
        >
          <ArrowLeftIcon className="w-5 h-5" />
        </button>

        <div className="flex-1 flex flex-col min-w-0">
          <input
            ref={titleRef}
            type="text"
            value={title}
            onChange={(e) => handleTitleChange(e.target.value)}
            onFocus={onTitleFocus}
            placeholder="Tiêu đề câu chuyện…"
            className={`input input-ghost input-sm w-full font-semibold text-base focus:outline-none focus:bg-base-100 rounded ${titleError ? 'input-error' : ''}`}
          />
          {titleError && (
            <span className="text-error text-xs px-1">Vui lòng nhập tiêu đề</span>
          )}
        </div>
      </div>

      {/* Row 2: time selector (under title) + status + action buttons (incl. publish) */}
      <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap pl-10">
        {showTimeSelector && (
          <StoryTimeSelector
            compact
            timeIndex={timeIndex ?? 0}
            onChange={onTimeIndexChange}
            worldCalendar={worldCalendar}
          />
        )}

        <div className="flex items-center gap-2 ml-auto shrink-0">
          {saveStatus === 'saved'
            ? <span className="text-xs text-base-content/50 shrink-0">{badge.label}</span>
            : <span className={`badge ${badge.cls} badge-sm shrink-0`}>{badge.label}</span>
          }

          {wordCount > 0 && (
            <span className="text-xs text-base-content/50 shrink-0 hidden sm:block">
              {wordCount.toLocaleString()}w · ~{readTime}m
            </span>
          )}

          {saveStatus === 'saved' && !isPublished && title.trim() && wordCount > 0 && (
            <button onClick={onPublish} className="btn btn-success btn-sm shrink-0">
              Xuất bản
            </button>
          )}
          <button onClick={handleSave} className="btn btn-primary btn-sm shrink-0">
            Lưu
          </button>
        </div>
      </div>
    </header>
  )
}

export default EditorHeader
