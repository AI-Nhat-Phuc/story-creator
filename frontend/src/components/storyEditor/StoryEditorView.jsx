import React, { useState } from 'react'
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'
import EditorHeader from './EditorHeader'
import LeftPanel from './LeftPanel'
import NovelEditor from './NovelEditor'
import FormattingToolbar from './FormattingToolbar'
import LoadingSpinner from '../LoadingSpinner'

function StoryEditorView({
  editor,
  wordCount,
  readTime,
  headings,
  editorRef,
  gpt,
  activeFormats,
  userSignature,
  onTitleChange,
  onContentUpdate,
  onSelectionChange,
  onSave,
  onBack,
  onInsertSignature,
  initialFormat,
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
        onBack={onBack}
      />

      <FormattingToolbar editorRef={editorRef} activeFormats={activeFormats} />

      <div className="flex flex-1 overflow-hidden">
        <LeftPanel
          gpt={gpt}
          headings={headings}
          userSignature={userSignature}
          onInsertSignature={onInsertSignature}
          panelOpen={panelOpen}
          onClosePanel={() => setPanelOpen(false)}
        />

        <main
          className="flex-1 overflow-y-auto cursor-text"
          onClick={(e) => {
            // Focus editor when clicking outside the actual ProseMirror content area
            if (!e.target.closest('.ProseMirror')) {
              // Direct DOM focus avoids TipTap's internal setTimeout delay
              const pm = e.currentTarget.querySelector('.ProseMirror')
              pm?.focus()
              editorRef.current?.commands.focus('end')
            }
          }}
        >
          <button
            className="md:hidden fixed bottom-4 left-4 z-20 btn btn-circle btn-sm btn-primary shadow-lg"
            onClick={() => setPanelOpen(p => !p)}
            aria-label="Toggle sidebar"
          >
            {panelOpen ? <XMarkIcon className="w-4 h-4" /> : <Bars3Icon className="w-4 h-4" />}
          </button>
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
