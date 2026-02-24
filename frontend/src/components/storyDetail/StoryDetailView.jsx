import React, { useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import GptButton from '../GptButton'
import AnalyzedEntitiesEditor from '../AnalyzedEntitiesEditor'
import {
  GlobeAltIcon,
  UserIcon,
  MapPinIcon,
  ClockIcon,
  ClipboardDocumentListIcon,
  PencilIcon,
  XMarkIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'
import { ArrowDownTrayIcon } from '@heroicons/react/24/solid'

function StoryDetailView({
  story,
  world,
  linkedCharacters = [],
  linkedLocations = [],
  editing,
  editForm,
  formattedWorldTime,
  displayWorldTime,
  normalizedTimelineIndex,
  gptAnalyzing,
  analyzedEntities,
  onEdit,
  onCancelEdit,
  onSaveEdit,
  onChangeForm,
  onAnalyzeStory,
  onClearAnalyzedEntities,
  onUpdateAnalyzedEntities,
  onLinkEntities,
  showAnalyzedModal,
  onCloseAnalyzedModal,
  onReanalyzeStory,
  onDeleteStory,
  highlightEventId,
  highlightPosition = -1
}) {
  const highlightRef = useRef(null)

  useEffect(() => {
    if (highlightPosition >= 0 && highlightRef.current) {
      setTimeout(() => {
        highlightRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 300)
    }
  }, [highlightPosition])

  const renderStoryContent = () => {
    if (!story.content) return null
    const paragraphs = story.content.split('\n')

    // Resolve highlight: if target paragraph is empty, find nearest non-empty one
    let effectiveHighlight = highlightPosition
    if (effectiveHighlight >= 0) {
      if (effectiveHighlight >= paragraphs.length || !paragraphs[effectiveHighlight]?.trim()) {
        // Find nearest non-empty paragraph
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
  return (
    <div>
      <div className="flex gap-2 mb-4">
        <Link to="/stories" className="btn btn-ghost btn-sm">
          ← Quay lại danh sách
        </Link>
        {world && (
          <Link to={`/worlds/${world.world_id}`} className="btn btn-ghost btn-sm">
            <GlobeAltIcon className="inline w-4 h-4" /> Về thế giới {world.name}
          </Link>
        )}
      </div>

      <div className="bg-base-100 shadow-xl mb-6 p-6 rounded-box">
        {editing ? (
          <>
            <input
              type="text"
              value={editForm.title}
              onChange={(e) => onChangeForm('title', e.target.value)}
              className="mb-4 w-full font-bold text-3xl input input-bordered"
              placeholder="Tiêu đề câu chuyện"
            />
            <textarea
              value={editForm.content}
              onChange={(e) => onChangeForm('content', e.target.value)}
              className="mb-4 w-full min-h-[200px] textarea textarea-bordered"
              placeholder="Mô tả câu chuyện"
            />
            <div className="mb-4 form-control">
              <label className="label">
                <span className="font-semibold label-text">Chế độ hiển thị</span>
              </label>
              <select
                value={editForm.visibility}
                onChange={(e) => onChangeForm('visibility', e.target.value)}
                className="w-full max-w-xs select-bordered select"
              >
                <option value="draft">Bản nháp - Chỉ bạn thấy, đang viết</option>
                <option value="private">Riêng tư - Chỉ bạn có thể xem</option>
                <option value="public">Công khai - Mọi người có thể xem</option>
              </select>
            </div>
            <div className="flex gap-2">
              <button onClick={onSaveEdit} className="btn btn-primary">
                <ArrowDownTrayIcon className="inline w-4 h-4" /> Lưu
              </button>
              <button onClick={onCancelEdit} className="btn btn-ghost">
                <XMarkIcon className="inline w-4 h-4" /> Hủy
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="flex justify-between items-start mb-2">
              <h1 className="font-bold text-3xl">{story.title}</h1>
              <div className="flex gap-1">
                <button onClick={onEdit} className="btn btn-sm btn-ghost">
                  <PencilIcon className="inline w-4 h-4" /> Sửa
                </button>
                {onDeleteStory && (
                  <button onClick={onDeleteStory} className="text-error btn btn-sm btn-ghost">
                    <TrashIcon className="inline w-4 h-4" /> Xóa
                  </button>
                )}
              </div>
            </div>
            <div className="flex gap-2 mb-4">
              <span className="badge badge-neutral" title={`Time index: ${normalizedTimelineIndex ?? 0}`}>
                                <ClockIcon className="inline w-3.5 h-3.5" /> {formattedWorldTime}
              </span>
              {story.visibility && (
                <span className={`badge ${story.visibility === 'public' ? 'badge-success' : story.visibility === 'draft' ? 'badge-warning' : 'badge-ghost'}`}>
                  {story.visibility === 'public' ? 'Công khai' : story.visibility === 'draft' ? 'Bản nháp' : 'Riêng tư'}
                </span>
              )}
              {world && (
                <Link to={`/worlds/${world.world_id}`} className="cursor-pointer badge badge-info hover:badge-info-focus">
                                    <GlobeAltIcon className="inline w-3.5 h-3.5" /> {world.name}
                </Link>
              )}
            </div>
            {renderStoryContent()}

            {/* Analyze Button */}
            {story.content && !analyzedEntities && (
              <div className="flex gap-2 mt-4">
                {/* Show regular analyze button only if no existing links */}
                {(!linkedCharacters?.length && !linkedLocations?.length) && (
                  <GptButton
                    onClick={onAnalyzeStory}
                    loading={gptAnalyzing}
                    loadingText="Đang phân tích..."
                    variant="primary"
                    size="sm"
                  >
                    Phân tích nhân vật & địa điểm
                  </GptButton>
                )}
                {/* Re-analyze button when existing links are present */}
                {(linkedCharacters?.length > 0 || linkedLocations?.length > 0) && (
                  <GptButton
                    onClick={onReanalyzeStory}
                    loading={gptAnalyzing}
                    loadingText="Đang phân tích lại..."
                    variant="warning"
                    size="sm"
                  >
                    Phân tích lại
                  </GptButton>
                )}
              </div>
            )}

            {/* Analyzed Entities Display - now in modal */}
          </>
        )}
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
              {linkedCharacters.length > 0 && (
                <tr>
                  <td className="font-semibold">Nhân vật liên kết</td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      {linkedCharacters.map((char) => (
                        <span key={char.entity_id} className="badge badge-primary badge-sm">
                          <UserIcon className="inline w-3 h-3" /> {char.name}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              )}
              {linkedLocations.length > 0 && (
                <tr>
                  <td className="font-semibold">Địa điểm liên kết</td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      {linkedLocations.map((loc) => (
                        <span key={loc.location_id} className="badge badge-secondary badge-sm">
                          <MapPinIcon className="inline w-3 h-3" /> {loc.name}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              )}
              {(linkedCharacters.length === 0 && linkedLocations.length === 0 &&
                (story.entities?.length > 0 || story.locations?.length > 0)) && (
                <tr>
                  <td className="font-semibold">Liên kết</td>
                  <td className="opacity-60 text-sm">
                    {story.entities?.length || 0} nhân vật, {story.locations?.length || 0} địa điểm (đang tải...)
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

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
