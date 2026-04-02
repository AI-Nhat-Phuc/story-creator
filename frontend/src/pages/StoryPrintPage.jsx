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
      document.title = story.title || 'Story'
      window.print()
    }
  }, [story])

  if (notFound) {
    return (
      <div style={{ padding: '2rem', fontFamily: 'serif' }}>
        <p>Story not found.</p>
      </div>
    )
  }

  if (!story) {
    return (
      <div style={{ padding: '2rem', fontFamily: 'serif' }}>
        <p>Loading…</p>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto', padding: '2rem 1.5rem', fontFamily: 'Georgia, serif' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
        {story.title}
      </h1>

      {(story.author_name || story.world_name) && (
        <p style={{ color: '#555', marginBottom: '2rem', fontSize: '0.9rem' }}>
          {story.author_name && `By ${story.author_name}`}
          {story.author_name && story.world_name && ' · '}
          {story.world_name && story.world_name}
        </p>
      )}

      <hr style={{ marginBottom: '2rem', borderColor: '#ccc' }} />

      {renderContent(story)}
    </div>
  )
}

export default StoryPrintPage
