import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import LoadingSpinner from '../LoadingSpinner'
import Tag from '../Tag'
import {
  BookOpenIcon,
  GlobeAltIcon,
} from '@heroicons/react/24/outline'

function StoryCard({ story }) {
  const date = story.updated_at || story.created_at
  return (
    <Link
      to={`/stories/${story.story_id}`}
      className="bg-base-100 rounded-box shadow p-4 flex flex-col gap-2 hover:shadow-md transition"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-bold text-base leading-snug line-clamp-2">{story.title}</h3>
        {story.visibility && (
          <span className={`badge badge-xs shrink-0 mt-0.5 ${
            story.visibility === 'public' ? 'badge-success' :
            story.visibility === 'draft'  ? 'badge-warning' : 'badge-ghost'
          }`}>
            {story.visibility}
          </span>
        )}
      </div>
      {story.content_preview && (
        <p className="text-sm text-base-content/60 line-clamp-2">{story.content_preview}</p>
      )}
      <div className="flex items-center gap-2 mt-auto pt-1 flex-wrap">
        {story.genre && <Tag color="accent" size="sm">{story.genre}</Tag>}
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
      className="bg-base-100 rounded-box shadow p-4 flex flex-col gap-1 hover:shadow-md transition"
    >
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-bold text-base leading-snug line-clamp-1">{world.name}</h3>
        {world.visibility && (
          <span className={`badge badge-xs shrink-0 ${
            world.visibility === 'public' ? 'badge-success' : 'badge-ghost'
          }`}>
            {world.visibility}
          </span>
        )}
      </div>
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

function DiscoveryView({ stories, worlds, isLoading }) {
  const { t } = useTranslation()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="space-y-10">
      {/* Recent stories */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <BookOpenIcon className="w-5 h-5" />
            {t('pages.home.recentStories')}
          </h2>
          <Link to="/stories" className="btn btn-ghost btn-sm">
            {t('pages.home.viewAll')}
          </Link>
        </div>
        {stories.length === 0 ? (
          <p className="text-base-content/50 italic py-4">{t('pages.home.noStories')}</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {stories.map(s => <StoryCard key={s.story_id} story={s} />)}
          </div>
        )}
      </section>

      {/* Recent worlds */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <GlobeAltIcon className="w-5 h-5" />
            {t('pages.home.recentWorlds')}
          </h2>
          <Link to="/worlds" className="btn btn-ghost btn-sm">
            {t('pages.home.viewAll')}
          </Link>
        </div>
        {worlds.length === 0 ? (
          <p className="text-base-content/50 italic py-4">{t('pages.home.noWorlds')}</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {worlds.map(w => <WorldCard key={w.world_id} world={w} />)}
          </div>
        )}
      </section>
    </div>
  )
}

export default DiscoveryView
