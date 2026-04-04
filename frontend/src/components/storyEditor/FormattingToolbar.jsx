import React from 'react'
import { ListBulletIcon } from '@heroicons/react/24/outline'

function ToolbarBtn({ active, onMouseDown, title, children }) {
  return (
    <button
      onMouseDown={onMouseDown}
      title={title}
      className={`btn btn-xs btn-ghost h-7 min-h-0 px-2 ${active ? 'bg-base-300 btn-active' : ''}`}
    >
      {children}
    </button>
  )
}

function Sep() {
  return <div className="w-px h-5 bg-base-300 mx-1 shrink-0" />
}

function FormattingToolbar({ editorRef, activeFormats = {} }) {
  const run = (fn) => (e) => {
    e.preventDefault()
    const ed = editorRef.current
    if (!ed) return
    fn(ed)
  }

  return (
    <div className="flex items-center flex-wrap gap-0.5 px-3 py-1.5 border-b border-base-300 bg-base-100 shrink-0">
      {/* Headings */}
      <ToolbarBtn
        active={!activeFormats.h1 && !activeFormats.h2 && !activeFormats.h3}
        title="Paragraph"
        onMouseDown={run(ed => ed.chain().focus().setParagraph().run())}
      >
        <span className="text-xs font-normal">T</span>
      </ToolbarBtn>
      <ToolbarBtn
        active={activeFormats.h1}
        title="Heading 1"
        onMouseDown={run(ed => ed.chain().focus().toggleHeading({ level: 1 }).run())}
      >
        <span className="text-sm font-bold">H1</span>
      </ToolbarBtn>
      <ToolbarBtn
        active={activeFormats.h2}
        title="Heading 2"
        onMouseDown={run(ed => ed.chain().focus().toggleHeading({ level: 2 }).run())}
      >
        <span className="text-xs font-bold">H2</span>
      </ToolbarBtn>
      <ToolbarBtn
        active={activeFormats.h3}
        title="Heading 3"
        onMouseDown={run(ed => ed.chain().focus().toggleHeading({ level: 3 }).run())}
      >
        <span className="text-xs font-bold">H3</span>
      </ToolbarBtn>

      <Sep />

      {/* Inline formatting */}
      <ToolbarBtn
        active={activeFormats.bold}
        title="Bold (Ctrl+B)"
        onMouseDown={run(ed => ed.chain().focus().toggleBold().run())}
      >
        <span className="font-bold">B</span>
      </ToolbarBtn>
      <ToolbarBtn
        active={activeFormats.italic}
        title="Italic (Ctrl+I)"
        onMouseDown={run(ed => ed.chain().focus().toggleItalic().run())}
      >
        <span className="italic font-serif">I</span>
      </ToolbarBtn>
      <ToolbarBtn
        active={activeFormats.underline}
        title="Underline (Ctrl+U)"
        onMouseDown={run(ed => ed.chain().focus().toggleUnderline().run())}
      >
        <span className="underline">U</span>
      </ToolbarBtn>
      <ToolbarBtn
        active={activeFormats.strike}
        title="Strikethrough"
        onMouseDown={run(ed => ed.chain().focus().toggleStrike().run())}
      >
        <span className="line-through">S</span>
      </ToolbarBtn>

      <Sep />

      {/* Highlight */}
      <ToolbarBtn
        active={activeFormats.highlight}
        title="Highlight"
        onMouseDown={run(ed => ed.chain().focus().toggleHighlight({ color: '#fef08a' }).run())}
      >
        <span
          className="px-0.5 rounded font-bold text-xs"
          style={{ background: activeFormats.highlight ? '#fef08a' : 'transparent' }}
        >
          A
        </span>
      </ToolbarBtn>

      <Sep />

      {/* Lists */}
      <ToolbarBtn
        active={activeFormats.bulletList}
        title="Bullet list"
        onMouseDown={run(ed => ed.chain().focus().toggleBulletList().run())}
      >
        <ListBulletIcon className="w-4 h-4" />
      </ToolbarBtn>
      <ToolbarBtn
        active={activeFormats.orderedList}
        title="Numbered list"
        onMouseDown={run(ed => ed.chain().focus().toggleOrderedList().run())}
      >
        <span className="font-mono text-xs">1.</span>
      </ToolbarBtn>

      <Sep />

      {/* Text alignment */}
      <ToolbarBtn
        active={activeFormats.alignLeft}
        title="Align left"
        onMouseDown={run(ed => ed.chain().focus().setTextAlign('left').run())}
      >
        <AlignLeftIcon />
      </ToolbarBtn>
      <ToolbarBtn
        active={activeFormats.alignCenter}
        title="Align center"
        onMouseDown={run(ed => ed.chain().focus().setTextAlign('center').run())}
      >
        <AlignCenterIcon />
      </ToolbarBtn>
      <ToolbarBtn
        active={activeFormats.alignRight}
        title="Align right"
        onMouseDown={run(ed => ed.chain().focus().setTextAlign('right').run())}
      >
        <AlignRightIcon />
      </ToolbarBtn>
    </div>
  )
}

// Simple inline SVG icons for text alignment
function AlignLeftIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 16 16" fill="currentColor">
      <rect x="1" y="2" width="14" height="2" rx="1" />
      <rect x="1" y="6" width="9" height="2" rx="1" />
      <rect x="1" y="10" width="14" height="2" rx="1" />
      <rect x="1" y="14" width="6" height="2" rx="1" />
    </svg>
  )
}

function AlignCenterIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 16 16" fill="currentColor">
      <rect x="1" y="2" width="14" height="2" rx="1" />
      <rect x="3.5" y="6" width="9" height="2" rx="1" />
      <rect x="1" y="10" width="14" height="2" rx="1" />
      <rect x="5" y="14" width="6" height="2" rx="1" />
    </svg>
  )
}

function AlignRightIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 16 16" fill="currentColor">
      <rect x="1" y="2" width="14" height="2" rx="1" />
      <rect x="6" y="6" width="9" height="2" rx="1" />
      <rect x="1" y="10" width="14" height="2" rx="1" />
      <rect x="9" y="14" width="6" height="2" rx="1" />
    </svg>
  )
}

export default FormattingToolbar
