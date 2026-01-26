import React from 'react'
import { Link } from 'react-router-dom'
import GptButton, { OpenAILogo } from '../GptButton'

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
  onLinkEntities,
  onReanalyzeStory
}) {
  return (
    <div>
      <div className="flex gap-2 mb-4">
        <Link to="/stories" className="btn btn-ghost btn-sm">
          ← Quay lại danh sách
        </Link>
        {world && (
          <Link to={`/worlds/${world.world_id}`} className="btn btn-ghost btn-sm">
            🌍 Về thế giới {world.name}
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
            <div className="flex gap-2">
              <button onClick={onSaveEdit} className="btn btn-primary">
                💾 Lưu
              </button>
              <button onClick={onCancelEdit} className="btn btn-ghost">
                ❌ Hủy
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="flex justify-between items-start mb-2">
              <h1 className="font-bold text-3xl">{story.title}</h1>
              <button onClick={onEdit} className="btn btn-sm btn-ghost">
                ✏️ Sửa
              </button>
            </div>
            <div className="flex gap-2 mb-4">
              <span className="badge badge-neutral" title={`Time index: ${normalizedTimelineIndex ?? 0}`}>
                ⏰ {formattedWorldTime}
              </span>
              {world && (
                <Link to={`/worlds/${world.world_id}`} className="cursor-pointer badge badge-info hover:badge-info-focus">
                  🌍 {world.name}
                </Link>
              )}
            </div>
            <p className="text-lg whitespace-pre-wrap">{story.content}</p>

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

            {/* Analyzed Entities Display */}
            {analyzedEntities && (
              <div className="bg-base-200/50 mt-6 p-5 border border-base-300 rounded-xl">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="flex items-center gap-2 font-semibold text-base">
                    <span className="flex justify-center items-center bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-full w-7 h-7 text-emerald-600">
                      <OpenAILogo className="w-4 h-4" />
                    </span>
                    Kết quả phân tích GPT
                  </h4>
                  <button
                    type="button"
                    className="opacity-50 hover:opacity-100 btn btn-xs btn-circle btn-ghost"
                    onClick={onClearAnalyzedEntities}
                    title="Xóa kết quả"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-4">
                  {analyzedEntities.characters?.length > 0 && (
                    <div>
                      <p className="opacity-70 mb-2 text-sm">
                        👤 Nhân vật <span className="opacity-50">({analyzedEntities.characters.length})</span>
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {analyzedEntities.characters.map((char, i) => (
                          <span key={i} className="bg-primary/10 px-3 py-1.5 border border-primary/30 rounded-lg font-medium text-primary text-sm">
                            {char.name || char}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {analyzedEntities.locations?.length > 0 && (
                    <div>
                      <p className="opacity-70 mb-2 text-sm">
                        📍 Địa điểm <span className="opacity-50">({analyzedEntities.locations.length})</span>
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {analyzedEntities.locations.map((loc, i) => (
                          <span key={i} className="bg-secondary/10 px-3 py-1.5 border border-secondary/30 rounded-lg font-medium text-secondary text-sm">
                            {loc.name || loc}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {(!analyzedEntities.characters?.length && !analyzedEntities.locations?.length) && (
                    <p className="opacity-60 text-sm text-center">Không tìm thấy nhân vật hoặc địa điểm cụ thể.</p>
                  )}
                </div>

                {/* Link Entities Button */}
                {(analyzedEntities.characters?.length > 0 || analyzedEntities.locations?.length > 0) && (
                  <div className="flex items-center gap-3 mt-5 pt-4 border-base-300 border-t">
                    <button
                      type="button"
                      onClick={onLinkEntities}
                      className="bg-gradient-to-r from-success hover:from-success/90 to-emerald-500 hover:to-emerald-500/90 shadow-sm border-0 text-white btn btn-sm"
                    >
                      ✅ Xác nhận liên kết
                    </button>
                    <span className="opacity-50 text-xs">
                      Lưu nhân vật và địa điểm vào câu chuyện
                    </span>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      <div className="bg-base-100 shadow-xl p-6 rounded-box">
        <h2 className="mb-4 font-bold text-2xl">📋 Thông tin chi tiết</h2>
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
                          👤 {char.name}
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
                          📍 {loc.name}
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
    </div>
  )
}

export default StoryDetailView
