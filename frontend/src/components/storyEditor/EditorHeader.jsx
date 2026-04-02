import React from 'react'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

const STATUS_BADGE = {
  idle:    { cls: 'badge-warning',  label: 'Draft'    },
  saving:  { cls: 'badge-info',     label: 'Saving…'  },
  saved:   { cls: 'badge-success',  label: 'Saved'    },
  error:   { cls: 'badge-error',    label: 'Error'    },
}

function EditorHeader({
  title,
  saveStatus,
  isPublished,
  wordCount,
  readTime,
  onTitleChange,
  onSave,
  onPublish,
  onBack,
}) {
  const badge = STATUS_BADGE[saveStatus] || STATUS_BADGE.idle

  return (
    <header className="flex items-center gap-3 px-4 py-2 bg-base-200 border-b border-base-300 min-h-[52px]">
      <button
        onClick={onBack}
        className="btn btn-ghost btn-sm btn-square"
        aria-label="Back"
      >
        <ArrowLeftIcon className="w-5 h-5" />
      </button>

      <input
        type="text"
        value={title}
        onChange={(e) => onTitleChange(e.target.value)}
        placeholder="Story title…"
        className="input input-ghost input-sm flex-1 font-semibold text-base focus:outline-none focus:bg-base-100 rounded"
      />

      <span className={`badge ${badge.cls} badge-sm shrink-0`}>{badge.label}</span>

      {wordCount > 0 && (
        <span className="text-xs text-base-content/50 shrink-0 hidden sm:block">
          {wordCount.toLocaleString()}w · ~{readTime}m
        </span>
      )}

      {isPublished
        ? <span className="badge badge-success badge-sm shrink-0">Published</span>
        : <button onClick={onPublish} className="btn btn-primary btn-sm shrink-0">Publish</button>
      }
    </header>
  )
}

export default EditorHeader
