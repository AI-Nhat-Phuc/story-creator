import React, { useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

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
  const { t } = useTranslation()
  const titleRef = useRef(null)
  const [titleError, setTitleError] = useState(false)

  const STATUS_BADGE = {
    new:    { cls: 'badge-ghost',   label: t('pages.storyEditor.statusNew')    },
    idle:   { cls: 'badge-warning', label: t('pages.storyEditor.statusDraft')  },
    saving: { cls: '',              label: t('pages.storyEditor.statusSaving') },
    saved:  { cls: '',              label: t('pages.storyEditor.statusSaved')  },
    error:  { cls: 'badge-error',   label: t('pages.storyEditor.statusError')  },
  }
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
    <header className="flex items-center flex-wrap gap-1 px-3 py-1.5 bg-base-100 border-b border-base-300 shrink-0">
      <button
        onClick={onBack}
        className="btn btn-xs btn-ghost h-7 min-h-0 px-2 shrink-0"
        aria-label={t('pages.storyEditor.back')}
      >
        <ArrowLeftIcon className="w-4 h-4" />
      </button>

      <div className="flex-1 flex flex-col min-w-0">
        <input
          ref={titleRef}
          type="text"
          value={title}
          onChange={(e) => handleTitleChange(e.target.value)}
          onFocus={onTitleFocus}
          placeholder={t('pages.storyEditor.titlePlaceholder')}
          className={`input input-ghost input-xs h-7 w-full font-semibold text-sm focus:outline-none focus:bg-base-200 rounded px-2 ${titleError ? 'input-error' : ''}`}
        />
        {titleError && (
          <span className="text-error text-xs px-1">
            {t('pages.storyEditor.titleRequired')}
          </span>
        )}
      </div>

      <div className="flex items-center gap-1 shrink-0">
        {saveStatus === 'saved'
          ? <span className="text-xs text-base-content/50 shrink-0">{badge.label}</span>
          : <span className={`badge ${badge.cls} badge-sm shrink-0`}>{badge.label}</span>
        }

        {wordCount > 0 && (
          <span className="text-xs text-base-content/50 shrink-0 hidden sm:inline">
            {wordCount.toLocaleString()}w · ~{readTime}m
          </span>
        )}

        {saveStatus === 'saved' && !isPublished && title.trim() && wordCount > 0 && (
          <button
            onClick={onPublish}
            className="btn btn-xs btn-success h-7 min-h-0 px-2 shrink-0"
          >
            {t('pages.storyEditor.publish')}
          </button>
        )}
        <button
          onClick={handleSave}
          className="btn btn-xs btn-primary h-7 min-h-0 px-2 shrink-0"
        >
          {t('pages.storyEditor.save')}
        </button>
      </div>
    </header>
  )
}

export default EditorHeader
