import { Link } from 'react-router-dom'
import {
  UserIcon,
  MapPinIcon,
  LinkIcon,
  ClockIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'

function WorldTimeline({ stories, characters = [], locations = [], getStoryWorldTime, getTimelineLabel, onDeleteStory }) {
  if (!stories || stories.length === 0) {
    return <p className="opacity-60 py-8 text-center">Chưa có câu chuyện nào</p>
  }

  const paletteMap = {
    adventure: { line: 'bg-primary', iconText: 'text-primary', iconBorder: 'border-primary', badge: 'badge-success' },
    mystery: { line: 'bg-secondary', iconText: 'text-secondary', iconBorder: 'border-secondary', badge: 'badge-secondary' },
    conflict: { line: 'bg-error', iconText: 'text-error', iconBorder: 'border-error', badge: 'badge-error' },
    discovery: { line: 'bg-info', iconText: 'text-info', iconBorder: 'border-info', badge: 'badge-info' }
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

  const sortedStories = [...stories].sort((a, b) => {
    const yearA = getStoryWorldTime(a)?.year ?? (a.time_index || 0)
    const yearB = getStoryWorldTime(b)?.year ?? (b.time_index || 0)
    return yearA - yearB
  })

  // Group stories by year/time_index
  const groupedByYear = sortedStories.reduce((acc, story) => {
    const worldTime = getStoryWorldTime(story)
    const yearKey = worldTime?.year ?? story.time_index ?? 'unknown'
    if (!acc[yearKey]) {
      acc[yearKey] = []
    }
    acc[yearKey].push(story)
    return acc
  }, {})

  const yearGroups = Object.entries(groupedByYear).map(([yearKey, storiesInYear]) => ({
    yearKey,
    stories: storiesInYear,
    worldTime: getStoryWorldTime(storiesInYear[0]),
    timeLabel: getTimelineLabel(storiesInYear[0])
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
          badge: 'badge-accent'
        }

        return (
          <li key={group.yearKey}>
            {groupIndex === 0 && <hr className={palette.line} />}
            <div className="text-left md:text-right timeline-start">
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
            <div className="space-y-3 timeline-end">
              {group.stories.map((story) => {
                const storyWorldTime = getStoryWorldTime(story)
                const storyPalette = paletteMap[story.genre] || {
                  line: 'bg-accent',
                  iconText: 'text-accent',
                  iconBorder: 'border-accent',
                  badge: 'badge-accent'
                }

                // Get linked stories
                const linkedStoryIds = story.linked_stories || []
                const linkedStories = linkedStoryIds
                  .map(id => sortedStories.find(s => s.story_id === id))
                  .filter(Boolean)

                return (
                  <div key={story.story_id} className="bg-base-100 shadow-lg p-4 timeline-box">
                    <div className="flex justify-between items-start">
                      <Link to={`/stories/${story.story_id}`} className="link link-hover">
                        <h3 className="font-bold text-xl">{story.title}</h3>
                      </Link>
                      {onDeleteStory && (
                        <button
                          onClick={(e) => { e.preventDefault(); onDeleteStory(story.story_id, story.title) }}
                          className="opacity-40 hover:opacity-100 text-error btn btn-ghost btn-xs"
                          title="Xóa câu chuyện"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2 mt-3">
                      <span className={`badge ${storyPalette.badge}`}>{story.genre}</span>
                      {getStoryCharacters(story).slice(0, 3).map(char => (
                        <span key={char.entity_id} className="text-primary-content badge badge-primary">
                          <UserIcon className="inline w-3 h-3" /> {char.name}
                        </span>
                      ))}
                      {getStoryCharacters(story).length > 3 && (
                        <span className="badge badge-ghost">+{getStoryCharacters(story).length - 3}</span>
                      )}
                      {getStoryLocations(story).slice(0, 2).map(loc => (
                        <span key={loc.location_id} className="text-secondary-content badge badge-secondary">
                          <MapPinIcon className="inline w-3 h-3" /> {loc.name}
                        </span>
                      ))}
                      {getStoryLocations(story).length > 2 && (
                        <span className="badge badge-ghost">+{getStoryLocations(story).length - 2} địa điểm</span>
                      )}
                    </div>
                    {linkedStories.length > 0 && (
                      <div className="mt-3 pt-3 border-base-300 border-t">
                        <p className="opacity-70 mb-2 text-xs"><LinkIcon className="inline w-3 h-3" /> Liên kết với:</p>
                        <div className="flex flex-wrap gap-1">
                          {linkedStories.map(linked => (
                            <Link
                              key={linked.story_id}
                              to={`/stories/${linked.story_id}`}
                              className="badge-outline badge badge-sm hover:badge-secondary"
                            >
                              {linked.title}
                            </Link>
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
