'use client'

import React from 'react'
import { Link } from '../../utils/router-compat'
import { useTranslation } from 'react-i18next'
import {
  ArrowLeftIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline'
import LoadingSpinner from '../LoadingSpinner'
import { renderStoryContent } from '../../utils/renderStoryContent'

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

  const NavButton = ({ target, label, disabledLabel, Icon, iconSide }) => {
    if (!target) {
      return (
        <span className="btn btn-sm btn-disabled gap-1 opacity-50">
          {iconSide === 'left' && <Icon className="w-4 h-4" />}
          {disabledLabel}
          {iconSide === 'right' && <Icon className="w-4 h-4" />}
        </span>
      )
    }
    return (
      <Link to={`/stories/${target.story_id}/read`} className="btn btn-sm gap-1">
        {iconSide === 'left' && <Icon className="w-4 h-4" />}
        <span className="truncate max-w-[40vw]">{label}: {target.title}</span>
        {iconSide === 'right' && <Icon className="w-4 h-4" />}
      </Link>
    )
  }

  const NavBar = () => (
    <div className="flex justify-between items-center gap-2 flex-wrap">
      <NavButton
        target={prev}
        label={t('pages.storyReader.prev')}
        disabledLabel={t('pages.storyReader.noPrev')}
        Icon={ChevronLeftIcon}
        iconSide="left"
      />
      <NavButton
        target={next}
        label={t('pages.storyReader.next')}
        disabledLabel={t('pages.storyReader.noNext')}
        Icon={ChevronRightIcon}
        iconSide="right"
      />
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-4">
        <Link to={`/stories/${story.story_id}`} className="btn btn-ghost btn-sm gap-1">
          <ArrowLeftIcon className="w-4 h-4" />
          {t('pages.storyReader.backToStory')}
        </Link>
      </div>

      <div className="mb-6"><NavBar /></div>

      <article className="bg-base-100 shadow-xl rounded-box p-6 sm:p-10">
        <h1 className="font-bold text-3xl sm:text-4xl mb-6 text-center">{story.title}</h1>
        {renderStoryContent(story, {
          className: 'text-lg whitespace-pre-wrap leading-relaxed',
          proseClassName: 'prose prose-lg max-w-none',
        })}
      </article>

      <div className="mt-8"><NavBar /></div>
    </div>
  )
}

export default StoryReaderView
