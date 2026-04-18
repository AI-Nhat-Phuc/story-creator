import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'

function TitleSuggestionModal({ suggestion, onConfirm, onSkip, onCancel }) {
  const { t } = useTranslation()
  const [title, setTitle] = useState(suggestion || '')

  return (
    <dialog className="modal modal-open">
      <div className="modal-box max-w-sm">
        <h3 className="font-bold text-lg">{t('pages.storyEditor.titleSuggestTitle')}</h3>
        <p className="text-sm opacity-60 mb-3 mt-1">{t('pages.storyEditor.titleSuggestMessage')}</p>
        <input
          value={title}
          onChange={e => setTitle(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && title.trim()) onConfirm(title.trim()) }}
          placeholder={t('pages.storyEditor.titleSuggestPlaceholder')}
          className="input input-bordered w-full"
          autoFocus
          maxLength={200}
        />
        <div className="modal-action gap-2 flex-wrap">
          <button onClick={onCancel} className="btn btn-ghost btn-sm">
            {t('common.cancel')}
          </button>
          <button onClick={onSkip} className="btn btn-ghost btn-sm">
            {t('pages.storyEditor.titleSuggestSkip')}
          </button>
          <button
            onClick={() => onConfirm(title.trim())}
            disabled={!title.trim()}
            className="btn btn-primary btn-sm"
          >
            {t('common.save')}
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={onCancel} />
    </dialog>
  )
}

export default TitleSuggestionModal
