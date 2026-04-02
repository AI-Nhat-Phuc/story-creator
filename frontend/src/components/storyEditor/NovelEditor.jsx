import React from 'react'
import { Editor } from 'novel'

function NovelEditor({ initialContent, format, onUpdate, editorRef }) {
  // For plain/markdown stories, wrap as TipTap doc with plain text paragraph
  const defaultValue =
    format === 'html'
      ? initialContent || ''
      : {
          type: 'doc',
          content: [
            {
              type: 'paragraph',
              content: initialContent ? [{ type: 'text', text: initialContent }] : [],
            },
          ],
        }

  return (
    <Editor
      defaultValue={defaultValue}
      disableLocalStorage={true}
      onUpdate={({ editor }) => {
        editorRef.current = editor
        const { from, to } = editor.state.selection
        const selectionLength = editor.state.doc.textBetween(from, to, ' ').length
        onUpdate({ html: editor.getHTML(), editor, selectionLength })
      }}
      className="min-h-full"
    />
  )
}

export default NovelEditor
