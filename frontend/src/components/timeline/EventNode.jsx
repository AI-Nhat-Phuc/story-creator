import { memo } from 'react'
import { Handle, Position } from '@xyflow/react'
import {
  BookOpenIcon,
  UserIcon,
  MapPinIcon,
} from '@heroicons/react/24/solid'

/**
 * Generate abstract gradient style from a seed string.
 */
function generateAbstractStyle(seed) {
  let hash = 0
  for (let i = 0; i < seed.length; i++) {
    const char = seed.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  hash = Math.abs(hash)
  const hue1 = hash % 360
  const hue2 = (hash * 7) % 360
  const hue3 = (hash * 13) % 360
  return {
    background: `radial-gradient(circle at 30% 30%, hsl(${hue1}, 70%, 65%), hsl(${hue2}, 60%, 45%), hsl(${hue3}, 50%, 30%))`
  }
}

/**
 * EventNode - Custom React Flow node for timeline events
 *
 * Renders a circle with abstract gradient + short description below
 */
const EventNode = memo(({ data, selected }) => {
  const { title, description, abstractImageSeed, storyTitle, characterNames, locationNames } = data
  const gradientStyle = generateAbstractStyle(abstractImageSeed || title || 'default')

  return (
    <div
      className={`flex flex-col items-center gap-2 group ${selected ? 'scale-110' : ''} transition-transform`}
      style={{ zIndex: 1 }}
      onMouseEnter={(e) => {
        // Elevate the React Flow node wrapper above siblings
        const wrapper = e.currentTarget.closest('.react-flow__node')
        if (wrapper) wrapper.style.zIndex = '1000'
      }}
      onMouseLeave={(e) => {
        const wrapper = e.currentTarget.closest('.react-flow__node')
        if (wrapper) wrapper.style.zIndex = ''
      }}
    >
      {/* Event Circle with embedded handles */}
      <div
        className="relative shadow-lg rounded-full ring-2 ring-base-300 group-hover:ring-primary w-14 h-14 transition-all cursor-pointer"
        style={gradientStyle}
        title={`${title}\n${description}`}
      >
        <Handle
          type="target"
          position={Position.Left}
          className="!bg-transparent !border-0 !w-0 !min-w-0 !h-0 !min-h-0"
        />
        <Handle
          type="source"
          position={Position.Right}
          className="!bg-transparent !border-0 !w-0 !min-w-0 !h-0 !min-h-0"
        />
      </div>

      {/* Event Title */}
      <div className="max-w-28 text-center">
        <p className="font-semibold text-xs line-clamp-1 leading-tight">{title}</p>
      </div>

      {/* Tooltip on hover */}
      <div className="-bottom-2 left-1/2 z-50 absolute bg-base-300 opacity-0 group-hover:opacity-100 shadow-lg p-2 rounded-lg min-w-48 transition-opacity -translate-x-1/2 translate-y-full pointer-events-none">
        <p className="font-bold text-xs">{title}</p>
        <p className="mt-1 text-[10px] text-base-content/70">{description}</p>
        {storyTitle && (
          <p className="mt-1 text-[10px]">
            <BookOpenIcon className="inline w-2.5 h-2.5 text-secondary" /> {storyTitle}
          </p>
        )}
        {characterNames?.length > 0 && (
          <p className="mt-0.5 text-[10px]">
            <UserIcon className="inline w-2.5 h-2.5 text-primary" /> {characterNames.join(', ')}
          </p>
        )}
        {locationNames?.length > 0 && (
          <p className="mt-0.5 text-[10px]">
            <MapPinIcon className="inline w-2.5 h-2.5 text-accent" /> {locationNames.join(', ')}
          </p>
        )}
      </div>
    </div>
  )
})

EventNode.displayName = 'EventNode'

export default EventNode
