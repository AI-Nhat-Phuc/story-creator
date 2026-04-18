import React, { useState } from 'react'
import EditorHeader from './EditorHeader'
import LeftPanel from './LeftPanel'
import NovelEditor from './NovelEditor'
import FormattingToolbar from './FormattingToolbar'
import LoadingSpinner from '../LoadingSpinner'
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'

function StoryEditorView({
  editor,
  wordCount,
  readTime,
  headings,
  editorRef,
  gpt,
  activeFormats,
  signatures,
  showSignatureModal,
  onOpenSignatureModal,
  onCloseSignatureModal,
  onSignaturesChange,
  onInsertSignature,
  onTitleChange,
  onContentUpdate,
  onSelectionChange,
  onSave,
  onPublish,
  onBack,
  initialFormat,
  showToast,
}) {
  const [panelOpen, setPanelOpen] = useState(false)

  if (editor.isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-base-100">
      <EditorHeader
        title={editor.title}
        saveStatus={editor.saveStatus}
        wordCount={wordCount}
        readTime={readTime}
        onTitleChange={onTitleChange}
        onSave={onSave}
        onPublish={onPublish}
        isPublished={editor.isPublished}
        onBack={onBack}
        onTitleFocus={() => setPanelOpen(false)}
      />

      <FormattingToolbar editorRef={editorRef} activeFormats={activeFormats} />

      {/* Mobile FAB — opens left panel as bottom sheet */}
      <button
        onClick={() => setPanelOpen(p => !p)}
        className="md:hidden fixed bottom-6 right-4 z-40 btn btn-circle shadow-lg bg-base-100 border border-base-300"
        aria-label="Toggle panel"
      >
        {panelOpen
          ? <XMarkIcon className="w-5 h-5" />
          : <Bars3Icon className="w-5 h-5" />}
      </button>

      <div className="flex flex-1 overflow-hidden">
        <LeftPanel
          gpt={gpt}
          headings={headings}
          signatures={signatures}
          showSignatureModal={showSignatureModal}
          onOpenSignatureModal={onOpenSignatureModal}
          onCloseSignatureModal={onCloseSignatureModal}
          onSignaturesChange={onSignaturesChange}
          onInsertSignature={onInsertSignature}
          panelOpen={panelOpen}
          onClosePanel={() => setPanelOpen(false)}
          showToast={showToast}
        />

        <main
          className="flex-1 overflow-y-auto cursor-text"
          onFocus={() => setPanelOpen(false)}
          onClick={(e) => {
            if (!e.target.closest('.ProseMirror')) {
              const pm = e.currentTarget.querySelector('.ProseMirror')
              pm?.focus()
              editorRef.current?.commands.focus('end')
            }
          }}
        >
          <NovelEditor
            initialContent={editor.content}
            format={initialFormat}
            onUpdate={onContentUpdate}
            onSelectionChange={onSelectionChange}
            editorRef={editorRef}
          />
        </main>
      </div>
    </div>
  )
}

export default StoryEditorView
