import { Link } from 'react-router-dom'
import WorldTimeline from './WorldTimeline'
import GptButton, { OpenAILogo } from '../GptButton'

function WorldDetailView({
  world,
  stories,
  characters,
  locations,
  activeTab,
  editing,
  editForm,
  onChangeTab,
  onEdit,
  onCancelEdit,
  onSaveEdit,
  onChangeField,
  getStoryWorldTime,
  getTimelineLabel,
  // Auto-link props
  autoLinking,
  onAutoLinkStories,
  // Delete entity/location props
  onDeleteEntity,
  onDeleteLocation,
  // Story creation props
  showStoryModal,
  storyForm,
  gptGenerating,
  gptAnalyzing,
  analyzedEntities,
  onOpenStoryModal,
  onCloseStoryModal,
  onStoryFormChange,
  onGenerateStoryDescription,
  onAnalyzeStory,
  onClearAnalyzedEntities,
  onCreateStory
}) {
  return (
    <div>
      <div className="mb-4">
        <Link to="/worlds" className="btn btn-ghost btn-sm">
          ← Quay lại danh sách
        </Link>
      </div>

      <div className="bg-base-100 shadow-xl mb-6 p-6 rounded-box">
        {editing ? (
          <>
            <input
              type="text"
              value={editForm.name}
              onChange={(e) => onChangeField('name', e.target.value)}
              className="mb-4 w-full font-bold text-3xl input input-bordered"
              placeholder="Tên thế giới"
            />
            <textarea
              value={editForm.description}
              onChange={(e) => onChangeField('description', e.target.value)}
              className="mb-4 w-full min-h-[120px] textarea textarea-bordered"
              placeholder="Mô tả thế giới"
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
              <h1 className="font-bold text-3xl">{world.name}</h1>
              <button onClick={onEdit} className="btn btn-sm btn-ghost">
                ✏️ Sửa
              </button>
            </div>
            <p className="mb-4 badge badge-primary">{world.world_type}</p>
            <p className="text-lg">{world.description}</p>
          </>
        )}
      </div>

      <div className="mb-4 tabs tabs-boxed">
        <a
          className={`tab ${activeTab === 'stories' ? 'tab-active' : ''}`}
          onClick={() => onChangeTab('stories')}
        >
          📖 Câu chuyện ({stories.length})
        </a>
        <a
          className={`tab ${activeTab === 'characters' ? 'tab-active' : ''}`}
          onClick={() => onChangeTab('characters')}
        >
          👤 Nhân vật ({characters.length})
        </a>
        <a
          className={`tab ${activeTab === 'locations' ? 'tab-active' : ''}`}
          onClick={() => onChangeTab('locations')}
        >
          📍 Địa điểm ({locations.length})
        </a>
      </div>

      {activeTab === 'stories' && (
        <div className="w-full">
          <div className="flex justify-end gap-2 mb-4">
            <button
              onClick={onAutoLinkStories}
              className={`btn btn-secondary btn-sm ${autoLinking ? 'loading' : ''}`}
              disabled={autoLinking || stories.length < 2}
              title="Tự động liên kết các câu chuyện có chung nhân vật hoặc địa điểm"
            >
              {autoLinking ? 'Đang liên kết...' : '🔗 Liên kết tự động'}
            </button>
            <button onClick={onOpenStoryModal} className="btn btn-primary btn-sm">
              + Thêm câu chuyện
            </button>
          </div>
          <WorldTimeline
            stories={stories}
            characters={characters}
            locations={locations}
            getStoryWorldTime={getStoryWorldTime}
            getTimelineLabel={getTimelineLabel}
          />
        </div>
      )}

      {activeTab === 'characters' && (
        <div className="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {characters.map(char => (
            <div key={char.entity_id} className="bg-base-100 shadow card">
              <div className="card-body">
                <div className="flex justify-between items-start">
                  <h3 className="card-title">👤 {char.name}</h3>
                  <button
                    onClick={() => onDeleteEntity(char.entity_id, char.name)}
                    className="hover:bg-error text-error hover:text-error-content btn btn-ghost btn-xs"
                    title="Xóa nhân vật"
                  >
                    🗑️
                  </button>
                </div>
                <p className="badge">{char.entity_type}</p>
                {char.attributes && (
                  <div className="text-sm">
                    <p>💪 Sức mạnh: {char.attributes.Strength}</p>
                    <p>🧠 Trí tuệ: {char.attributes.Intelligence}</p>
                    <p>✨ Sức hút: {char.attributes.Charisma}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
          {characters.length === 0 && <p className="opacity-60 text-center">Chưa có nhân vật nào</p>}
        </div>
      )}

      {activeTab === 'locations' && (
        <div className="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {locations.map(loc => (
            <div key={loc.location_id} className="bg-base-100 shadow card">
              <div className="card-body">
                <div className="flex justify-between items-start">
                  <h3 className="card-title">📍 {loc.name}</h3>
                  <button
                    onClick={() => onDeleteLocation(loc.location_id, loc.name)}
                    className="hover:bg-error text-error hover:text-error-content btn btn-ghost btn-xs"
                    title="Xóa địa điểm"
                  >
                    🗑️
                  </button>
                </div>
                {loc.location_type && <p className="badge">{loc.location_type}</p>}
                {loc.description && <p className="opacity-70 text-sm">{loc.description}</p>}
                {loc.coordinates && (
                  <p className="opacity-50 text-xs">
                    Tọa độ: ({Math.round(loc.coordinates.x)}, {Math.round(loc.coordinates.y)})
                  </p>
                )}
              </div>
            </div>
          ))}
          {locations.length === 0 && <p className="opacity-60 text-center">Chưa có địa điểm nào</p>}
        </div>
      )}

      {/* Create Story Modal */}
      {showStoryModal && (
        <div className="modal modal-open">
          <div className="max-w-2xl modal-box">
            <h3 className="mb-4 font-bold text-lg">Tạo câu chuyện mới trong {world.name}</h3>
            <form onSubmit={onCreateStory}>
              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">Tiêu đề *</span>
                </label>
                <input
                  type="text"
                  name="title"
                  value={storyForm.title}
                  onChange={onStoryFormChange}
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
                  value={storyForm.genre}
                  onChange={onStoryFormChange}
                  className="select-bordered select"
                >
                  <option value="adventure">Phiêu lưu</option>
                  <option value="mystery">Bí ẩn</option>
                  <option value="conflict">Xung đột</option>
                  <option value="discovery">Khám phá</option>
                </select>
              </div>

              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">Mô tả *</span>
                </label>
                <div className="flex gap-2 mb-2">
                  <GptButton
                    onClick={onGenerateStoryDescription}
                    loading={gptGenerating}
                    loadingText="Đang tạo..."
                    disabled={!storyForm.title}
                    variant="secondary"
                    size="sm"
                  >
                    Tự động tạo mô tả
                  </GptButton>
                </div>
                <textarea
                  name="description"
                  value={storyForm.description}
                  onChange={onStoryFormChange}
                  className="h-32 textarea textarea-bordered"
                  placeholder="Nhập mô tả hoặc dùng GPT để tự động tạo..."
                  required
                />
                <label className="label">
                  <span className="label-text-alt">
                    {storyForm.description.length > 0
                      ? `${storyForm.description.length} ký tự`
                      : '💡 Click nút GPT để tự động tạo mô tả'}
                  </span>
                </label>
              </div>

              {/* Analyze Button */}
              {storyForm.description && !analyzedEntities && (
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
                      <div className="mb-2">
                        <span className="font-semibold">👤 Nhân vật ({analyzedEntities.characters.length}):</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {analyzedEntities.characters.map((char, i) => (
                            <span key={i} className="badge badge-primary">{char.name || char}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {analyzedEntities.locations?.length > 0 && (
                      <div className="mb-2">
                        <span className="font-semibold">📍 Địa điểm ({analyzedEntities.locations.length}):</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {analyzedEntities.locations.map((loc, i) => (
                            <span key={i} className="badge badge-secondary">{loc.name || loc}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {(!analyzedEntities.characters?.length && !analyzedEntities.locations?.length) && (
                      <p className="text-sm">Không tìm thấy nhân vật hoặc địa điểm cụ thể.</p>
                    )}
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

              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">Thời điểm (0-100): {storyForm.time_index}</span>
                </label>
                <input
                  type="range"
                  name="time_index"
                  min="0"
                  max="100"
                  value={storyForm.time_index}
                  onChange={onStoryFormChange}
                  className="range"
                />
              </div>

              <div className="modal-action">
                <button type="submit" className="btn btn-primary" disabled={gptGenerating}>
                  Tạo câu chuyện
                </button>
                <button type="button" onClick={onCloseStoryModal} className="btn" disabled={gptGenerating}>Hủy</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default WorldDetailView
