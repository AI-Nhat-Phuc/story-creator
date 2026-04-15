import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { marked } from 'marked'
import {
  ArrowLeftIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline'
import LoadingSpinner from '../LoadingSpinner'

function StoryReaderView({ story, prev, next, isLoading }) {
  const { t } = useTranslation()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  if (!story) return null

  const renderContent = () => {
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
      <div className="text-lg whitespace-pre-wrap leading-relaxed">
        {story.content}
      </div>
    )
  }

  const NavButton = ({ target, label, icon, disabledLabel, align }) => {
    const className = `btn btn-sm gap-1 ${align === 'end' ? '' : ''}`
    if (!target) {
      return (
        <span className="btn btn-sm btn-disabled gap-1 opacity-50">
          {icon === 'left' && <ChevronLeftIcon className="w-4 h-4" />}
          {disabledLabel}
          {icon === 'right' && <ChevronRightIcon className="w-4 h-4" />}
        </span>
      )
    }
    return (
      <Link to={`/stories/${target.story_id}/read`} className={className}>
        {icon === 'left' && <ChevronLeftIcon className="w-4 h-4" />}
        <span className="truncate max-w-[40vw]">{label}: {target.title}</span>
        {icon === 'right' && <ChevronRightIcon className="w-4 h-4" />}
      </Link>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-4">
        <Link to={`/stories/${story.story_id}`} className="btn btn-ghost btn-sm gap-1">
          <ArrowLeftIcon className="w-4 h-4" />
          {t('pages.storyReader.backToStory')}
        </Link>
      </div>

      <div className="flex justify-between items-center mb-6 gap-2 flex-wrap">
        <NavButton
          target={prev}
          label={t('pages.storyReader.prev')}
          icon="left"
          disabledLabel={t('pages.storyReader.noPrev')}
        />
        <NavButton
          target={next}
          label={t('pages.storyReader.next')}
          icon="right"
          disabledLabel={t('pages.storyReader.noNext')}
          align="end"
        />
      </div>

      <article className="bg-base-100 shadow-xl rounded-box p-6 sm:p-10">
        <h1 className="font-bold text-3xl sm:text-4xl mb-6 text-center">{story.title}</h1>
        {renderContent()}
      </article>

      <div className="flex justify-between items-center mt-8 gap-2 flex-wrap">
        <NavButton
          target={prev}
          label={t('pages.storyReader.prev')}
          icon="left"
          disabledLabel={t('pages.storyReader.noPrev')}
        />
        <NavButton
          target={next}
          label={t('pages.storyReader.next')}
          icon="right"
          disabledLabel={t('pages.storyReader.noNext')}
          align="end"
        />
      </div>
    </div>
  )
}

export default StoryReaderView
