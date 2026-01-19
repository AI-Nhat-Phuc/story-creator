{/* Đảm bảo màu nền trắng cho nội dung card */ }
import React from 'react'
import { Link } from 'react-router-dom'
import GptButton, { OpenAILogo } from '../GptButton'

function StoriesView({
  stories,
  worlds,
  showCreateModal,
  formData,
  detectedCharacters,
  analyzedEntities,
  gptGenerating,
  gptAnalyzing,
  onOpenModal,
  onCloseModal,
  onInputChange,
  onSubmit,
  onGenerateDescription,
  onAnalyzeStory,
  onClearAnalyzedEntities,
  formatWorldTime,
  getWorldName
}) {
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="font-bold text-3xl">📖 Câu chuyện</h1>
        {worlds.length > 0 ? (
          <button onClick={onOpenModal} className="btn btn-primary">
            + Tạo câu chuyện mới
          </button>
        ) : (
          <div className="tooltip-left tooltip" data-tip="Tạo thế giới trước để bắt đầu">
            <button className="btn btn-disabled" disabled>
              + Tạo câu chuyện mới
            </button>
          </div>
        )}
      </div>

      <div className="gap-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {stories.map(story => {
          // Get world name for scroll color
          const worldName = getWorldName(story.world_id)

          // Generate color based on world name hash
          const colorPalettes = [
            { rod: 'from-amber-600 via-amber-500 to-amber-600', rodEdge: 'from-amber-700 to-amber-800', text: 'text-amber-100' },
            { rod: 'from-cyan-600 via-cyan-500 to-cyan-600', rodEdge: 'from-cyan-700 to-cyan-800', text: 'text-cyan-100' },
            { rod: 'from-emerald-600 via-emerald-500 to-emerald-600', rodEdge: 'from-emerald-700 to-emerald-800', text: 'text-emerald-100' },
            { rod: 'from-violet-600 via-violet-500 to-violet-600', rodEdge: 'from-violet-700 to-violet-800', text: 'text-violet-100' },
            { rod: 'from-rose-600 via-rose-500 to-rose-600', rodEdge: 'from-rose-700 to-rose-800', text: 'text-rose-100' },
            { rod: 'from-sky-600 via-sky-500 to-sky-600', rodEdge: 'from-sky-700 to-sky-800', text: 'text-sky-100' },
            { rod: 'from-orange-600 via-orange-500 to-orange-600', rodEdge: 'from-orange-700 to-orange-800', text: 'text-orange-100' },
            { rod: 'from-teal-600 via-teal-500 to-teal-600', rodEdge: 'from-teal-700 to-teal-800', text: 'text-teal-100' },
            { rod: 'from-indigo-600 via-indigo-500 to-indigo-600', rodEdge: 'from-indigo-700 to-indigo-800', text: 'text-indigo-100' },
            { rod: 'from-pink-600 via-pink-500 to-pink-600', rodEdge: 'from-pink-700 to-pink-800', text: 'text-pink-100' },
          ]

          // Simple hash from world name
          const hash = worldName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
          const colors = colorPalettes[hash % colorPalettes.length]

          return (
            <Link key={story.story_id} to={`/stories/${story.story_id}`} className="group block">
              {/* Scroll Container */}
              <div className="flex h-[220px]">
                {/* Left Scroll Rod */}
                <div className={`relative bg-gradient-to-r ${colors.rod} shadow-md rounded-l-sm w-7`}>
                  {/* World name vertical text */}
                  <div className="absolute inset-0 flex justify-center items-center">
                    <span
                      className={`font-bold text-[16px] ${colors.text} whitespace-nowrap origin-center drop-shadow-sm`}
                      style={{ writingMode: 'vertical-rl', textOrientation: 'mixed', transform: 'rotate(180deg)' }}
                    >
                      {worldName}
                    </span>
                  </div>
                </div>

                {/* Scroll Paper */}
                <div className="relative flex-1 bg-white shadow-xl group-hover:shadow-2xl border border-gray-200 border-l-0 rounded-r-sm overflow-hidden transition-all">
                  <div className="z-10 relative flex flex-col p-4 h-full">
                    <h2 className="mb-2 font-bold text-gray-900 text-lg line-clamp-2 leading-tight">
                      {story.title}
                    </h2>
                    <div className="flex flex-wrap gap-1 mb-2">
                      <span className="bg-gray-100 px-2 py-0.5 rounded text-gray-700 text-xs">
                        ⏰ {formatWorldTime(story)}
                      </span>
                    </div>
                    <div className="flex-1 overflow-hidden">
                      {story.content ? (
                        <p className="text-gray-800 text-sm line-clamp-4 leading-relaxed">
                          {story.content}
                        </p>
                      ) : (
                        <p className="text-gray-400 text-sm italic">
                          Chưa có mô tả...
                        </p>
                      )}
                    </div>
                    <div className="mt-2 pt-2 border-gray-300 border-t border-dashed">
                      <span className="text-gray-400 text-xs">📜 Click để đọc thêm</span>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {stories.length === 0 && worlds.length > 0 && (
        <div className="py-12 text-center">
          <p className="opacity-60 text-xl">Chưa có câu chuyện nào. Hãy tạo câu chuyện đầu tiên!</p>
        </div>
      )}

      {worlds.length === 0 && (
        <div className="py-12 text-center">
          <div className="mx-auto max-w-md">
            <svg xmlns="http://www.w3.org/2000/svg" className="opacity-30 mx-auto w-24 h-24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="opacity-60 mt-4 text-xl">Chưa có thế giới nào!</p>
            <p className="opacity-50 mt-2">Bạn cần tạo thế giới trước khi tạo câu chuyện.</p>
            <Link to="/worlds" className="mt-4 btn btn-primary">
              🌍 Tạo thế giới mới
            </Link>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="modal modal-open">
          <div className="max-w-2xl modal-box">
            <h3 className="mb-4 font-bold text-lg">Tạo câu chuyện mới</h3>
            <form onSubmit={onSubmit}>
              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">Thế giới *</span>
                </label>
                <select
                  name="world_id"
                  value={formData.world_id}
                  onChange={onInputChange}
                  className="select-bordered select"
                  required
                >
                  <option value="">-- Chọn thế giới --</option>
                  {worlds.map(world => (
                    <option key={world.world_id} value={world.world_id}>
                      {world.name} ({world.world_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">Tiêu đề *</span>
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={onInputChange}
                  className="input input-bordered"
                  required
                />
              </div>

              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">Thể loại</span>
                </label>
                <select
                  name="genre"
                  value={formData.genre}
                  onChange={onInputChange}
                  className="select-bordered select"
                >
                  <option value="adventure">Phiêu lưu</option>
                  <option value="mystery">Bí ẩn</option>
                  <option value="conflict">Xung đột</option>
                  <option value="discovery">Khám phá</option>
                </select>
              </div>

              <div className="mb-4 form-control">
                <div className='flex justify-between'>
                  <label className="label">
                    <span className="label-text">Mô tả *</span>
                  </label>
                  <div className="flex gap-2 mb-2">
                    <GptButton
                      onClick={onGenerateDescription}
                      loading={gptGenerating}
                      loadingText="Đang tạo..."
                      disabled={!formData.world_id || !formData.title}
                      variant="secondary"
                      size="xs"
                    >
                      Tạo Mô tả
                    </GptButton>
                  </div>
                </div>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={onInputChange}
                  className="h-32 textarea textarea-bordered"
                  placeholder="Nhập mô tả hoặc dùng GPT để tự động tạo..."
                  required
                />
                <label className="label">
                  <span className="label-text-alt">
                    {formData.description.length > 0
                      ? `${formData.description.length} ký tự`
                      : <span className="px-2 py-1 rounded font-semibold text-gray-400">Click nút GPT để tự động tạo mô tả</span>}
                  </span>
                </label>
              </div>

              {/* Analyze Button */}
              {formData.description && !analyzedEntities && (
                <div className="mb-4">
                  <GptButton
                    onClick={onAnalyzeStory}
                    loading={gptAnalyzing}
                    loadingText="Đang phân tích..."
                    variant="primary"
                    size="sm"
                  >
                    Phân tích nhân vật & địa điểm
                  </GptButton>
                </div>
              )}

              {/* Analyzed Entities Display */}
              {analyzedEntities && (
                <div className="bg-base-200/50 mb-4 p-4 border border-base-300 rounded-xl">
                  <div className="w-full">
                    <div className="flex justify-between items-center mb-3">
                      <span className="flex items-center gap-2 font-semibold">
                        <span className="flex justify-center items-center bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-full w-6 h-6 text-emerald-600">
                          <OpenAILogo className="w-3.5 h-3.5" />
                        </span>
                        Kết quả phân tích
                      </span>
                      <button
                        type="button"
                        className="opacity-50 hover:opacity-100 btn btn-xs btn-circle btn-ghost"
                        onClick={onClearAnalyzedEntities}
                      >
                        ✕
                      </button>
                    </div>
                    {analyzedEntities.characters?.length > 0 && (
                      <div className="mb-3">
                        <span className="opacity-70 text-sm">👤 Nhân vật ({analyzedEntities.characters.length}):</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {analyzedEntities.characters.map((char, i) => (
                            <span key={i} className="bg-primary/10 px-2 py-1 border border-primary/30 rounded-lg font-medium text-primary text-sm">{char.name || char}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {analyzedEntities.locations?.length > 0 && (
                      <div className="mb-3">
                        <span className="opacity-70 text-sm">📍 Địa điểm ({analyzedEntities.locations.length}):</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {analyzedEntities.locations.map((loc, i) => (
                            <span key={i} className="bg-secondary/10 px-2 py-1 border border-secondary/30 rounded-lg font-medium text-secondary text-sm">{loc.name || loc}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {(!analyzedEntities.characters?.length && !analyzedEntities.locations?.length) && (
                      <p className="text-sm">Không tìm thấy nhân vật hoặc địa điểm cụ thể.</p>
                    )}
                    {/* Link confirmation message */}
                    {(analyzedEntities.characters?.length > 0 || analyzedEntities.locations?.length > 0) && (
                      <div className="mt-2 pt-2 border-success/30 border-t">
                        <span className="text-sm">
                          ✅ Nhấn <strong>Tạo câu chuyện</strong> để lưu và liên kết các thực thể này
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {gptGenerating && (
                <div className="mb-4 alert alert-info">
                  <div>
                    <span className="loading loading-spinner"></span>
                    <span>Đang tạo mô tả với GPT...</span>
                  </div>
                </div>
              )}

              {detectedCharacters.length > 0 && (
                <div className="mb-4 alert alert-info">
                  <div>
                    <svg xmlns="http://www.w3.org/2000/svg" className="flex-shrink-0 stroke-current w-6 h-6" fill="none" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <div className="font-bold">Đã phát hiện {detectedCharacters.length} nhân vật:</div>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {detectedCharacters.map(char => (
                          <span key={char.entity_id} className="badge badge-primary">
                            👤 {char.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">Thời điểm (0-100): {formData.time_index}</span>
                </label>
                <input
                  type="range"
                  name="time_index"
                  min="0"
                  max="100"
                  value={formData.time_index}
                  onChange={onInputChange}
                  className="range"
                />
              </div>

              <div className="modal-action">
                <button type="submit" className="btn btn-primary" disabled={gptGenerating}>
                  Tạo câu chuyện
                </button>
                <button type="button" onClick={onCloseModal} className="btn" disabled={gptGenerating}>Hủy</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default StoriesView
