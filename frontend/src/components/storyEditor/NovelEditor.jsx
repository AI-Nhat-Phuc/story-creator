import React from 'react'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Underline from '@tiptap/extension-underline'
import Highlight from '@tiptap/extension-highlight'
import TextAlign from '@tiptap/extension-text-align'

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

  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder: 'Bắt đầu viết câu chuyện của bạn...' }),
      Underline,
      Highlight.configure({ multicolor: true }),
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
    ],
    content: defaultContent,
    editorProps: {
      attributes: {
        class: 'prose prose-stone dark:prose-invert max-w-none focus:outline-none p-4 md:p-8',
      },
    },
    onCreate: ({ editor }) => {
      editorRef.current = editor
      editor.on('selectionUpdate', ({ editor: e }) => {
        const { from, to } = e.state.selection
        const selectionLength = e.state.doc.textBetween(from, to, ' ').length
        onSelectionChange?.({ selectionLength, editor: e })
      })
    },
    onUpdate: ({ editor }) => {
      editorRef.current = editor
      const { from, to } = editor.state.selection
      const selectionLength = editor.state.doc.textBetween(from, to, ' ').length
      onUpdate({ html: editor.getHTML(), editor, selectionLength })
    },
  })

  return <EditorContent editor={editor} className="min-h-full" />
}

export default NovelEditor
