import React from 'react'
import { useTranslation } from 'react-i18next'

function NovelHeader({ title, description, totalWordCount }) {
  const { t } = useTranslation()

  return (
    <div className="mb-6">
      <h1 className="text-3xl font-bold">{title}</h1>
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
