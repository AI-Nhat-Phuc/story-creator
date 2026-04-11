import React, { useRef, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import GptButton from '../GptButton'
import AnalyzedEntitiesEditor from '../AnalyzedEntitiesEditor'
import Tag from '../Tag'
import { marked } from 'marked'
import {
  GlobeAltIcon,
  UserIcon,
  MapPinIcon,
  ClockIcon,
  ClipboardDocumentListIcon,
  PencilIcon,
  XMarkIcon,
  TrashIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'
import { ArrowDownTrayIcon } from '@heroicons/react/24/solid'

function StoryDetailView({
  story,
  world,
  linkedCharacters = [],
  linkedLocations = [],
  formattedWorldTime,
  displayWorldTime,
  normalizedTimelineIndex,
  gptAnalyzing,
  analyzedEntities,
  onAnalyzeStory,
  onClearAnalyzedEntities,
  onUpdateAnalyzedEntities,
  onLinkEntities,
  showAnalyzedModal,
  onCloseAnalyzedModal,
  onReanalyzeStory,
  canEdit = false,
  onDeleteStory,
  highlightEventId,
  highlightPosition = -1
}) {
  const highlightRef = useRef(null)
  const [showAnalysisPanel, setShowAnalysisPanel] = useState(false)

  useEffect(() => {
    if (highlightPosition >= 0 && highlightRef.current) {
      setTimeout(() => {
        highlightRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 300)
    }
  }, [highlightPosition])

  const renderStoryContent = () => {
    if (!story.content) return null

    // HTML or markdown — render as rich HTML
    if (story.format === 'html' || story.format === 'markdown') {
      const html = story.format === 'markdown' ? marked.parse(story.content) : story.content
      return (
        <div
          className="prose prose-sm max-w-none"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      )
    }

    // Plain/markdown: paragraph-by-paragraph with highlight support
    const paragraphs = story.content.split('\n')

    // Resolve highlight: if target paragraph is empty, find nearest non-empty one
    let effectiveHighlight = highlightPosition
    if (effectiveHighlight >= 0) {
      if (effectiveHighlight >= paragraphs.length || !paragraphs[effectiveHighlight]?.trim()) {
        let closest = -1
        let minDist = Infinity
        paragraphs.forEach((p, i) => {
          if (p.trim() && Math.abs(i - effectiveHighlight) < minDist) {
            minDist = Math.abs(i - effectiveHighlight)
            closest = i
          }
        })
        effectiveHighlight = closest
      }
    }

    if (effectiveHighlight < 0) {
      return <p className="text-lg whitespace-pre-wrap">{story.content}</p>
    }

    return (
      <div className="text-lg whitespace-pre-wrap">
        {paragraphs.map((para, idx) => {
          const isHighlighted = idx === effectiveHighlight
          return (
            <p
              key={idx}
              ref={isHighlighted ? highlightRef : undefined}
              className={
                isHighlighted
                  ? 'bg-warning/20 border-l-4 border-warning pl-3 py-1 rounded-r transition-colors duration-700'
                  : ''
              }
            >
              {para || '\u00A0'}
            </p>
          )
        })}
      </div>
    )
  }

  const hasLinks = linkedCharacters.length > 0 || linkedLocations.length > 0

  return (
    <div className="overflow-x-hidden">
      <div className="flex flex-wrap gap-2 mb-4">
        <Link to="/stories" className="btn btn-ghost btn-sm">
          ← Quay lại danh sách
        </Link>
        {world && (
          <Link to={`/worlds/${world.world_id}`} className="btn btn-ghost btn-sm min-w-0 max-w-[65vw]">
            <GlobeAltIcon className="w-4 h-4 shrink-0" />
            <span className="truncate">Về thế giới {world.name}</span>
          </Link>
        )}
      </div>

      <div className="flex gap-0 items-start">
        {/* Main content */}
        <div className="flex-1 min-w-0">
          <div className="bg-base-100 shadow-xl mb-6 p-6 rounded-box">
            <div className="flex justify-between items-start mb-2">
              <h1 className="font-bold text-3xl">{story.title}</h1>
              <div className="flex gap-1 items-center">
                <a
                  href={`/stories/${story.story_id}/print`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline btn-sm gap-1"
                >
                  <ArrowDownTrayIcon className="w-4 h-4" /> Export PDF
                </a>
                {canEdit && (
                  <>
                    <Link to={`/stories/${story.story_id}/edit`} className="btn btn-sm btn-ghost">
                      <PencilIcon className="inline w-4 h-4" /> <span className="hidden sm:inline">Sửa</span>
                    </Link>
                    {onDeleteStory && (
                      <button onClick={onDeleteStory} className="text-error btn btn-sm btn-ghost" title="Xóa">
                        <TrashIcon className="inline w-4 h-4" /> <span className="hidden sm:inline">Xóa</span>
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>
            <div className="flex flex-wrap gap-2 mb-4">
              <Tag color="neutral" icon={ClockIcon} title={`Time index: ${normalizedTimelineIndex ?? 0}`}>
                {formattedWorldTime}
              </Tag>
              {story.visibility && (
                <Tag color={story.visibility === 'public' ? 'success' : story.visibility === 'draft' ? 'warning' : 'ghost'}>
                  {story.visibility === 'public' ? 'Công khai' : story.visibility === 'draft' ? 'Bản nháp' : 'Riêng tư'}
                </Tag>
              )}
              {world && (
                <Tag as={Link} to={`/worlds/${world.world_id}`} color="info" icon={GlobeAltIcon} className="cursor-pointer hover:badge-info-focus">
                  {world.name}
                </Tag>
              )}
            </div>
            {renderStoryContent()}
          </div>

          <div className="bg-base-100 shadow-xl p-6 rounded-box">
            <h2 className="mb-4 font-bold text-2xl"><ClipboardDocumentListIcon className="inline w-6 h-6" /> Thông tin chi tiết</h2>
            <div className="overflow-x-auto">
              <table className="table table-zebra w-full">
                <tbody>
                  <tr>
                    <td className="font-semibold">ID</td>
                    <td className="font-mono text-sm">{story.story_id}</td>
                  </tr>
                  <tr>
                    <td className="font-semibold">Thế giới</td>
                    <td>
                      {world ? (
                        <Link to={`/worlds/${world.world_id}`} className="link link-info">
                          {world.name}
                        </Link>
                      ) : (
                        'N/A'
                      )}
                    </td>
                  </tr>
                  <tr>
                    <td className="font-semibold">Thời điểm</td>
                    <td>
                      <div>{formattedWorldTime}</div>
                      {displayWorldTime?.era && (
                        <div className="opacity-60 mt-1 text-xs">
                          Kỷ nguyên: {displayWorldTime.era}
                        </div>
                      )}
                      {displayWorldTime?.year > 0 && (
                        <div className="opacity-60 text-xs">
                          Niên đại: {(displayWorldTime.year_name || 'Năm')} {displayWorldTime.year}
                        </div>
                      )}
                      {normalizedTimelineIndex !== null && normalizedTimelineIndex !== 0 ? (
                        <div className="opacity-50 mt-1 text-xs">
                          Chỉ số timeline: {normalizedTimelineIndex}
                        </div>
                      ) : (
                        <div className="opacity-50 mt-1 text-xs">
                          Mốc thời gian chưa xác định
                        </div>
                      )}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Desktop: Analysis panel sidebar (hidden on mobile) */}
        {story.content && (
          <div className="hidden sm:flex items-start ml-2 mt-0">
            <button
              onClick={() => setShowAnalysisPanel(v => !v)}
              className="btn btn-ghost btn-sm px-1.5 py-6 h-auto rounded-l-lg rounded-r-none border border-base-300 border-r-0 bg-base-100 shadow"
              title={showAnalysisPanel ? 'Đóng phân tích' : 'Mở phân tích'}
            >
              <span className="font-mono text-base-content/60 text-xs leading-none" style={{ writingMode: 'vertical-rl' }}>
                {showAnalysisPanel ? '>>' : '<<'}
              </span>
            </button>

            {showAnalysisPanel && (
              <div className="bg-base-100 shadow-xl border border-base-300 rounded-r-box w-72 shrink-0 overflow-hidden">
                <div className="bg-base-200 px-4 py-3 border-b border-base-300">
                  <h3 className="flex items-center gap-2 font-semibold text-sm">
                    <SparklesIcon className="w-4 h-4 text-warning" />
                    Phân tích AI
                  </h3>
                </div>
                <div className="p-4 space-y-4">
                  {!analyzedEntities && (
                    <>
                      {!hasLinks && (
                        <GptButton onClick={onAnalyzeStory} loading={gptAnalyzing} loadingText="Đang phân tích..." variant="primary" size="sm">
                          Phân tích nhân vật & địa điểm
                        </GptButton>
                      )}
                      {hasLinks && (
                        <GptButton onClick={onReanalyzeStory} loading={gptAnalyzing} loadingText="Đang phân tích lại..." variant="warning" size="sm">
                          Phân tích lại
                        </GptButton>
                      )}
                    </>
                  )}
                  {linkedCharacters.length > 0 && (
                    <div>
                      <div className="flex items-center gap-1 mb-2 text-xs font-semibold text-base-content/60 uppercase tracking-wide">
                        <UserIcon className="w-3.5 h-3.5" /> Nhân vật
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {linkedCharacters.map((char) => (
                          <Tag key={char.entity_id} color="primary" size="sm" icon={UserIcon}>{char.name}</Tag>
                        ))}
                      </div>
                    </div>
                  )}
                  {linkedLocations.length > 0 && (
                    <div>
                      <div className="flex items-center gap-1 mb-2 text-xs font-semibold text-base-content/60 uppercase tracking-wide">
                        <MapPinIcon className="w-3.5 h-3.5" /> Địa điểm
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {linkedLocations.map((loc) => (
                          <Tag key={loc.location_id} color="secondary" size="sm" icon={MapPinIcon}>{loc.name}</Tag>
                        ))}
                      </div>
                    </div>
                  )}
                  {!hasLinks && !gptAnalyzing && !analyzedEntities && (
                    <p className="text-base-content/40 text-xs italic">Chưa có liên kết nhân vật hay địa điểm nào.</p>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Mobile: FAB to open analysis bottom sheet */}
      {story.content && (
        <button
          onClick={() => setShowAnalysisPanel(v => !v)}
          className="sm:hidden fixed bottom-24 right-4 z-40 btn btn-circle shadow-lg bg-base-100 border border-base-300"
          title="Phân tích AI"
        >
          <SparklesIcon className="w-5 h-5 text-warning" />
        </button>
      )}

      {/* Mobile: Analysis bottom sheet modal */}
      {story.content && showAnalysisPanel && (
        <div
          className="sm:hidden modal modal-open modal-bottom-sheet"
          onClick={() => setShowAnalysisPanel(false)}
        >
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="flex items-center gap-2 font-semibold">
                <SparklesIcon className="w-4 h-4 text-warning" />
                Phân tích AI
              </h3>
              <button className="btn btn-ghost btn-sm btn-circle" onClick={() => setShowAnalysisPanel(false)}>
                <XMarkIcon className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-4">
              {!analyzedEntities && (
                <>
                  {!hasLinks && (
                    <GptButton onClick={onAnalyzeStory} loading={gptAnalyzing} loadingText="Đang phân tích..." variant="primary" size="sm">
                      Phân tích nhân vật & địa điểm
                    </GptButton>
                  )}
                  {hasLinks && (
                    <GptButton onClick={onReanalyzeStory} loading={gptAnalyzing} loadingText="Đang phân tích lại..." variant="warning" size="sm">
                      Phân tích lại
                    </GptButton>
                  )}
                </>
              )}
              {linkedCharacters.length > 0 && (
                <div>
                  <div className="flex items-center gap-1 mb-2 text-xs font-semibold text-base-content/60 uppercase tracking-wide">
                    <UserIcon className="w-3.5 h-3.5" /> Nhân vật
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {linkedCharacters.map((char) => (
                      <Tag key={char.entity_id} color="primary" size="sm" icon={UserIcon}>{char.name}</Tag>
                    ))}
                  </div>
                </div>
              )}
              {linkedLocations.length > 0 && (
                <div>
                  <div className="flex items-center gap-1 mb-2 text-xs font-semibold text-base-content/60 uppercase tracking-wide">
                    <MapPinIcon className="w-3.5 h-3.5" /> Địa điểm
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {linkedLocations.map((loc) => (
                      <Tag key={loc.location_id} color="secondary" size="sm" icon={MapPinIcon}>{loc.name}</Tag>
                    ))}
                  </div>
                </div>
              )}
              {!hasLinks && !gptAnalyzing && !analyzedEntities && (
                <p className="text-base-content/40 text-sm italic">Chưa có liên kết nhân vật hay địa điểm nào.</p>
              )}
            </div>
          </div>
          <div className="modal-backdrop" onClick={() => setShowAnalysisPanel(false)}></div>
        </div>
      )}

      {/* GPT Analyzed Entities Modal */}
      <AnalyzedEntitiesEditor
        open={showAnalyzedModal}
        analyzedEntities={analyzedEntities}
        onUpdate={onUpdateAnalyzedEntities}
        onClose={onCloseAnalyzedModal}
        onClear={onClearAnalyzedEntities}
        onLink={onLinkEntities}
        linkLabel="Xác nhận liên kết"
      />
    </div>
  )
}

export default StoryDetailView
