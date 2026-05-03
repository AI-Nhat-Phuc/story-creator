'use client'

import React, { useRef } from 'react'
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

  const STATUS_TEXT = {
    new:    { cls: 'text-base-content/40',          label: t('pages.storyEditor.statusNew')    },
    idle:   { cls: 'text-accent font-medium',        label: t('pages.storyEditor.statusDraft')  },
    saving: { cls: 'text-primary/60 italic',        label: t('pages.storyEditor.statusSaving') },
    saved:  { cls: 'text-base-content/50',          label: t('pages.storyEditor.statusSaved')  },
    error:  { cls: 'text-error font-medium',        label: t('pages.storyEditor.statusError')  },
  }
  const badge = STATUS_TEXT[saveStatus] || STATUS_TEXT.idle

  return (
    <header className="sticky top-0 z-10 flex items-center flex-wrap gap-1 px-3 py-1.5 bg-base-100 border-b border-base-300 shrink-0">
      <button
        onClick={onBack}
        className="btn btn-xs btn-ghost h-7 min-h-0 px-2 shrink-0"
        aria-label={t('pages.storyEditor.back')}
      >
        <ArrowLeftIcon className="w-4 h-4" />
      </button>

      <div className="flex-1 min-w-0">
        <input
          ref={titleRef}
          type="text"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
          onFocus={onTitleFocus}
          placeholder={t('pages.storyEditor.titlePlaceholder')}
          className="bg-transparent border-0 outline-none h-7 w-full font-semibold text-sm px-2 rounded placeholder:text-base-content/30 hover:bg-base-200/60 focus:bg-base-200 transition-colors"
        />
      </div>

      <div className="flex items-center gap-1 shrink-0">
        <span className={`text-xs shrink-0 ${badge.cls}`}>{badge.label}</span>

        {wordCount > 0 && (
          <span className="text-xs text-base-content/50 shrink-0 hidden sm:inline">
            {wordCount.toLocaleString()}w · ~{readTime}m
          </span>
        )}

        {saveStatus === 'saved' && !isPublished && wordCount > 0 && (
          <button
            onClick={onPublish}
            className="btn btn-xs btn-outline btn-primary h-7 min-h-0 px-2 shrink-0"
          >
            {t('pages.storyEditor.publish')}
          </button>
        )}
        <button
          onClick={onSave}
          className="btn btn-xs btn-primary h-7 min-h-0 px-2 shrink-0"
        >
          {t('pages.storyEditor.save')}
        </button>
      </div>
    </header>
  )
}

export default EditorHeader
