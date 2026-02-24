import { Link } from 'react-router-dom'
import WorldTimeline from './WorldTimeline'
import UnlinkedStoriesModal from './UnlinkedStoriesModal'
import GptButton from '../GptButton'
import AnalyzedEntitiesEditor from '../AnalyzedEntitiesEditor'
import {
  BookOpenIcon,
  UserIcon,
  MapPinIcon,
  LinkIcon,
  TrashIcon,
  PencilIcon,
  CheckCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'
import { ArrowDownTrayIcon } from '@heroicons/react/24/solid'

function WorldDetailView({
  world,
  stories,
  characters,
  locations,
  activeTab,
  editing,
  editForm,
  user,
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
  // Unlinked stories modal props
  showUnlinkedModal,
  unlinkedStories,
  batchAnalyzing,
  batchProgress,
  batchResult,
  onBatchAnalyze,
  onCloseUnlinkedModal,
  // Delete entity/location/story props
  onDeleteEntity,
  onDeleteLocation,
  onDeleteStory,
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
  onUpdateAnalyzedEntities,
  showAnalyzedModal,
  onCloseAnalyzedModal,
  onOpenAnalyzedModal,
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
              <h1 className="font-bold text-3xl">{world.name}</h1>
              <button onClick={onEdit} className="btn btn-sm btn-ghost">
                <PencilIcon className="inline w-4 h-4" /> Sửa
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
                    <BookOpenIcon className="inline w-4 h-4" /> Câu chuyện ({stories.length})
        </a>
        <a
          className={`tab ${activeTab === 'characters' ? 'tab-active' : ''}`}
          onClick={() => onChangeTab('characters')}
        >
                    <UserIcon className="inline w-4 h-4" /> Nhân vật ({characters.length})
        </a>
        <a
          className={`tab ${activeTab === 'locations' ? 'tab-active' : ''}`}
          onClick={() => onChangeTab('locations')}
        >
                    <MapPinIcon className="inline w-4 h-4" /> Địa điểm ({locations.length})
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
              {autoLinking ? 'Đang liên kết...' : <><LinkIcon className="inline w-4 h-4" /> Liên kết tự động</>}
            </button>
            {user?.role === 'admin' ? (
              <div className="tooltip-left tooltip" data-tip="Admin chỉ quản lý hệ thống, không tạo nội dung">
                <button className="btn btn-primary btn-sm btn-disabled">
                  + Thêm câu chuyện
                </button>
              </div>
            ) : (
              <button onClick={onOpenStoryModal} className="btn btn-primary btn-sm">
                + Thêm câu chuyện
              </button>
            )}
          </div>
          <WorldTimeline
            stories={stories}
            characters={characters}
            locations={locations}
            getStoryWorldTime={getStoryWorldTime}
            getTimelineLabel={getTimelineLabel}
            onDeleteStory={onDeleteStory}
          />
        </div>
      )}

      {activeTab === 'characters' && (
        <div className="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {characters.map(char => (
            <div key={char.entity_id} className="bg-base-100 shadow card">
              <div className="card-body">
                <div className="flex justify-between items-start">
                  <h3 className="card-title"><UserIcon className="inline w-4 h-4" /> {char.name}</h3>
                  <button
                    onClick={() => onDeleteEntity(char.entity_id, char.name)}
                    className="hover:bg-error text-error hover:text-error-content btn btn-ghost btn-xs"
                    title="Xóa nhân vật"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
                <p className="badge">{char.entity_type}</p>
                {char.attributes && (
                  <div className="text-sm">
                    <p><svg xmlns="http://www.w3.org/2000/svg" className="inline w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg> Sức mạnh: {char.attributes.Strength}</p>
                    <p><svg xmlns="http://www.w3.org/2000/svg" className="inline w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg> Trí tuệ: {char.attributes.Intelligence}</p>
                    <p><svg xmlns="http://www.w3.org/2000/svg" className="inline w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg> Sức hút: {char.attributes.Charisma}</p>
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
                  <h3 className="card-title"><MapPinIcon className="inline w-4 h-4" /> {loc.name}</h3>
                  <button
                    onClick={() => onDeleteLocation(loc.location_id, loc.name)}
                    className="hover:bg-error text-error hover:text-error-content btn btn-ghost btn-xs"
                    title="Xóa địa điểm"
                  >
                    <TrashIcon className="w-4 h-4" />
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
                <div className='flex justify-between'>
                  <label className="label">
                    <span className="label-text">Mô tả *</span>
                  </label>
                  <GptButton
                    onClick={onGenerateStoryDescription}
                    loading={gptGenerating}
                    loadingText="Đang tạo..."
                    disabled={!storyForm.title}
                    variant="secondary"
                    size="xs"
                  >
                    Tạo mô tả
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
                      : 'Click nút GPT để tự động tạo mô tả'}
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

              {/* Analyzed entities indicator */}
              {analyzedEntities && (analyzedEntities.characters?.length > 0 || analyzedEntities.locations?.length > 0) && (
                <div className="flex items-center gap-2 bg-success/10 mb-4 px-3 py-2 border border-success/30 rounded-lg text-sm">
                  <CheckCircleIcon className="w-4 h-4 text-success shrink-0" />
                  <span>
                    Đã phân tích: {analyzedEntities.characters?.length || 0} nhân vật, {analyzedEntities.locations?.length || 0} địa điểm
                  </span>
                  <button
                    type="button"
                    className="ml-auto text-xs link link-primary"
                    onClick={onOpenAnalyzedModal}
                  >
                    Xem / Sửa
                  </button>
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

      {/* Unlinked Stories Modal */}
      <UnlinkedStoriesModal
        open={showUnlinkedModal}
        onClose={onCloseUnlinkedModal}
        unlinkedStories={unlinkedStories}
        getTimelineLabel={getTimelineLabel}
        batchAnalyzing={batchAnalyzing}
        batchProgress={batchProgress}
        batchResult={batchResult}
        onBatchAnalyze={onBatchAnalyze}
      />

      {/* GPT Analyzed Entities Modal */}
      <AnalyzedEntitiesEditor
        open={showAnalyzedModal}
        analyzedEntities={analyzedEntities}
        onUpdate={onUpdateAnalyzedEntities}
        onClose={onCloseAnalyzedModal}
        onClear={onClearAnalyzedEntities}
        linkLabel="Xác nhận"
      />
    </div>
  )
}

export default WorldDetailView
