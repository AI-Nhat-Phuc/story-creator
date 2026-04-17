import React, { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'
import NovelHeader from './NovelHeader'
import ChapterList from './ChapterList'
import NovelContentStream from './NovelContentStream'
import LoadingSpinner from '../LoadingSpinner'

function NovelView({
  worldId,
  novel,
  chapters,
  contentBlocks,
  hasMore,
  isLoadingMore,
  onLoadMore,
  totalWordCount,
  isLoading,
  canEdit,
  canReorder,
  editingMeta,
  metaForm,
  savingMeta,
  onEditMeta,
  onCancelMeta,
  onSaveMeta,
  onMetaFormChange,
  onReorder,
}) {
  const { t } = useTranslation()
  const sentinelRef = useRef(null)

  // Infinite-scroll: observe a sentinel element near the bottom. The
  // container is responsible for de-duplicating concurrent loads; we only
  // need to wire the observer whenever `hasMore` changes.
  useEffect(() => {
    if (!hasMore || !sentinelRef.current) return
    const el = sentinelRef.current
    const observer = new IntersectionObserver((entries) => {
      if (entries.some(e => e.isIntersecting)) {
        onLoadMore()
      }
    }, { rootMargin: '400px' })
    observer.observe(el)
    return () => observer.disconnect()
  }, [hasMore, onLoadMore])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-6">
        <Link to={`/worlds/${worldId}`} className="btn btn-ghost btn-sm gap-1">
          <ArrowLeftIcon className="w-4 h-4" /> {t('common.backToWorld')}
        </Link>
      </div>

      <NovelHeader
        title={novel?.title || ''}
        description={novel?.description || ''}
        totalWordCount={totalWordCount}
        canEdit={canEdit}
        editing={editingMeta}
        metaForm={metaForm}
        saving={savingMeta}
        onEdit={onEditMeta}
        onCancel={onCancelMeta}
        onSave={onSaveMeta}
        onFormChange={onMetaFormChange}
      />

      {contentBlocks && contentBlocks.length > 0 ? (
        <>
          <NovelContentStream blocks={contentBlocks} />
          <div ref={sentinelRef} className="h-6" />
          {isLoadingMore && (
            <div className="flex items-center justify-center py-6 opacity-70">
              <LoadingSpinner />
              <span className="ml-2">{t('pages.novel.loadingMore')}</span>
            </div>
          )}
          {!hasMore && contentBlocks.length > 0 && (
            <p className="text-center opacity-60 py-6 italic">
              {t('pages.novel.endOfNovel')}
            </p>
          )}
        </>
      ) : (
        <p className="text-center opacity-60 py-8 italic">
          {t('pages.novel.emptyWorld')}
        </p>
      )}

      {chapters && chapters.length > 0 && (
        <details className="mt-10 collapse collapse-arrow bg-base-200">
          <summary className="collapse-title text-lg font-semibold">Chapters</summary>
          <div className="collapse-content">
            <ChapterList
              chapters={chapters}
              canReorder={canReorder}
              onReorder={onReorder}
            />
          </div>
        </details>
      )}
    </div>
  )
}

export default NovelView
