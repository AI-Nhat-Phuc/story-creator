import React from 'react'
import EditorHeader from './EditorHeader'
import LeftPanel from './LeftPanel'
import NovelEditor from './NovelEditor'
import LoadingSpinner from '../LoadingSpinner'

function StoryEditorView({
  editor,
  wordCount,
  readTime,
  headings,
  editorRef,
  gpt,
  userSignature,
  onTitleChange,
  onContentUpdate,
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

      <div className="flex flex-1 overflow-hidden">
        <LeftPanel
          gpt={gpt}
          headings={headings}
          userSignature={userSignature}
          onInsertSignature={onInsertSignature}
        />

        <main className="flex-1 overflow-y-auto">
          <NovelEditor
            initialContent={editor.content}
            format={initialFormat}
            onUpdate={onContentUpdate}
            editorRef={editorRef}
          />
        </main>
      </div>
    </div>
  )
}

export default StoryEditorView
