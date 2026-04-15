import React from 'react'
import { marked } from 'marked'

/**
 * Render a story's `content` according to its `format` field.
 *
 * Returns a React element (or null) — used by StoryDetailView and
 * StoryReaderView so both stay in sync.
 *
 * @param {{content?: string, format?: 'plain' | 'markdown' | 'html'}} story
 * @param {{className?: string}} [options]
 */
export function renderStoryContent(story, options = {}) {
  if (!story?.content) return null
  const className = options.className || 'text-lg whitespace-pre-wrap'

  if (story.format === 'html' || story.format === 'markdown') {
    const html = story.format === 'markdown'
      ? marked.parse(story.content)
      : story.content
    return (
      <div
        className={options.proseClassName || 'prose prose-sm max-w-none'}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    )
  }

  return <p className={className}>{story.content}</p>
}
