'use client'

import React from 'react'
import { useTranslation } from 'react-i18next'

function UnsavedChangesModal({ onSave, onDiscard, onCancel }) {
  const { t } = useTranslation()

  return (
    <dialog className="modal modal-open">
      <div className="modal-box max-w-sm">
        <h3 className="font-bold text-lg">{t('pages.storyEditor.unsavedTitle')}</h3>
        <p className="py-3 text-sm opacity-70">{t('pages.storyEditor.unsavedMessage')}</p>
        <div className="modal-action gap-2">
          <button onClick={onCancel} className="btn btn-ghost btn-sm">
            {t('common.cancel')}
          </button>
          <button onClick={onDiscard} className="btn btn-error btn-outline btn-sm">
            {t('pages.storyEditor.discard')}
          </button>
          <button onClick={onSave} className="btn btn-primary btn-sm">
            {t('pages.storyEditor.saveDraft')}
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={onCancel} />
    </dialog>
  )
}

export default UnsavedChangesModal
