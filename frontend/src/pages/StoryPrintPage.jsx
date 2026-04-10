import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'
import { usePageTitle } from '../hooks/usePageTitle'
import { storiesAPI } from '../services/api'
import { marked } from 'marked'

function renderContent(story) {
  if (!story.content) return null

  if (story.format === 'html' || story.format === 'markdown') {
    const html = story.format === 'markdown' ? marked.parse(story.content) : story.content
    return (
      <div
        className="prose prose-lg max-w-none"
        dangerouslySetInnerHTML={{ __html: html }}
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
  const { t } = useTranslation()
  const [story, setStory] = useState(null)
  const [notFound, setNotFound] = useState(false)
  const pageTitle = usePageTitle('storyPrint', story?.title)

  useEffect(() => {
    storiesAPI.getById(storyId)
      .then(res => setStory(res.data))
      .catch(() => setNotFound(true))
  }, [storyId])

  useEffect(() => {
    if (story) window.print()
  }, [story])

  if (notFound) {
    return (
      <div className="p-8 font-serif">
        <Helmet><title>{pageTitle}</title></Helmet>
        <p>{t('pages.storyPrint.notFound')}</p>
      </div>
    )
  }

  if (!story) {
    return (
      <div className="p-8 font-serif">
        <Helmet><title>{pageTitle}</title></Helmet>
        <p>{t('common.loading')}</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-8 font-serif">
      <Helmet>
        <title>{pageTitle}</title>
        <meta name="description" content={t('meta.storyPrint.description')} />
      </Helmet>
      <h1 className="text-4xl font-bold mb-1">
        {story.title}
      </h1>

      {(story.author_name || story.world_name) && (
        <p className="text-gray-500 mb-8 text-sm">
          {story.author_name && t('pages.storyPrint.by', { name: story.author_name })}
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
