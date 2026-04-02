import React from 'react'
import { PencilIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'

function NovelHeader({
  title,
  description,
  totalWordCount,
  canEdit,
  editing,
  metaForm,
  saving,
  onEdit,
  onCancel,
  onSave,
  onFormChange,
}) {
  if (editing) {
    return (
      <div className="space-y-3 mb-6">
        <input
          type="text"
          value={metaForm.title}
          onChange={(e) => onFormChange('title', e.target.value)}
          className="input input-bordered w-full text-2xl font-bold"
          placeholder="Novel title"
        />
        <textarea
          value={metaForm.description}
          onChange={(e) => onFormChange('description', e.target.value)}
          className="textarea textarea-bordered w-full"
          rows={3}
          placeholder="Novel description…"
        />
        <div className="flex gap-2">
          <button onClick={onSave} disabled={saving} className="btn btn-primary btn-sm gap-1">
            <CheckIcon className="w-4 h-4" />
            {saving ? <span className="loading loading-spinner loading-xs" /> : 'Save'}
          </button>
          <button onClick={onCancel} className="btn btn-ghost btn-sm gap-1">
            <XMarkIcon className="w-4 h-4" /> Cancel
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="mb-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">{title}</h1>
          {description && <p className="text-base-content/70 mt-1">{description}</p>}
        </div>
        {canEdit && (
          <button onClick={onEdit} className="btn btn-ghost btn-sm btn-square shrink-0">
            <PencilIcon className="w-4 h-4" />
          </button>
        )}
      </div>
      {totalWordCount > 0 && (
        <p className="text-sm text-base-content/50 mt-2">
          {totalWordCount.toLocaleString()} words total
        </p>
      )}
    </div>
  )
}

export default NovelHeader
