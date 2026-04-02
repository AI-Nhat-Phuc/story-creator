import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'
import NovelHeader from './NovelHeader'
import ChapterList from './ChapterList'
import LoadingSpinner from '../LoadingSpinner'

function NovelView({
  worldId,
  novel,
  chapters,
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
          <ArrowLeftIcon className="w-4 h-4" /> Back to World
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

      <div>
        <h2 className="text-lg font-semibold mb-3">Chapters</h2>
        <ChapterList
          chapters={chapters}
          canReorder={canReorder}
          onReorder={onReorder}
        />
      </div>
    </div>
  )
}

export default NovelView
