import React from 'react'
import GptToolsPanel from './GptToolsPanel'
import DocumentOutline from './DocumentOutline'
import { PencilSquareIcon } from '@heroicons/react/24/outline'

function LeftPanel({ gpt, headings, userSignature, onInsertSignature, panelOpen, onClosePanel }) {
  return (
    <aside className={`flex flex-col gap-5 p-4 w-56 shrink-0 border-r border-base-300 bg-base-100 overflow-y-auto fixed inset-y-0 left-0 z-10 transition-transform duration-200 md:relative md:translate-x-0 md:flex ${panelOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
      <GptToolsPanel {...gpt} />

      <div className="divider my-0" />

      <div className="space-y-2">
        <div className="text-xs font-semibold text-base-content/60 uppercase tracking-wider">
          Signature
        </div>
        <button
          onClick={onInsertSignature}
          disabled={!userSignature}
          className="btn btn-sm btn-outline w-full justify-start gap-2"
          title={userSignature ? `Insert: — ${userSignature}` : 'No signature set'}
        >
          <PencilSquareIcon className="w-4 h-4" />
          {userSignature ? 'Insert sig' : 'No signature'}
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
  )
}

export default LeftPanel
