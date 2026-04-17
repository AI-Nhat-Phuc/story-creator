import { useMemo, useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Tag from '../Tag'
import {
  UserIcon,
  MapPinIcon,
  LinkIcon,
  Bars3Icon,
  TrashIcon,
} from '@heroicons/react/24/outline'

function WorldTimeline({
  stories,
  characters = [],
  locations = [],
  getTimelineLabel,
  onDeleteStory,
  canReorder = false,
  onReorderStories,
  hasMore = false,
  loadingMore = false,
  onLoadMore,
}) {
  const { t } = useTranslation()
  // Spec BR-1/BR-2 — sort by (order ASC, created_at ASC). Legacy stories
  // with no `order` are pushed to the end.
  const sortedStories = useMemo(() => (
    [...(stories || [])].sort((a, b) => {
      const orderA = a.order ?? Number.MAX_SAFE_INTEGER
      const orderB = b.order ?? Number.MAX_SAFE_INTEGER
      if (orderA !== orderB) return orderA - orderB
      return (a.created_at || '').localeCompare(b.created_at || '')
    })
  ), [stories])

  const [draggingIdx, setDraggingIdx] = useState(null)
  const [hoverIdx, setHoverIdx] = useState(null)
  // HTML5 DnD fires dragenter on children; counter handles flicker-free leave.
  const dragCounterRef = useRef(0)

  if (!stories || stories.length === 0) {
    return <p className="opacity-60 py-8 text-center">{t('pages.worldTimeline.empty')}</p>
  }

  const paletteMap = {
    adventure: { line: 'bg-primary', iconText: 'text-primary', iconBorder: 'border-primary', badgeColor: 'success' },
    mystery: { line: 'bg-secondary', iconText: 'text-secondary', iconBorder: 'border-secondary', badgeColor: 'secondary' },
    conflict: { line: 'bg-error', iconText: 'text-error', iconBorder: 'border-error', badgeColor: 'error' },
    discovery: { line: 'bg-info', iconText: 'text-info', iconBorder: 'border-info', badgeColor: 'info' }
  }

  const getStoryCharacters = (story) => {
    const entityIds = story.entities || story.entity_ids || []
    if (entityIds.length === 0) return []
    return characters.filter(char => entityIds.includes(char.entity_id))
  }

  const getStoryLocations = (story) => {
    const locationIds = story.locations || story.location_ids || []
    if (locationIds.length === 0) return []
    return locations.filter(loc => locationIds.includes(loc.location_id))
  }

  const handleDragStart = (idx) => (e) => {
    setDraggingIdx(idx)
    dragCounterRef.current = 0
    e.dataTransfer.effectAllowed = 'move'
    try { e.dataTransfer.setData('text/plain', String(idx)) } catch { /* Firefox quirks */ }
  }

  const handleDragEnter = (idx) => (e) => {
    if (draggingIdx === null) return
    e.preventDefault()
    dragCounterRef.current += 1
    setHoverIdx(idx)
  }

  const handleDragOver = (e) => {
    if (draggingIdx === null) return
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDragLeave = () => {
    dragCounterRef.current -= 1
    if (dragCounterRef.current <= 0) {
      dragCounterRef.current = 0
      setHoverIdx(null)
    }
  }

  const handleDrop = (targetIdx) => (e) => {
    e.preventDefault()
    if (draggingIdx === null || draggingIdx === targetIdx) {
      setDraggingIdx(null)
      setHoverIdx(null)
      return
    }
    const ids = sortedStories.map(s => s.story_id)
    const [moved] = ids.splice(draggingIdx, 1)
    // When dragging forward, splice already shifted indices left by 1.
    const insertAt = draggingIdx < targetIdx ? targetIdx - 1 : targetIdx
    ids.splice(insertAt, 0, moved)
    setDraggingIdx(null)
    setHoverIdx(null)
    onReorderStories?.(ids)
  }

  const handleDragEnd = () => {
    setDraggingIdx(null)
    setHoverIdx(null)
    dragCounterRef.current = 0
  }

  return (
    <>
    <ul className="timeline timeline-vertical max-md:timeline-compact">
      {sortedStories.map((story, groupIndex) => {
        const palette = paletteMap[story.genre] || {
          line: 'bg-accent',
          iconText: 'text-accent',
          iconBorder: 'border-accent',
          badgeColor: 'accent'
        }

        // Zigzag: odd-indexed rows flip sides on md+ screens.
        const flip = groupIndex % 2 === 1
        const metaPos = flip ? 'timeline-end md:text-left' : 'timeline-start md:text-right'
        const cardPos = flip ? 'timeline-start' : 'timeline-end'
        const isDragging = draggingIdx === groupIndex
        const showGap = canReorder && draggingIdx !== null && hoverIdx === groupIndex && draggingIdx !== groupIndex

        // Get linked stories
        const linkedStoryIds = story.linked_stories || []
        const linkedStories = linkedStoryIds
          .map(id => sortedStories.find(s => s.story_id === id))
          .filter(Boolean)

        const timeLabel = getTimelineLabel ? getTimelineLabel(story) : `#${story.order ?? '?'}`

        return (
          <li
            key={story.story_id}
            onDragEnter={canReorder ? handleDragEnter(groupIndex) : undefined}
            onDragOver={canReorder ? handleDragOver : undefined}
            onDragLeave={canReorder ? handleDragLeave : undefined}
            onDrop={canReorder ? handleDrop(groupIndex) : undefined}
            className={isDragging ? 'opacity-40' : ''}
          >
            {/* Top connector — absent on the very first item */}
            {groupIndex > 0 && <hr className={palette.line} />}
            {showGap && (
              <div className="timeline-end w-full h-20 border-2 border-dashed border-primary bg-primary/5 rounded" />
            )}
            <div className={metaPos}>
              <time className="opacity-70 font-mono text-sm px-2">{timeLabel}</time>
            </div>
            <div className="timeline-middle">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className={`w-5 h-5 ${palette.iconText}`}>
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
              </svg>
            </div>
            <div className={`space-y-3 min-w-0 ${cardPos}`}>
              <div
                className={`bg-base-100 shadow-lg p-4 timeline-box transition-transform max-w-full overflow-hidden ${isDragging ? 'scale-95' : ''}`}
                draggable={canReorder}
                onDragStart={canReorder ? handleDragStart(groupIndex) : undefined}
                onDragEnd={canReorder ? handleDragEnd : undefined}
              >
                <div className="flex justify-between items-center gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    {canReorder && (
                      <span
                        className="cursor-grab active:cursor-grabbing text-base-content/40 shrink-0"
                        title={t('pages.worldTimeline.dragToReorder')}
                      >
                        <Bars3Icon className="w-4 h-4" />
                      </span>
                    )}
                    <Link to={`/stories/${story.story_id}`} className="link link-hover min-w-0">
                      <h3 className="font-bold text-xl truncate">{story.title}</h3>
                    </Link>
                  </div>
                  {onDeleteStory && (
                    <button
                      onClick={(e) => { e.preventDefault(); onDeleteStory(story.story_id, story.title) }}
                      className="text-error btn btn-ghost btn-xs"
                      title={t('pages.worldTimeline.deleteStory')}
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  )}
                </div>
                {(story.content_preview || story.content) && (
                  <p className="text-sm text-base-content/60 mt-1 line-clamp-2">
                    {story.content_preview
                      ? story.content_preview.slice(0, 120)
                      : story.content.replace(/<[^>]*>/g, '').slice(0, 120)}
                  </p>
                )}
                <div className="flex items-center gap-2 mt-1 text-xs text-base-content/40">
                  {story.created_at && (
                    <time>{new Date(story.created_at).toLocaleDateString()}</time>
                  )}
                  {story.visibility && (
                    <span className={`badge badge-sm ${story.visibility === 'public' ? 'badge-success' : story.visibility === 'draft' ? 'badge-warning' : 'badge-ghost'}`}>
                      {t(`common.${story.visibility}`, story.visibility)}
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap gap-2 mt-3">
                  <Tag color={palette.badgeColor}>{story.genre}</Tag>
                  {getStoryCharacters(story).slice(0, 3).map(char => (
                    <Tag key={char.entity_id} color="primary" outline icon={UserIcon}>
                      {char.name}
                    </Tag>
                  ))}
                  {getStoryCharacters(story).length > 3 && (
                    <Tag color="ghost">+{getStoryCharacters(story).length - 3}</Tag>
                  )}
                  {getStoryLocations(story).slice(0, 2).map(loc => (
                    <Tag key={loc.location_id} color="secondary" outline icon={MapPinIcon}>
                      {loc.name}
                    </Tag>
                  ))}
                  {getStoryLocations(story).length > 2 && (
                    <Tag color="ghost">{t('pages.worldTimeline.moreLocations', { count: getStoryLocations(story).length - 2 })}</Tag>
                  )}
                </div>
                {linkedStories.length > 0 && (
                  <div className="mt-3 pt-3 border-base-300 border-t">
                    <p className="opacity-70 mb-2 text-xs"><LinkIcon className="inline w-3 h-3" /> {t('pages.worldTimeline.linkedWith')}</p>
                    <div className="flex flex-wrap gap-1">
                      {linkedStories.map(linked => (
                        <Tag
                          key={linked.story_id}
                          as={Link}
                          to={`/stories/${linked.story_id}`}
                          size="sm"
                          outline
                          className="hover:badge-secondary"
                        >
                          {linked.title}
                        </Tag>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
            {/* Bottom connector — absent on the very last item */}
            {groupIndex < sortedStories.length - 1 && <hr className={palette.line} />}
          </li>
        )
      })}
    </ul>
    {hasMore && (
      <div className="flex justify-center mt-6">
        <button
          onClick={onLoadMore}
          disabled={loadingMore}
          className="btn btn-outline btn-primary btn-sm gap-2"
        >
          {loadingMore
            ? <><span className="loading loading-spinner loading-xs"></span> {t('pages.worldDetail.loadingMoreStories')}</>
            : t('pages.worldDetail.loadMoreStories')}
        </button>
      </div>
    )}
    </>
  )
}

export default WorldTimeline
