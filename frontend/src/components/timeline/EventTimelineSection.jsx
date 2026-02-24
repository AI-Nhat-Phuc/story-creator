import { useState, useEffect, useRef } from 'react'
import EventTimelineContainer from '../../containers/EventTimelineContainer'

/**
 * Event Timeline Section - Lazy-loaded section on Dashboard
 * Features:
 * - Toggle bar to expand/collapse
 * - World dropdown selector
 * - Lazy loads when scrolled into view
 * - Persists preferences in localStorage
 * - Receives worlds list from parent (avoids extra API call)
 */
function EventTimelineSection({ showToast, worldsList = [] }) {
  const [expanded, setExpanded] = useState(() => {
    try {
      const prefs = JSON.parse(localStorage.getItem('timelinePrefs') || '{}')
      return prefs.expanded ?? false
    } catch { return false }
  })

  const [worlds, setWorlds] = useState(worldsList)
  const [selectedWorldId, setSelectedWorldId] = useState(() => {
    return localStorage.getItem('lastViewedWorldId') || ''
  })
  const [direction, setDirection] = useState(() => {
    try {
      const prefs = JSON.parse(localStorage.getItem('timelinePrefs') || '{}')
      return prefs.direction ?? 'horizontal'
    } catch { return 'horizontal' }
  })
  const [isVisible, setIsVisible] = useState(false)
  const sectionRef = useRef(null)

  // Force vertical on mobile
  const effectiveDirection = typeof window !== 'undefined' && window.innerWidth < 768 ? 'vertical' : direction

  // IntersectionObserver for lazy loading
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      { threshold: 0.1 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => observer.disconnect()
  }, [])

  // Sync worlds from props
  useEffect(() => {
    setWorlds(worldsList)
  }, [worldsList])

  // Auto-select world
  useEffect(() => {
    if (worlds.length > 0 && !selectedWorldId) {
      // Default to most recently created world
      const sorted = [...worlds].sort((a, b) =>
        new Date(b.created_at) - new Date(a.created_at)
      )
      setSelectedWorldId(sorted[0]?.world_id || '')
    }
  }, [worlds, selectedWorldId])

  // Persist preferences
  useEffect(() => {
    localStorage.setItem('timelinePrefs', JSON.stringify({ expanded, direction }))
  }, [expanded, direction])

  useEffect(() => {
    if (selectedWorldId) {
      localStorage.setItem('lastViewedWorldId', selectedWorldId)
    }
  }, [selectedWorldId])

  const toggleDirection = () => {
    setDirection(prev => prev === 'horizontal' ? 'vertical' : 'horizontal')
  }

  const selectedWorld = worlds.find(w => w.world_id === selectedWorldId)

  return (
    <div ref={sectionRef} className="mt-8">
      {/* Toggle Bar */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex justify-between items-center bg-base-200 hover:bg-base-300 px-6 py-3 rounded-box w-full transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span className="font-semibold">
            Timeline Sự kiện
            {selectedWorld && <span className="ml-2 text-sm text-base-content/60">— {selectedWorld.name}</span>}
          </span>
        </div>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className={`w-5 h-5 transition-transform duration-300 ${expanded ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expandable Content */}
      <div className={`transition-all duration-500 overflow-hidden ${expanded ? 'max-h-[2000px] opacity-100 mt-4' : 'max-h-0 opacity-0'}`}>
        <div className="bg-base-100 shadow rounded-box">
          {/* Header with controls */}
          <div className="flex flex-wrap justify-between items-center gap-3 px-6 py-4 border-base-200 border-b">
            <div className="flex items-center gap-3">
              {/* World Dropdown */}
              <select
                className="w-64 select-bordered select-sm select"
                value={selectedWorldId}
                onChange={(e) => setSelectedWorldId(e.target.value)}
              >
                <option value="" disabled>Chọn thế giới...</option>
                {worlds.map(w => (
                  <option key={w.world_id} value={w.world_id}>
                    {w.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              {/* Direction Toggle */}
              <div className="tooltip" data-tip={direction === 'horizontal' ? 'Chuyển sang dọc' : 'Chuyển sang ngang'}>
                <button
                  onClick={toggleDirection}
                  className="btn btn-ghost btn-sm btn-square"
                >
                  {direction === 'horizontal' ? (
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12M8 12h12M8 17h12M4 7h.01M4 12h.01M4 17h.01" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Timeline Canvas */}
          <div className="p-4" style={{ minHeight: '400px' }}>
            {selectedWorldId ? (
              <EventTimelineContainer
                worldId={selectedWorldId}
                direction={effectiveDirection}
                showToast={showToast}
              />
            ) : (
              <div className="flex justify-center items-center h-64 text-base-content/50">
                <div className="text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="opacity-30 mx-auto mb-3 w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064" />
                  </svg>
                  <p>Chọn một thế giới để xem timeline sự kiện</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default EventTimelineSection
