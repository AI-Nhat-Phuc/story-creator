import { memo } from 'react'

/**
 * YearCluster - Group node representing a year in the timeline.
 * Contains visual grouping for events that happen in the same year.
 */
const YearCluster = memo(({ data }) => {
  const { year, era, eventCount } = data

  return (
    <div className="flex flex-col items-center">
      {/* Year Label */}
      <div className="bg-primary/10 mb-2 px-4 py-1.5 border border-primary/20 rounded-full">
        <span className="font-bold text-primary text-sm">
          {year === 0 ? 'Thời kỳ khởi đầu' : `Năm ${year}`}
        </span>
        {era && (
          <span className="ml-1.5 text-primary/60 text-xs">({era})</span>
        )}
      </div>

      {/* Event count badge */}
      {eventCount > 0 && (
        <div className="badge badge-primary badge-xs">
          {eventCount} sự kiện
        </div>
      )}
    </div>
  )
})

YearCluster.displayName = 'YearCluster'

export default YearCluster
