import React from 'react'
import { useTranslation } from 'react-i18next'
import { UserIcon } from '@heroicons/react/24/outline'

function NovelHeader({ title, description, totalWordCount, authorName }) {
  const { t } = useTranslation()

  return (
    <div className="mb-6">
      <h1 className="text-3xl font-bold">{title}</h1>
      {authorName && (
        <p className="flex items-center gap-1.5 text-base-content/60 text-sm mt-1">
          <UserIcon className="w-4 h-4" />
          <span>{authorName}</span>
        </p>
      )}
      {description && (
        <p className="text-base-content/70 mt-1">{description}</p>
      )}
      {totalWordCount > 0 && (
        <p className="text-sm text-base-content/50 mt-2">
          {t('pages.novel.totalWords', { words: totalWordCount.toLocaleString() })}
        </p>
      )}
    </div>
  )
}

export default NovelHeader
