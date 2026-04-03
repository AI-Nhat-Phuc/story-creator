import React from 'react'
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
  onPublish,
  onBack,
  onInsertSignature,
  initialFormat,
}) {
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
        isPublished={editor.isPublished}
        wordCount={wordCount}
        readTime={readTime}
        onTitleChange={onTitleChange}
        onSave={onSave}
        onPublish={onPublish}
        onBack={onBack}
      />

      <FormattingToolbar editorRef={editorRef} activeFormats={activeFormats} />

      <div className="flex flex-1 overflow-hidden">
        <LeftPanel
          gpt={gpt}
          headings={headings}
          userSignature={userSignature}
          onInsertSignature={onInsertSignature}
        />

        <main
          className="flex-1 overflow-y-auto cursor-text"
          onClick={(e) => {
            // Focus editor at end when clicking on empty area below content
            if (e.target === e.currentTarget) {
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
