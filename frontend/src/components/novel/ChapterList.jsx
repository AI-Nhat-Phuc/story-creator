import React, { useRef } from 'react'
import { Link } from 'react-router-dom'
import { PencilSquareIcon, Bars3Icon } from '@heroicons/react/24/outline'

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

function ChapterList({ chapters, canReorder, onReorder }) {
  const dragIndexRef = useRef(null)

  const handleDragStart = (index) => {
    dragIndexRef.current = index
  }

  const handleDragEnd = () => {
    dragIndexRef.current = null
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleDrop = (targetIndex) => {
    const fromIndex = dragIndexRef.current
    if (fromIndex === null || fromIndex === targetIndex) return
    dragIndexRef.current = null

    const reordered = [...chapters]
    const [moved] = reordered.splice(fromIndex, 1)
    reordered.splice(targetIndex, 0, moved)
    onReorder(reordered)
  }

  if (chapters.length === 0) {
    return (
      <div className="text-center py-16 text-base-content/50">
        <p className="text-lg">No chapters yet.</p>
        <p className="text-sm mt-1">Open a story in the editor and assign it a chapter number to get started.</p>
      </div>
    )
  }

  return (
    <ul className="space-y-2">
      {chapters.map((ch, index) => {
        const words = ch.word_count || 0
        return (
          <li
            key={ch.story_id}
            draggable={canReorder}
            onDragStart={() => handleDragStart(index)}
            onDragEnd={handleDragEnd}
            onDragOver={handleDragOver}
            onDrop={() => handleDrop(index)}
            className={`flex items-center gap-3 p-3 bg-base-200 rounded-lg border border-base-300 ${canReorder ? 'cursor-grab active:cursor-grabbing' : ''}`}
          >
            {canReorder && (
              <Bars3Icon className="w-5 h-5 text-base-content/40 shrink-0" />
            )}

            <span className="text-sm font-mono text-base-content/50 w-8 shrink-0 text-right">
              {ch.chapter_number ?? index + 1}
            </span>

            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">{ch.title}</p>
              <p className="text-xs text-base-content/50">
                {words.toLocaleString()} words
                {ch.updated_at && ` · ${formatDate(ch.updated_at)}`}
              </p>
            </div>

            <Link
              to={`/stories/${ch.story_id}/edit`}
              className="btn btn-ghost btn-xs gap-1 shrink-0"
            >
              <PencilSquareIcon className="w-4 h-4" />
              Edit
            </Link>
          </li>
        )
      })}
    </ul>
  )
}

export default ChapterList
