import React from 'react'
import { EditorRoot, EditorContent, StarterKit, Placeholder } from 'novel'

const extensions = [StarterKit, Placeholder]

function NovelEditor({ initialContent, format, onUpdate, onSelectionChange, editorRef }) {
  // For plain/markdown stories, wrap as TipTap doc with plain text paragraph
  const defaultContent =
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
    <EditorRoot>
      <EditorContent
        initialContent={defaultContent}
        extensions={extensions}
        onCreate={({ editor }) => {
          editorRef.current = editor
          // Track selection changes separately from content changes
          editor.on('selectionUpdate', ({ editor: e }) => {
            const { from, to } = e.state.selection
            const selectionLength = e.state.doc.textBetween(from, to, ' ').length
            onSelectionChange?.({ selectionLength, editor: e })
          })
        }}
        onUpdate={({ editor }) => {
          editorRef.current = editor
          const { from, to } = editor.state.selection
          const selectionLength = editor.state.doc.textBetween(from, to, ' ').length
          onUpdate({ html: editor.getHTML(), editor, selectionLength })
        }}
        className="min-h-full"
      />
    </EditorRoot>
  )
}

export default NovelEditor
