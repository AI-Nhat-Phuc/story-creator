import React from 'react'
import { ClockIcon } from '@heroicons/react/24/outline'

function StoryTimeSelector({ timeIndex, onChange, worldCalendar, compact = false }) {
  const calculateYear = (idx) => {
    if (!worldCalendar || !idx) return null
    const currentYear = worldCalendar.current_year || 1
    return Math.max(1, currentYear + idx - 50)
  }

  const year = calculateYear(timeIndex)
  const era = worldCalendar?.current_era || ''
  const yearName = worldCalendar?.year_name || 'Năm'

  if (compact) {
    return (
      <div className="flex items-center gap-2 min-w-0 flex-1">
        <ClockIcon className="w-3.5 h-3.5 shrink-0 text-base-content/60" />
        <span className="text-xs font-semibold text-base-content/60 uppercase tracking-wider shrink-0 hidden sm:inline">
          Thời điểm
        </span>
        <input
          type="range"
          min="0"
          max="100"
          value={timeIndex}
          onChange={(e) => onChange(Number(e.target.value))}
          className="range range-xs range-primary flex-1 min-w-[60px] max-w-[180px]"
        />
        <span className="text-xs text-base-content/70 shrink-0 whitespace-nowrap">
          {!timeIndex ? (
            <span className="opacity-50">Chưa xác định</span>
          ) : (
            <>
              {yearName} {year}
              {era && <span className="opacity-60 ml-1 hidden sm:inline">({era})</span>}
            </>
          )}
        </span>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <div className="text-xs font-semibold text-base-content/60 uppercase tracking-wider flex items-center gap-1">
        <ClockIcon className="w-3.5 h-3.5" />
        Thời điểm
      </div>
      <input
        type="range"
        min="0"
        max="100"
        value={timeIndex}
        onChange={(e) => onChange(Number(e.target.value))}
        className="range range-xs range-primary w-full"
      />
      <div className="text-xs text-center text-base-content/70 min-h-[1.25rem]">
        {!timeIndex ? (
          <span className="opacity-50">Chưa xác định</span>
        ) : (
          <span>
            {yearName} {year}
            {era && <span className="opacity-60 ml-1">({era})</span>}
          </span>
        )}
      </div>
    </div>
  )
}

export default StoryTimeSelector
