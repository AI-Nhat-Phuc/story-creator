import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import LoadingSpinner from '../LoadingSpinner'
import Tag from '../Tag'
import { BookOpenIcon, GlobeAltIcon, ArrowRightIcon, MapIcon } from '@heroicons/react/24/outline'

const GENRE_COLOR = {
  adventure: 'success',
  mystery: 'secondary',
  conflict: 'error',
  discovery: 'info',
}

function StoryCard({ story, featured = false }) {
  const date = story.updated_at || story.created_at

  if (featured) {
    return (
      <Link
        to={`/stories/${story.story_id}`}
        className="col-span-2 bg-base-100 rounded-2xl shadow-md hover:shadow-lg transition p-6 flex flex-col gap-3 group"
      >
        <h3 className="font-extrabold text-2xl leading-snug group-hover:text-primary transition-colors line-clamp-2">
          {story.title}
        </h3>
        {story.content_preview && (
          <p className="text-base-content/70 text-sm leading-relaxed line-clamp-3">
            {story.content_preview}
          </p>
        )}
        <div className="flex items-center gap-2 mt-auto flex-wrap">
          {story.genre && (
            <Tag color={GENRE_COLOR[story.genre] || 'accent'} size="sm">{story.genre}</Tag>
          )}
          {story.world_name && (
            <Link
              to={`/worlds/${story.world_id}`}
              onClick={e => e.stopPropagation()}
              className="flex items-center gap-1 text-xs text-base-content/50 hover:text-primary transition"
            >
              <MapIcon className="w-3 h-3" />{story.world_name}
            </Link>
          )}
          {date && (
            <span className="text-xs text-base-content/40 ml-auto">
              {new Date(date).toLocaleDateString()}
            </span>
          )}
        </div>
      </Link>
    )
  }

  return (
    <Link
      to={`/stories/${story.story_id}`}
      className="bg-base-100 rounded-2xl shadow hover:shadow-md transition p-4 flex flex-col gap-2 group"
    >
      <h3 className="font-bold text-base leading-snug group-hover:text-primary transition-colors line-clamp-2">
        {story.title}
      </h3>
      {story.content_preview && (
        <p className="text-sm text-base-content/60 line-clamp-2 flex-1">
          {story.content_preview}
        </p>
      )}
      <div className="flex items-center gap-2 mt-auto pt-1 flex-wrap">
        {story.genre && (
          <Tag color={GENRE_COLOR[story.genre] || 'accent'} size="sm">{story.genre}</Tag>
        )}
        {story.world_name && (
          <Link
            to={`/worlds/${story.world_id}`}
            onClick={e => e.stopPropagation()}
            className="flex items-center gap-1 text-xs text-base-content/50 hover:text-primary transition"
          >
            <MapIcon className="w-3 h-3" />{story.world_name}
          </Link>
        )}
        {date && (
          <span className="text-xs text-base-content/40 ml-auto">
            {new Date(date).toLocaleDateString()}
          </span>
        )}
      </div>
    </Link>
  )
}

function WorldCard({ world }) {
  return (
    <Link
      to={`/worlds/${world.world_id}`}
      className="bg-base-100 rounded-2xl shadow hover:shadow-md transition p-4 flex flex-col gap-2 group"
    >
      <h3 className="font-bold text-base leading-snug group-hover:text-primary transition-colors line-clamp-1">
        {world.name}
      </h3>
      {world.world_type && (
        <Tag color="secondary" size="sm" className="w-fit">{world.world_type}</Tag>
      )}
      {world.created_at && (
        <span className="text-xs text-base-content/40 mt-auto pt-1">
          {new Date(world.created_at).toLocaleDateString()}
        </span>
      )}
    </Link>
  )
}

function SectionHeader({ icon: Icon, title, linkTo, linkLabel }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-xl font-bold flex items-center gap-2">
        <Icon className="w-5 h-5 text-primary" />
        {title}
      </h2>
      <Link to={linkTo} className="flex items-center gap-1 text-sm text-base-content/50 hover:text-primary transition">
        {linkLabel} <ArrowRightIcon className="w-4 h-4" />
      </Link>
    </div>
  )
}

function DiscoveryView({ stories, worlds, isLoading }) {
  const { t } = useTranslation()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  const [featured, ...rest] = stories

  return (
    <div className="space-y-10 max-w-6xl mx-auto">
      {/* Stories section */}
      <section>
        <SectionHeader
          icon={BookOpenIcon}
          title={t('pages.home.recentStories')}
          linkTo="/stories"
          linkLabel={t('pages.home.viewAll')}
        />
        {stories.length === 0 ? (
          <p className="text-base-content/50 italic py-4">{t('pages.home.noStories')}</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 auto-rows-fr">
            {featured && <StoryCard story={featured} featured />}
            {rest.map(s => <StoryCard key={s.story_id} story={s} />)}
          </div>
        )}
      </section>

      {/* Worlds section */}
      <section>
        <SectionHeader
          icon={GlobeAltIcon}
          title={t('pages.home.recentWorlds')}
          linkTo="/worlds"
          linkLabel={t('pages.home.viewAll')}
        />
        {worlds.length === 0 ? (
          <p className="text-base-content/50 italic py-4">{t('pages.home.noWorlds')}</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {worlds.map(w => <WorldCard key={w.world_id} world={w} />)}
          </div>
        )}
      </section>
    </div>
  )
}

export default DiscoveryView
