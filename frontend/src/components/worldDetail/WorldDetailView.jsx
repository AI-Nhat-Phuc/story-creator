import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import WorldTimeline from './WorldTimeline'
import UnlinkedStoriesModal from './UnlinkedStoriesModal'
import CollaboratorsPanel from './CollaboratorsPanel'
import AnalyzedEntitiesEditor from '../AnalyzedEntitiesEditor'
import Tag from '../Tag'
import {
  BookOpenIcon,
  UserIcon,
  MapPinIcon,
  LinkIcon,
  TrashIcon,
  PencilIcon,
  XMarkIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline'
import { ArrowDownTrayIcon } from '@heroicons/react/24/solid'

function WorldDetailView({
  world,
  stories,
  characters,
  locations,
  activeTab,
  canEdit = false,
  editing,
  editForm,
  user,
  authLoading,
  onChangeTab,
  onEdit,
  onCancelEdit,
  onSaveEdit,
  onChangeField,
  onPublish,
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
  onUpdateEntity,
  onDeleteLocation,
  onDeleteStory,
  collaborators = [],
  inviteLoading = false,
  onInviteCollaborator,
  onRemoveCollaborator,
}) {
  const [editingEntityId, setEditingEntityId] = useState(null)
  const [entityEditForm, setEntityEditForm] = useState({})
  const [publishTarget, setPublishTarget] = useState(null)

  const startEditEntity = (char) => {
    setEditingEntityId(char.entity_id)
    setEntityEditForm({
      name: char.name || '',
      entity_type: char.entity_type || '',
      description: char.description || '',
      attributes: { ...char.attributes }
    })
  }

  const cancelEditEntity = () => {
    setEditingEntityId(null)
    setEntityEditForm({})
  }

  const saveEditEntity = async () => {
    if (onUpdateEntity) {
      await onUpdateEntity(editingEntityId, entityEditForm)
    }
    setEditingEntityId(null)
    setEntityEditForm({})
  }

  const handleEntityFieldChange = (field, value) => {
    setEntityEditForm(prev => ({ ...prev, [field]: value }))
  }

  const handleAttributeChange = (attr, value) => {
    const num = Math.min(10, Math.max(0, Number(value) || 0))
    setEntityEditForm(prev => ({
      ...prev,
      attributes: { ...prev.attributes, [attr]: num }
    }))
  }

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
            <div className="mb-4 form-control">
              <label className="label">
                <span className="font-semibold label-text">Chế độ hiển thị</span>
              </label>
              <select
                value={editForm.visibility}
                onChange={(e) => onChangeField('visibility', e.target.value)}
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
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2 mb-2">
              <h1 className="font-bold text-2xl md:text-3xl">{world.name}</h1>
              <div className="flex items-center gap-2 flex-wrap">
                <Link to={`/worlds/${world.world_id}/novel`} className="btn btn-outline btn-sm gap-1">
                  <BookOpenIcon className="w-4 h-4" /> Novel
                </Link>
                {canEdit && world.visibility !== 'public' && (
                  <button onClick={() => setPublishTarget(world.visibility === 'draft' ? 'private' : 'public')} className="btn btn-success btn-sm">
                    Publish
                  </button>
                )}
                {canEdit && (
                  <button onClick={onEdit} className="btn btn-sm btn-ghost">
                    <PencilIcon className="inline w-4 h-4" /> Sửa
                  </button>
                )}
              </div>
            </div>
            <div className="flex flex-wrap gap-2 mb-4">
              <Tag color="primary">{world.world_type}</Tag>
              {world.visibility && (
                <Tag color={world.visibility === 'public' ? 'success' : world.visibility === 'draft' ? 'warning' : 'ghost'}>
                  {world.visibility === 'public' ? 'Công khai' : world.visibility === 'draft' ? 'Bản nháp' : 'Riêng tư'}
                </Tag>
              )}
            </div>
            <p className="text-lg">{world.description}</p>
          </>
        )}
      </div>

      {(collaborators.length > 0 || canEdit) && (
        <div className="mb-4">
          <CollaboratorsPanel
            collaborators={collaborators}
            canEdit={canEdit}
            inviteLoading={inviteLoading}
            onInvite={onInviteCollaborator}
            onRemove={onRemoveCollaborator}
          />
        </div>
      )}

      <div className="mb-4 tabs tabs-boxed w-full">
        <a
          className={`tab flex-1 flex items-center justify-center gap-1 ${activeTab === 'stories' ? 'tab-active' : ''}`}
          onClick={() => onChangeTab('stories')}
        >
          <BookOpenIcon className="w-4 h-4 shrink-0" />
          <span>Câu chuyện ({stories.length})</span>
        </a>
        <a
          className={`tab flex-1 flex items-center justify-center gap-1 ${activeTab === 'characters' ? 'tab-active' : ''}`}
          onClick={() => onChangeTab('characters')}
        >
          <UserIcon className="w-4 h-4 shrink-0" />
          <span>Nhân vật ({characters.length})</span>
        </a>
        <a
          className={`tab flex-1 flex items-center justify-center gap-1 ${activeTab === 'locations' ? 'tab-active' : ''}`}
          onClick={() => onChangeTab('locations')}
        >
          <MapPinIcon className="w-4 h-4 shrink-0" />
          <span>Địa điểm ({locations.length})</span>
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
            {authLoading ? (
              <button className="btn btn-primary btn-sm" disabled>
                <span className="loading loading-spinner loading-xs"></span>
              </button>
            ) : user?.role === 'admin' ? (
              <div className="tooltip-left tooltip" data-tip="Admin chỉ quản lý hệ thống, không tạo nội dung">
                <button className="btn btn-primary btn-sm btn-disabled">
                  + Thêm câu chuyện
                </button>
              </div>
            ) : user ? (
              <Link to={`/stories/new?worldId=${world.world_id}`} className="btn btn-primary btn-sm">
                + Thêm câu chuyện
              </Link>
            ) : (
              <div className="tooltip-left tooltip" data-tip="Vui lòng đăng nhập để tạo câu chuyện">
                <button className="btn btn-primary btn-sm btn-disabled" disabled>
                  + Thêm câu chuyện
                </button>
              </div>
            )}
          </div>
          <WorldTimeline
            stories={stories}
            characters={characters}
            locations={locations}
            getStoryWorldTime={getStoryWorldTime}
            getTimelineLabel={getTimelineLabel}
            onDeleteStory={canEdit ? onDeleteStory : null}
          />
        </div>
      )}

      {activeTab === 'characters' && (
        <div className="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {characters.map(char => (
            <div key={char.entity_id} className="bg-base-100 shadow card">
              <div className="card-body">
                {editingEntityId === char.entity_id ? (
                  /* Inline edit mode */
                  <>
                    <div className="form-control">
                      <label className="py-0 label"><span className="text-xs label-text">Tên</span></label>
                      <input
                        type="text"
                        value={entityEditForm.name}
                        onChange={(e) => handleEntityFieldChange('name', e.target.value)}
                        className="input input-bordered input-sm"
                      />
                    </div>
                    <div className="form-control">
                      <label className="py-0 label"><span className="text-xs label-text">Loại</span></label>
                      <input
                        type="text"
                        value={entityEditForm.entity_type}
                        onChange={(e) => handleEntityFieldChange('entity_type', e.target.value)}
                        className="input input-bordered input-sm"
                        placeholder="anh hùng, pháp sư, thường dân..."
                      />
                    </div>
                    <div className="form-control">
                      <label className="py-0 label"><span className="text-xs label-text">Mô tả</span></label>
                      <textarea
                        value={entityEditForm.description}
                        onChange={(e) => handleEntityFieldChange('description', e.target.value)}
                        className="h-16 textarea textarea-bordered textarea-sm"
                      />
                    </div>
                    {entityEditForm.attributes && (
                      <div className="gap-2 grid grid-cols-3 text-sm">
                        <div className="form-control">
                          <label className="py-0 label"><span className="text-xs label-text">Sức mạnh</span></label>
                          <input type="number" min="0" max="10" value={entityEditForm.attributes.Strength ?? 0}
                            onChange={(e) => handleAttributeChange('Strength', e.target.value)}
                            className="w-full input input-bordered input-xs" />
                        </div>
                        <div className="form-control">
                          <label className="py-0 label"><span className="text-xs label-text">Trí tuệ</span></label>
                          <input type="number" min="0" max="10" value={entityEditForm.attributes.Intelligence ?? 0}
                            onChange={(e) => handleAttributeChange('Intelligence', e.target.value)}
                            className="w-full input input-bordered input-xs" />
                        </div>
                        <div className="form-control">
                          <label className="py-0 label"><span className="text-xs label-text">Sức hút</span></label>
                          <input type="number" min="0" max="10" value={entityEditForm.attributes.Charisma ?? 0}
                            onChange={(e) => handleAttributeChange('Charisma', e.target.value)}
                            className="w-full input input-bordered input-xs" />
                        </div>
                      </div>
                    )}
                    <div className="flex gap-1 mt-1">
                      <button onClick={saveEditEntity} className="btn btn-primary btn-xs">
                        <CheckCircleIcon className="w-3.5 h-3.5" /> Lưu
                      </button>
                      <button onClick={cancelEditEntity} className="btn btn-ghost btn-xs">
                        <XMarkIcon className="w-3.5 h-3.5" /> Hủy
                      </button>
                    </div>
                  </>
                ) : (
                  /* View mode */
                  <>
                    <div className="flex justify-between items-start">
                      <h3 className="card-title"><UserIcon className="inline w-4 h-4" /> {char.name}</h3>
                      {canEdit && (
                        <div className="flex gap-0.5">
                          <button
                            onClick={() => startEditEntity(char)}
                            className="btn btn-ghost btn-xs"
                            title="Sửa nhân vật"
                          >
                            <PencilIcon className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => onDeleteEntity(char.entity_id, char.name)}
                            className="hover:bg-error text-error hover:text-error-content btn btn-ghost btn-xs"
                            title="Xóa nhân vật"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      )}
                    </div>
                     <Tag color="ghost">{char.entity_type}</Tag>
                    {char.description && <p className="opacity-70 text-sm">{char.description}</p>}
                    {char.attributes && (
                      <div className="text-sm">
                        <p><svg xmlns="http://www.w3.org/2000/svg" className="inline w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg> Sức mạnh: {char.attributes.Strength}</p>
                        <p><svg xmlns="http://www.w3.org/2000/svg" className="inline w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg> Trí tuệ: {char.attributes.Intelligence}</p>
                        <p><svg xmlns="http://www.w3.org/2000/svg" className="inline w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg> Sức hút: {char.attributes.Charisma}</p>
                      </div>
                    )}
                  </>
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
                  {canEdit && (
                    <button
                      onClick={() => onDeleteLocation(loc.location_id, loc.name)}
                      className="hover:bg-error text-error hover:text-error-content btn btn-ghost btn-xs"
                      title="Xóa địa điểm"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  )}
                </div>
                {loc.location_type && <Tag color="ghost">{loc.location_type}</Tag>}
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

      {/* Publish Modal */}
      {publishTarget && (
        <div className="modal modal-open">
          <div className="modal-box max-w-sm">
            <h3 className="font-bold text-lg mb-2">Publish thế giới</h3>
            <p className="mb-4 text-sm opacity-70">Chọn chế độ hiển thị cho thế giới này:</p>
            <div className="flex flex-col gap-2 mb-4">
              <button
                onClick={() => setPublishTarget('private')}
                className={`btn btn-outline justify-start ${publishTarget === 'private' ? 'btn-active' : ''}`}
              >
                Riêng tư — Chỉ bạn có thể xem
              </button>
              <button
                onClick={() => setPublishTarget('public')}
                className={`btn btn-outline justify-start ${publishTarget === 'public' ? 'btn-active' : ''}`}
              >
                Công khai — Mọi người có thể xem
              </button>
            </div>
            <div className="modal-action">
              <button
                className="btn btn-success"
                onClick={() => { onPublish(publishTarget); setPublishTarget(null) }}
              >
                Xác nhận
              </button>
              <button className="btn btn-ghost" onClick={() => setPublishTarget(null)}>Hủy</button>
            </div>
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

    </div>
  )
}

export default WorldDetailView
