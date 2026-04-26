import React from 'react'
import Link from 'next/link'
import Tag from '../Tag'
import { BookOpenIcon, GlobeAltIcon, ArrowRightIcon, MapIcon } from '@heroicons/react/24/outline'
import { getServerT } from '../../i18n/serverI18n'

const GENRE_COLOR = {
  adventure: 'success',
  mystery: 'secondary',
  conflict: 'error',
  discovery: 'info',
}

function processStories(stories, worlds) {
  const worldMap = Object.fromEntries((worlds || []).map(w => [w.world_id, w.name]))
  return [...(stories || [])]
    .sort((a, b) => (b.updated_at || b.created_at || '').localeCompare(a.updated_at || a.created_at || ''))
    .slice(0, 8)
    .map(s => ({
      ...s,
      world_name: worldMap[s.world_id] || null,
      content_preview: s.content_preview
        || (s.content ? s.content.replace(/<[^>]*>/g, '').slice(0, 160) : ''),
    }))
}

function StoryCard({ story, featured = false }) {
  const date = story.updated_at || story.created_at
  const wrapperClass = featured
    ? 'col-span-2 bg-base-100 rounded-2xl shadow-md hover:shadow-lg transition p-6 flex flex-col gap-3 group'
    : 'bg-base-100 rounded-2xl shadow hover:shadow-md transition p-4 flex flex-col gap-2 group'
  const titleClass = featured
    ? 'font-extrabold text-2xl leading-snug group-hover:text-primary transition-colors line-clamp-2'
    : 'font-bold text-base leading-snug group-hover:text-primary transition-colors line-clamp-2'
  const previewClass = featured
    ? 'text-base-content/70 text-sm leading-relaxed line-clamp-3'
    : 'text-sm text-base-content/60 line-clamp-2 flex-1'

  return (
    <Link href={`/stories/${story.story_id}`} className={wrapperClass}>
      <h3 className={titleClass}>{story.title}</h3>
      {story.content_preview && <p className={previewClass}>{story.content_preview}</p>}
      <div className="flex items-center gap-2 mt-auto pt-1 flex-wrap">
        {story.genre && <Tag color={GENRE_COLOR[story.genre] || 'accent'} size="sm">{story.genre}</Tag>}
        {story.world_name && (
          <Link
            href={`/worlds/${story.world_id}`}
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
      href={`/worlds/${world.world_id}`}
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
      <Link href={linkTo} className="flex items-center gap-1 text-sm text-base-content/50 hover:text-primary transition">
        {linkLabel} <ArrowRightIcon className="w-4 h-4" />
      </Link>
    </div>
  )
}

function DiscoverySection({ stories: rawStories = [], worlds: rawWorlds = [], locale = 'vi' }) {
  const t = getServerT(locale)
  const stories = processStories(rawStories, rawWorlds)
  const worlds = (rawWorlds || []).slice(0, 6)
  const [featured, ...rest] = stories

  return (
    <div className="space-y-10 max-w-6xl mx-auto">
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

export default DiscoverySection
