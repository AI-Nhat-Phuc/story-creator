import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { XMarkIcon, PlusIcon, TrashIcon, PencilSquareIcon } from '@heroicons/react/24/outline'
import { authAPI } from '../../services/api'

function SignatureModal({ signatures = [], onClose, onInsert, onSignaturesChange, showToast }) {
  const { t } = useTranslation()
  const [newSig, setNewSig] = useState('')
  const [saving, setSaving] = useState(false)

  const addSignature = async () => {
    const text = newSig.trim()
    if (!text) return
    const updated = [...signatures, text]
    setSaving(true)
    try {
      await authAPI.updateProfile({ signatures: updated })
      onSignaturesChange(updated)
      setNewSig('')
    } catch {
      showToast(t('pages.signatureModal.saveError'), 'error')
    } finally {
      setSaving(false)
    }
  }

  const deleteSignature = async (idx) => {
    const updated = signatures.filter((_, i) => i !== idx)
    try {
      await authAPI.updateProfile({ signatures: updated })
      onSignaturesChange(updated)
    } catch {
      showToast(t('pages.signatureModal.saveError'), 'error')
    }
  }

  return (
    <dialog className="modal modal-open">
      <div className="modal-box max-w-sm">
        <button
          className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2"
          onClick={onClose}
          aria-label={t('common.close')}
        >
          <XMarkIcon className="w-4 h-4" />
        </button>

        <h3 className="font-bold text-lg mb-4">{t('pages.signatureModal.title')}</h3>

        {signatures.length === 0 ? (
          <p className="text-sm opacity-60 text-center py-3">{t('pages.signatureModal.empty')}</p>
        ) : (
          <ul className="space-y-1 mb-4">
            {signatures.map((sig, idx) => (
              <li key={idx} className="flex items-center gap-2 py-1 px-2 rounded hover:bg-base-200">
                <PencilSquareIcon className="w-4 h-4 opacity-40 shrink-0" />
                <span className="flex-1 text-sm truncate">— {sig}</span>
                <button
                  onClick={() => { onInsert(sig); onClose() }}
                  className="btn btn-xs btn-primary shrink-0"
                >
                  {t('pages.signatureModal.insert')}
                </button>
                <button
                  onClick={() => deleteSignature(idx)}
                  className="btn btn-xs btn-ghost text-error shrink-0"
                  aria-label={t('actions.delete')}
                >
                  <TrashIcon className="w-3.5 h-3.5" />
                </button>
              </li>
            ))}
          </ul>
        )}

        <div className="flex gap-2 border-t border-base-300 pt-3">
          <input
            value={newSig}
            onChange={e => setNewSig(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addSignature()}
            placeholder={t('pages.signatureModal.placeholder')}
            maxLength={200}
            className="input input-sm input-bordered flex-1"
          />
          <button
            onClick={addSignature}
            disabled={!newSig.trim() || saving}
            className="btn btn-sm btn-primary"
            aria-label={t('pages.signatureModal.add')}
          >
            {saving
              ? <span className="loading loading-spinner loading-xs" />
              : <PlusIcon className="w-4 h-4" />}
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={onClose} />
    </dialog>
  )
}

export default SignatureModal
