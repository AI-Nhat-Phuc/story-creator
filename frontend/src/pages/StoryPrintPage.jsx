import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { storiesAPI } from '../services/api'

function renderContent(story) {
  if (!story.content) return null

  if (story.format === 'html') {
    return (
      <div
        className="prose prose-lg max-w-none"
        dangerouslySetInnerHTML={{ __html: story.content }}
      />
    )
  }

  return (
    <pre className="whitespace-pre-wrap font-serif text-base leading-relaxed">
      {story.content}
    </pre>
  )
}

function StoryPrintPage() {
  const { storyId } = useParams()
  const [story, setStory] = useState(null)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    storiesAPI.getById(storyId)
      .then(res => setStory(res.data))
      .catch(() => setNotFound(true))
  }, [storyId])

  // Trigger print once story is loaded
  useEffect(() => {
    if (story) {
      const prevTitle = document.title
      document.title = story.title || 'Story'
      window.print()
      return () => { document.title = prevTitle }
    }
  }, [story])

  if (notFound) {
    return (
      <div className="p-8 font-serif">
        <p>Story not found.</p>
      </div>
    )
  }

  if (!story) {
    return (
      <div className="p-8 font-serif">
        <p>Loading…</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-8 font-serif">
      <h1 className="text-4xl font-bold mb-1">
        {story.title}
      </h1>

      {(story.author_name || story.world_name) && (
        <p className="text-gray-500 mb-8 text-sm">
          {story.author_name && `By ${story.author_name}`}
          {story.author_name && story.world_name && ' · '}
          {story.world_name && story.world_name}
        </p>
      )}

      <hr className="mb-8 border-gray-300" />

      {renderContent(story)}
    </div>
  )
}

export default StoryPrintPage
