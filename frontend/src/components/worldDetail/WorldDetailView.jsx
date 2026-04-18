import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import WorldTimeline from './WorldTimeline'
import UnlinkedStoriesModal from './UnlinkedStoriesModal'
import CollaboratorsPanel from './CollaboratorsPanel'
import AnalyzedEntitiesEditor from '../AnalyzedEntitiesEditor'
import Modal from '../Modal'
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
  getTimelineLabel,
  onReorderStories,
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
  onUpdateLocation,
  onDeleteStory,
  collaborators = [],
  inviteLoading = false,
  onInviteCollaborator,
  onRemoveCollaborator,
  // Pagination props
  hasMoreStories = false,
  loadingMoreStories = false,
  onLoadMoreStories,
}) {
  const { t } = useTranslation()
  const [editingEntityId, setEditingEntityId] = useState(null)
  const [entityEditForm, setEntityEditForm] = useState({})
  const [editingLocationId, setEditingLocationId] = useState(null)
  const [locationEditForm, setLocationEditForm] = useState({})
  const [publishTarget, setPublishTarget] = useState(null)

  const startEditEntity = (char) => {
    setEditingEntityId(char.entity_id)
    setEntityEditForm({
      name: char.name || '',
      entity_type: char.entity_type || '',
      description: char.description || '',
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

  const startEditLocation = (loc) => {
    setEditingLocationId(loc.location_id)
    setLocationEditForm({
      name: loc.name || '',
      location_type: loc.location_type || '',
      description: loc.description || '',
    })
  }

  const cancelEditLocation = () => {
    setEditingLocationId(null)
    setLocationEditForm({})
  }

  const saveEditLocation = async () => {
    if (onUpdateLocation) {
      await onUpdateLocation(editingLocationId, locationEditForm)
    }
    setEditingLocationId(null)
    setLocationEditForm({})
  }

  const handleLocationFieldChange = (field, value) => {
    setLocationEditForm(prev => ({ ...prev, [field]: value }))
  }

  const getCharacterStories = (char) =>
    (stories || []).filter(s => (s.entities || s.entity_ids || []).includes(char.entity_id))

  const getLocationStories = (loc) =>
    (stories || []).filter(s => (s.locations || s.location_ids || []).includes(loc.location_id))

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-4">
        <Link to="/worlds" className="btn btn-ghost btn-sm">
          ← {t('common.backToList')}
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
            <div className="flex justify-between items-center gap-2 mb-2">
              <h1 className="font-bold text-2xl md:text-3xl">{world.name}</h1>
              <div className="flex items-center gap-2 shrink-0">
                {canEdit && world.visibility !== 'public' && (
                  <button onClick={() => setPublishTarget(world.visibility === 'draft' ? 'private' : 'public')} className="btn btn-success btn-sm">
                    Publish
                  </button>
                )}
                {canEdit && (
                  <button onClick={onEdit} className="btn btn-sm btn-ghost">
                    <PencilIcon className="inline w-4 h-4" /> <span className="hidden sm:inline">Sửa</span>
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
          <span className="hidden sm:inline">Câu chuyện </span>
          <span>({stories.length})</span>
        </a>
        <a
          className={`tab flex-1 flex items-center justify-center gap-1 ${activeTab === 'characters' ? 'tab-active' : ''}`}
          onClick={() => onChangeTab('characters')}
        >
          <UserIcon className="w-4 h-4 shrink-0" />
          <span className="hidden sm:inline">Nhân vật </span>
          <span>({characters.length})</span>
        </a>
        <a
          className={`tab flex-1 flex items-center justify-center gap-1 ${activeTab === 'locations' ? 'tab-active' : ''}`}
          onClick={() => onChangeTab('locations')}
        >
          <MapPinIcon className="w-4 h-4 shrink-0" />
          <span className="hidden sm:inline">Địa điểm </span>
          <span>({locations.length})</span>
        </a>
      </div>

      {activeTab === 'stories' && (
        <div className="w-full">
          <div className="flex justify-end gap-2 mb-4 flex-wrap">
            {stories.length > 0 && (
              <Link
                to={`/worlds/${world.world_id}/novel`}
                className="btn btn-accent btn-sm gap-1"
              >
                <BookOpenIcon className="inline w-4 h-4" />
                {t('pages.novel.viewAsNovel')}
              </Link>
            )}
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
              <button className="btn btn-primary btn-sm btn-disabled tooltip tooltip-left" data-tip="Admin chỉ quản lý hệ thống, không tạo nội dung">
                + Thêm câu chuyện
              </button>
            ) : user ? (
              <Link to={`/stories/new?worldId=${world.world_id}`} className="btn btn-primary btn-sm">
                + Thêm câu chuyện
              </Link>
            ) : (
              <button className="btn btn-primary btn-sm btn-disabled tooltip tooltip-left" data-tip="Vui lòng đăng nhập để tạo câu chuyện" disabled>
                + Thêm câu chuyện
              </button>
            )}
          </div>
          <WorldTimeline
            stories={stories}
            characters={characters}
            locations={locations}
            getTimelineLabel={getTimelineLabel}
            onDeleteStory={canEdit ? onDeleteStory : null}
            canReorder={canEdit}
            onReorderStories={onReorderStories}
            hasMore={hasMoreStories}
            loadingMore={loadingMoreStories}
            onLoadMore={onLoadMoreStories}
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
                    {(() => {
                      const charStories = getCharacterStories(char)
                      if (charStories.length === 0) return null
                      return (
                        <div className="mt-2">
                          <p className="text-xs opacity-50 mb-1">{t('pages.worldDetail.appearsIn')}</p>
                          <div className="flex flex-wrap gap-1">
                            {charStories.slice(0, 4).map(s => (
                              <Tag key={s.story_id} as={Link} to={`/stories/${s.story_id}`} size="sm" outline>
                                {s.title}
                              </Tag>
                            ))}
                            {charStories.length > 4 && <Tag color="ghost" size="sm">+{charStories.length - 4}</Tag>}
                          </div>
                        </div>
                      )
                    })()}
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
                {editingLocationId === loc.location_id ? (
                  <>
                    <div className="form-control">
                      <label className="py-0 label"><span className="text-xs label-text">Tên</span></label>
                      <input
                        type="text"
                        value={locationEditForm.name}
                        onChange={(e) => handleLocationFieldChange('name', e.target.value)}
                        className="input input-bordered input-sm"
                      />
                    </div>
                    <div className="form-control">
                      <label className="py-0 label"><span className="text-xs label-text">Loại</span></label>
                      <input
                        type="text"
                        value={locationEditForm.location_type}
                        onChange={(e) => handleLocationFieldChange('location_type', e.target.value)}
                        className="input input-bordered input-sm"
                        placeholder="làng, thành phố, rừng..."
                      />
                    </div>
                    <div className="form-control">
                      <label className="py-0 label"><span className="text-xs label-text">Mô tả</span></label>
                      <textarea
                        value={locationEditForm.description}
                        onChange={(e) => handleLocationFieldChange('description', e.target.value)}
                        className="h-16 textarea textarea-bordered textarea-sm"
                      />
                    </div>
                    <div className="flex gap-1 mt-1">
                      <button onClick={saveEditLocation} className="btn btn-primary btn-xs">
                        <CheckCircleIcon className="w-3.5 h-3.5" /> Lưu
                      </button>
                      <button onClick={cancelEditLocation} className="btn btn-ghost btn-xs">
                        <XMarkIcon className="w-3.5 h-3.5" /> Hủy
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex justify-between items-start">
                      <h3 className="card-title"><MapPinIcon className="inline w-4 h-4" /> {loc.name}</h3>
                      {canEdit && (
                        <div className="flex gap-0.5">
                          <button
                            onClick={() => startEditLocation(loc)}
                            className="btn btn-ghost btn-xs"
                            title="Sửa địa điểm"
                          >
                            <PencilIcon className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => onDeleteLocation(loc.location_id, loc.name)}
                            className="hover:bg-error text-error hover:text-error-content btn btn-ghost btn-xs"
                            title="Xóa địa điểm"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      )}
                    </div>
                    {loc.location_type && <Tag color="ghost">{loc.location_type}</Tag>}
                    {loc.description && <p className="opacity-70 text-sm">{loc.description}</p>}
                    {(() => {
                      const locStories = getLocationStories(loc)
                      if (locStories.length === 0) return null
                      return (
                        <div className="mt-2">
                          <p className="text-xs opacity-50 mb-1">{t('pages.worldDetail.appearsIn')}</p>
                          <div className="flex flex-wrap gap-1">
                            {locStories.slice(0, 4).map(s => (
                              <Tag key={s.story_id} as={Link} to={`/stories/${s.story_id}`} size="sm" outline>
                                {s.title}
                              </Tag>
                            ))}
                            {locStories.length > 4 && <Tag color="ghost" size="sm">+{locStories.length - 4}</Tag>}
                          </div>
                        </div>
                      )
                    })()}
                  </>
                )}
              </div>
            </div>
          ))}
          {locations.length === 0 && <p className="opacity-60 text-center">Chưa có địa điểm nào</p>}
        </div>
      )}

      {/* Publish Modal */}
      <Modal
        open={!!publishTarget}
        onClose={() => setPublishTarget(null)}
        title="Publish thế giới"
        className="max-w-sm"
      >
        <p className="mb-4 text-sm opacity-70">Chọn chế độ hiển thị cho thế giới này:</p>
        <div className="flex flex-col gap-2 mb-6">
          <button
            onClick={() => setPublishTarget('private')}
            className={`btn btn-outline justify-start ${publishTarget === 'private' ? 'btn-active btn-primary' : ''}`}
          >
            🔒 Riêng tư — Chỉ bạn có thể xem
          </button>
          <button
            onClick={() => setPublishTarget('public')}
            className={`btn btn-outline justify-start ${publishTarget === 'public' ? 'btn-active btn-success' : ''}`}
          >
            🌐 Công khai — Mọi người có thể xem
          </button>
        </div>
        <div className="flex justify-end gap-2">
          <button className="btn btn-ghost btn-sm" onClick={() => setPublishTarget(null)}>
            Hủy
          </button>
          <button
            className="btn btn-success btn-sm"
            onClick={() => { onPublish(publishTarget); setPublishTarget(null) }}
          >
            Xác nhận
          </button>
        </div>
      </Modal>

      {/* Unlinked Stories Modal */}
      <UnlinkedStoriesModal
        open={showUnlinkedModal}
        onClose={onCloseUnlinkedModal}
        unlinkedStories={unlinkedStories}
        batchAnalyzing={batchAnalyzing}
        batchProgress={batchProgress}
        batchResult={batchResult}
        onBatchAnalyze={onBatchAnalyze}
      />

    </div>
  )
}

export default WorldDetailView
