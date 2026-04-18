import React from 'react'
import { useTranslation } from 'react-i18next'
import GptToolsPanel from './GptToolsPanel'
import DocumentOutline from './DocumentOutline'
import SignatureModal from './SignatureModal'
import { PencilSquareIcon } from '@heroicons/react/24/outline'

function LeftPanel({
  gpt,
  headings,
  signatures,
  showSignatureModal,
  onOpenSignatureModal,
  onCloseSignatureModal,
  onSignaturesChange,
  onInsertSignature,
  panelOpen,
  onClosePanel,
  showToast,
}) {
  const { t } = useTranslation()

  return (
    <>
      {/* Mobile backdrop */}
      {panelOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-10"
          onClick={onClosePanel}
        />
      )}

      <aside className={[
        'flex flex-col gap-5 p-4 bg-base-100 overflow-y-auto',
        'fixed bottom-0 left-0 right-0 z-20 max-h-[75vh]',
        'rounded-t-2xl border-t border-base-300 shadow-2xl',
        'transition-transform duration-300 ease-out',
        panelOpen ? 'translate-y-0' : 'translate-y-full',
        'md:relative md:inset-auto md:max-h-none md:h-auto',
        'md:rounded-none md:border-t-0 md:border-r md:shadow-none',
        'md:translate-y-0 md:w-56 md:shrink-0',
      ].join(' ')}>

        {/* Mobile drag handle */}
        <div className="md:hidden flex justify-center -mt-1 mb-1 shrink-0">
          <div className="w-10 h-1 rounded-full bg-base-300" />
        </div>

        <GptToolsPanel {...gpt} />

        <div className="divider my-0" />

        <div className="space-y-2">
          <div className="text-xs font-semibold text-base-content/60 uppercase tracking-wider">
            {t('pages.signatureModal.title')}
          </div>
          <button
            onClick={onOpenSignatureModal}
            className="btn btn-sm btn-outline w-full justify-start gap-2"
          >
            <PencilSquareIcon className="w-4 h-4" />
            {signatures.length > 0
              ? t('pages.signatureModal.manage')
              : t('pages.signatureModal.noSignature')}
          </button>
        </div>

        <div className="divider my-0" />

        <div className="space-y-2">
          <div className="text-xs font-semibold text-base-content/60 uppercase tracking-wider">
            Outline
          </div>
          <DocumentOutline headings={headings} />
        </div>
      </aside>

      {showSignatureModal && (
        <SignatureModal
          signatures={signatures}
          onClose={onCloseSignatureModal}
          onInsert={onInsertSignature}
          onSignaturesChange={onSignaturesChange}
          showToast={showToast}
        />
      )}
    </>
  )
}

export default LeftPanel
