import { useCallback, useMemo, useState } from 'react'
import {
  ReactFlow,
  Background,
  MiniMap,
  Handle,
  Position,
  useNodesState,
  useEdgesState,
  useReactFlow,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import EventNode from './EventNode'
import ConnectionLine from './ConnectionLine'
import TimelineControls from './TimelineControls'

/**
 * Convert timeline API data into React Flow nodes and edges
 */
function buildFlowData(timeline, direction, onEventClick) {
  if (!timeline?.years?.length) return { nodes: [], edges: [] }

  const nodes = []
  const edges = []
  const isHorizontal = direction === 'horizontal'

  // Layout constants
  const EVENT_GAP = isHorizontal ? 120 : 160
  const YEAR_LABEL_OFFSET = isHorizontal ? -60 : -40
  const MAX_EVENTS_PER_COL = isHorizontal ? 3 : Infinity // wrap into columns in horizontal mode
  const COL_WIDTH = 140 // horizontal spacing between columns within a year

  // Pre-calculate each year's width (number of columns) for dynamic YEAR_GAP
  const yearWidths = timeline.years.map((yearData) => {
    if (!isHorizontal) return 200
    const cols = Math.ceil(yearData.events.length / MAX_EVENTS_PER_COL)
    return Math.max(1, cols) * COL_WIDTH + 140 // extra padding
  })

  let yearOffset = 0

  timeline.years.forEach((yearData, yearIdx) => {
    const yearBaseX = isHorizontal ? yearOffset : 0
    const yearBaseY = isHorizontal ? 0 : yearIdx * 200

    // Year label node (not interactive)
    nodes.push({
      id: `year-${yearData.year}`,
      type: 'yearCluster',
      position: {
        x: isHorizontal ? yearBaseX + 40 : yearBaseX - 30,
        y: isHorizontal ? YEAR_LABEL_OFFSET : yearBaseY - 20,
      },
      data: {
        year: yearData.year,
        era: yearData.era,
        eventCount: yearData.events.length,
      },
      draggable: false,
      selectable: false,
    })

    // Event nodes within this year — wrap to multiple columns in horizontal mode
    yearData.events.forEach((event, eventIdx) => {
      let eventX, eventY

      if (isHorizontal) {
        const col = Math.floor(eventIdx / MAX_EVENTS_PER_COL)
        const row = eventIdx % MAX_EVENTS_PER_COL
        eventX = yearBaseX + 40 + col * COL_WIDTH
        eventY = 40 + row * EVENT_GAP
      } else {
        eventX = yearBaseX + eventIdx * EVENT_GAP
        eventY = yearBaseY + 50
      }

      const characterNames = event.character_details?.map(c => c.name)
        || event.metadata?.character_names
        || []
      const locationNames = event.location_details?.map(l => l.name)
        || event.metadata?.location_names
        || []

      nodes.push({
        id: event.event_id,
        type: 'eventNode',
        position: { x: eventX, y: eventY },
        data: {
          title: event.title,
          description: event.description,
          abstractImageSeed: event.metadata?.abstract_image_seed || event.title,
          storyId: event.story_id,
          storyTitle: event.story_title,
          storyPosition: event.story_position,
          characterNames,
          locationNames,
          onClick: () => onEventClick?.(event),
        },
      })
    })

    // Advance offset for next year
    yearOffset += yearWidths[yearIdx]
  })

  // Build edges from connections
  if (timeline.connections) {
    timeline.connections.forEach((conn, idx) => {
      edges.push({
        id: `conn-${idx}`,
        source: conn.from_event_id,
        target: conn.to_event_id,
        type: 'connectionLine',
        data: {
          relationType: conn.relation_type,
          relationLabel: conn.relation_label,
        },
        animated: conn.relation_type === 'temporal',
      })
    })
  }

  return { nodes, edges }
}

// Register custom node/edge types
const nodeTypes = {
  eventNode: EventNode,
  yearCluster: ({ data }) => (
    <div className="flex flex-col items-center">
      <div className="bg-primary/10 px-4 py-1.5 border border-primary/20 rounded-full">
        <span className="font-bold text-primary text-sm">
          {data.year === 0 ? 'Khởi đầu' : `Năm ${data.year}`}
        </span>
        {data.era && <span className="ml-1 text-primary/60 text-xs">({data.era})</span>}
      </div>
      {data.eventCount > 0 && (
        <span className="mt-1 text-[10px] text-base-content/50">{data.eventCount} sự kiện</span>
      )}
    </div>
  ),
}

const edgeTypes = {
  connectionLine: ConnectionLine,
}

/**
 * TimelineCanvas - React Flow canvas for event timeline
 */
function TimelineCanvas({ timeline, direction, onEventClick, onToggleDirection }) {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => buildFlowData(timeline, direction, onEventClick),
    [timeline, direction, onEventClick]
  )

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [hoveredNodeId, setHoveredNodeId] = useState(null)
  const reactFlowInstance = useReactFlow()

  // Update nodes/edges when timeline or direction changes
  useMemo(() => {
    const { nodes: newNodes, edges: newEdges } = buildFlowData(timeline, direction, onEventClick)
    setNodes(newNodes)
    setEdges(newEdges)
  }, [timeline, direction, onEventClick])

  // Compute visible edges based on hovered event node
  const { visibleNodes, visibleEdges } = useMemo(() => {
    if (!hoveredNodeId) {
      return {
        visibleNodes: nodes,
        visibleEdges: [],
      }
    }

    // Find edges connected to hovered node
    const connectedEdgeIds = new Set()

    edges.forEach(e => {
      if (e.source === hoveredNodeId || e.target === hoveredNodeId) {
        connectedEdgeIds.add(e.id)
      }
    })

    return {
      visibleNodes: nodes,
      visibleEdges: edges.filter(e => connectedEdgeIds.has(e.id)),
    }
  }, [hoveredNodeId, nodes, edges])

  const onNodeMouseEnter = useCallback((_event, node) => {
    if (node.type === 'eventNode') {
      setHoveredNodeId(node.id)
    }
  }, [])

  const onNodeMouseLeave = useCallback(() => {
    setHoveredNodeId(null)
  }, [])

  const onNodeClick = useCallback((event, node) => {
    if (node.type === 'eventNode' && node.data.onClick) {
      node.data.onClick()
    }
  }, [])

  const handleZoomIn = useCallback(() => {
    reactFlowInstance.zoomIn({ duration: 200 })
  }, [reactFlowInstance])

  const handleZoomOut = useCallback(() => {
    reactFlowInstance.zoomOut({ duration: 200 })
  }, [reactFlowInstance])

  const handleFitView = useCallback(() => {
    reactFlowInstance.fitView({ padding: 0.2, duration: 300 })
  }, [reactFlowInstance])

  if (!timeline?.years?.length) {
    return (
      <div className="flex justify-center items-center h-80 text-base-content/40">
        <div className="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="opacity-20 mx-auto mb-3 w-16 h-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <p className="text-sm">Chưa có sự kiện nào</p>
          <p className="mt-1 text-xs">Nhấn "Trích xuất sự kiện" để phân tích câu chuyện</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative rounded-lg w-full h-96 overflow-hidden" style={{ minHeight: '400px' }}>
      <ReactFlow
        nodes={visibleNodes}
        edges={visibleEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onNodeMouseEnter={onNodeMouseEnter}
        onNodeMouseLeave={onNodeMouseLeave}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        minZoom={0.3}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#aaa" gap={20} size={1} />
        <MiniMap
          nodeStrokeWidth={3}
          zoomable
          pannable
          className="!bg-base-200/80 !rounded-lg"
          style={{ width: 120, height: 80 }}
        />
      </ReactFlow>

      <TimelineControls
        direction={direction}
        onToggleDirection={onToggleDirection}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onFitView={handleFitView}
      />
    </div>
  )
}

export default TimelineCanvas
