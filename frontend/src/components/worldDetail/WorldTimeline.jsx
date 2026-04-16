import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import Tag from '../Tag'
import {
  UserIcon,
  MapPinIcon,
  LinkIcon,
  ClockIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'

function WorldTimeline({ stories, characters = [], locations = [], getStoryWorldTime, getTimelineLabel, onDeleteStory }) {
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

  if (!stories || stories.length === 0) {
    return <p className="opacity-60 py-8 text-center">Chưa có câu chuyện nào</p>
  }

  const paletteMap = {
    adventure: { line: 'bg-primary', iconText: 'text-primary', iconBorder: 'border-primary', badgeColor: 'success' },
    mystery: { line: 'bg-secondary', iconText: 'text-secondary', iconBorder: 'border-secondary', badgeColor: 'secondary' },
    conflict: { line: 'bg-error', iconText: 'text-error', iconBorder: 'border-error', badgeColor: 'error' },
    discovery: { line: 'bg-info', iconText: 'text-info', iconBorder: 'border-info', badgeColor: 'info' }
  }

  // Get characters for a story by entities (entity IDs array)
  const getStoryCharacters = (story) => {
    const entityIds = story.entities || story.entity_ids || []
    if (entityIds.length === 0) return []
    return characters.filter(char => entityIds.includes(char.entity_id))
  }

  // Get locations for a story by location IDs array
  const getStoryLocations = (story) => {
    const locationIds = story.locations || story.location_ids || []
    if (locationIds.length === 0) return []
    return locations.filter(loc => locationIds.includes(loc.location_id))
  }

  // One zigzag group per story — alternating left/right is handled at render
  // time. We still fall back to `timeLabel` for back-compat with stories that
  // carry legacy world_time metadata.
  const yearGroups = sortedStories.map((story) => ({
    yearKey: story.story_id,
    stories: [story],
    worldTime: getStoryWorldTime ? getStoryWorldTime(story) : null,
    timeLabel: getTimelineLabel ? getTimelineLabel(story) : `#${story.order ?? '?'}`,
  }))

  return (
    <ul className="timeline timeline-vertical max-md:timeline-compact">
      {yearGroups.map((group, groupIndex) => {
        // Use first story's genre for the line color
        const firstStory = group.stories[0]
        const palette = paletteMap[firstStory.genre] || {
          line: 'bg-accent',
          iconText: 'text-accent',
          iconBorder: 'border-accent',
          badgeColor: 'accent'
        }

        // Zigzag: odd-indexed groups flip sides on md+ screens.
        const flip = groupIndex % 2 === 1
        const metaPos = flip ? 'timeline-end md:text-left' : 'timeline-start md:text-right'
        const cardPos = flip ? 'timeline-start' : 'timeline-end'
        return (
          <li key={group.yearKey}>
            {groupIndex === 0 && <hr className={palette.line} />}
            <div className={`${metaPos} text-left`}>
              <time className="opacity-70 font-mono text-sm"><ClockIcon className="inline w-3.5 h-3.5" /> {group.timeLabel}</time>
              {group.worldTime?.era && (
                <p className="opacity-60 mt-1 text-xs">Kỷ nguyên: {group.worldTime.era}</p>
              )}
            </div>
            <div className="timeline-middle">
              <div className={`timeline-icon border-2 ${palette.iconBorder} ${palette.iconText}`}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
            <div className={`space-y-3 ${cardPos}`}>
              {group.stories.map((story) => {
                const storyWorldTime = getStoryWorldTime(story)
                const storyPalette = paletteMap[story.genre] || {
                  line: 'bg-accent',
                  iconText: 'text-accent',
                  iconBorder: 'border-accent',
                  badgeColor: 'accent'
                }

                // Get linked stories
                const linkedStoryIds = story.linked_stories || []
                const linkedStories = linkedStoryIds
                  .map(id => sortedStories.find(s => s.story_id === id))
                  .filter(Boolean)

                return (
                  <div key={story.story_id} className="bg-base-100 shadow-lg p-4 timeline-box">
                    <div className="flex justify-between items-center">
                      <Link to={`/stories/${story.story_id}`} className="link link-hover">
                        <h3 className="font-bold text-xl">{story.title}</h3>
                      </Link>
                      {onDeleteStory && (
                        <button
                          onClick={(e) => { e.preventDefault(); onDeleteStory(story.story_id, story.title) }}
                          className="text-error btn btn-ghost btn-xs"
                          title="Xóa câu chuyện"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                    {story.content && (
                      <p className="text-sm text-base-content/60 mt-1 line-clamp-2">
                        {story.content.replace(/<[^>]*>/g, '').slice(0, 120)}
                      </p>
                    )}
                    <div className="flex items-center gap-2 mt-1 text-xs text-base-content/40">
                      {story.created_at && (
                        <time>{new Date(story.created_at).toLocaleDateString()}</time>
                      )}
                      {story.visibility && (
                        <span className={`badge badge-xs ${story.visibility === 'public' ? 'badge-success' : story.visibility === 'draft' ? 'badge-warning' : 'badge-ghost'}`}>
                          {story.visibility}
                        </span>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2 mt-3">
                      <Tag color={storyPalette.badgeColor}>{story.genre}</Tag>
                      {getStoryCharacters(story).slice(0, 3).map(char => (
                        <Tag key={char.entity_id} color="primary" icon={UserIcon} className="text-primary-content">
                          {char.name}
                        </Tag>
                      ))}
                      {getStoryCharacters(story).length > 3 && (
                        <Tag color="ghost">+{getStoryCharacters(story).length - 3}</Tag>
                      )}
                      {getStoryLocations(story).slice(0, 2).map(loc => (
                        <Tag key={loc.location_id} color="secondary" icon={MapPinIcon} className="text-secondary-content">
                          {loc.name}
                        </Tag>
                      ))}
                      {getStoryLocations(story).length > 2 && (
                        <Tag color="ghost">+{getStoryLocations(story).length - 2} địa điểm</Tag>
                      )}
                    </div>
                    {linkedStories.length > 0 && (
                      <div className="mt-3 pt-3 border-base-300 border-t">
                        <p className="opacity-70 mb-2 text-xs"><LinkIcon className="inline w-3 h-3" /> Liên kết với:</p>
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
                )
              })}
            </div>
            <hr className={palette.line} />
          </li>
        )
      })}
    </ul>
  )
}

export default WorldTimeline
