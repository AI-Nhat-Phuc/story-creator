import { memo } from 'react'
import { getBezierPath } from '@xyflow/react'
import {
  UserIcon,
  MapPinIcon,
  BoltIcon,
  ClockIcon,
} from '@heroicons/react/24/solid'

/**
 * Color map for different connection types
 */
const CONNECTION_COLORS = {
  character: '#3b82f6',  // Blue
  location: '#22c55e',   // Green
  causation: '#ef4444',  // Red
  temporal: '#eab308',   // Yellow
}

const CONNECTION_ICONS = {
  character: UserIcon,
  location: MapPinIcon,
  causation: BoltIcon,
  temporal: ClockIcon,
}

/**
 * ConnectionLine - Custom React Flow edge with color based on relation type
 */
const ConnectionLine = memo(({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  style = {},
  markerEnd,
}) => {
  const relationType = data?.relationType || 'temporal'
  const relationLabel = data?.relationLabel || ''
  const color = CONNECTION_COLORS[relationType] || CONNECTION_COLORS.temporal

  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  })

  return (
    <>
      {/* Edge path */}
      <path
        id={id}
        className="react-flow__edge-path"
        d={edgePath}
        style={{
          stroke: color,
          strokeWidth: 2,
          strokeDasharray: relationType === 'temporal' ? '5,5' : 'none',
          opacity: 0.7,
          ...style,
        }}
        markerEnd={markerEnd}
      />

      {/* Edge label */}
      {relationLabel && (
        <foreignObject
          width={120}
          height={30}
          x={labelX - 60}
          y={labelY - 15}
          className="pointer-events-none"
        >
          <div className="flex justify-center items-center h-full">
            <span
              className="flex items-center gap-0.5 bg-base-100/90 px-1.5 py-0.5 rounded-md text-[9px] whitespace-nowrap"
              style={{ color, borderColor: color, borderWidth: 1 }}
            >
              {(() => { const Icon = CONNECTION_ICONS[relationType]; return Icon ? <Icon className="w-2.5 h-2.5" /> : null })()}
              {relationLabel}
            </span>
          </div>
        </foreignObject>
      )}
    </>
  )
})

ConnectionLine.displayName = 'ConnectionLine'

export default ConnectionLine
