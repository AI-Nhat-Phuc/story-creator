import React, { useRef, useState } from 'react'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

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
  onTitleChange,
  onSave,
  onPublish,
  onBack,
  onTitleFocus,
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

  return (
    <header className="flex flex-col sm:flex-row sm:items-center gap-1 px-4 py-2 bg-base-200 border-b border-base-300">
      {/* Row 1: back button + title input */}
      <div className="flex items-center gap-2 flex-1 min-w-0">
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

      {/* Row 2 on mobile / inline on desktop: status + action buttons */}
      <div className="flex items-center gap-2 justify-end">
        {saveStatus === 'saved'
          ? <span className="text-xs text-base-content/50 shrink-0">{badge.label}</span>
          : <span className={`badge ${badge.cls} badge-sm shrink-0`}>{badge.label}</span>
        }

        {wordCount > 0 && (
          <span className="text-xs text-base-content/50 shrink-0 hidden sm:block">
            {wordCount.toLocaleString()}w · ~{readTime}m
          </span>
        )}

        {saveStatus !== 'new' && !isPublished && (
          <button onClick={onPublish} className="btn btn-success btn-sm shrink-0">
            Xuất bản
          </button>
        )}
        <button onClick={handleSave} className="btn btn-primary btn-sm shrink-0">
          Lưu
        </button>
      </div>
    </header>
  )
}

export default EditorHeader
