/**
 * TimelineControls - Control panel for the timeline canvas
 * Provides zoom controls and direction toggle
 */
function TimelineControls({ direction, onToggleDirection, onZoomIn, onZoomOut, onFitView }) {
  return (
    <div className="right-3 bottom-3 absolute flex flex-col gap-1 bg-base-100/90 shadow-md backdrop-blur-sm p-1 rounded-lg">
      {/* Fit view */}
      <div className="tooltip-left tooltip" data-tip="Vừa khung hình">
        <button onClick={onFitView} className="btn btn-ghost btn-xs btn-square">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
          </svg>
        </button>
      </div>

      {/* Zoom in */}
      <div className="tooltip-left tooltip" data-tip="Phóng to">
        <button onClick={onZoomIn} className="btn btn-ghost btn-xs btn-square">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
      </div>

      {/* Zoom out */}
      <div className="tooltip-left tooltip" data-tip="Thu nhỏ">
        <button onClick={onZoomOut} className="btn btn-ghost btn-xs btn-square">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 12H6" />
          </svg>
        </button>
      </div>

      {/* Divider */}
      <div className="my-0.5 border-base-300 border-t"></div>

      {/* Direction toggle */}
      <div className="tooltip-left tooltip" data-tip={direction === 'horizontal' ? 'Dọc' : 'Ngang'}>
        <button onClick={onToggleDirection} className="btn btn-ghost btn-xs btn-square">
          {direction === 'horizontal' ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          )}
        </button>
      </div>
    </div>
  )
}

export default TimelineControls
