import { useState } from 'react'
import { OpenAILogo } from './GptButton'
import {
  UserIcon,
  MapPinIcon,
  CheckCircleIcon,
  PlusIcon,
  TrashIcon,
  PencilIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

/**
 * Modal editor for GPT-analyzed entities (characters & locations).
 * Shows as a popup when GPT analysis completes.
 * Allows renaming, removing, and adding new items before linking.
 *
 * Props:
 *  - open: boolean — whether the modal is visible
 *  - analyzedEntities: { characters: [{name, role}], locations: [{name, description}] }
 *  - onUpdate: (updated) => void — called with the full updated object
 *  - onClose: () => void — close modal (keeps entities in state)
 *  - onClear: () => void — clear all results and close
 *  - onLink: () => void — confirm and link (for StoryDetail; also closes modal)
 *  - linkLabel: string — label for the confirm button
 */
function AnalyzedEntitiesEditor({
  open,
  analyzedEntities,
  onUpdate,
  onClose,
  onClear,
  onLink,
  linkLabel = 'Xác nhận liên kết',
}) {
  const [editingChar, setEditingChar] = useState(null)  // index
  const [editingLoc, setEditingLoc] = useState(null)    // index
  const [editValue, setEditValue] = useState('')
  const [addingChar, setAddingChar] = useState(false)
  const [addingLoc, setAddingLoc] = useState(false)
  const [newCharName, setNewCharName] = useState('')
  const [newCharRole, setNewCharRole] = useState('')
  const [newLocName, setNewLocName] = useState('')
  const [newLocDesc, setNewLocDesc] = useState('')

  if (!open || !analyzedEntities) return null

  const characters = analyzedEntities.characters || []
  const locations = analyzedEntities.locations || []
  const hasEntities = characters.length > 0 || locations.length > 0

  // -- Character helpers --
  const startEditChar = (i) => {
    const char = characters[i]
    setEditingChar(i)
    setEditValue(char.name || char)
  }

  const saveEditChar = (i) => {
    if (!editValue.trim()) return
    const updated = { ...analyzedEntities }
    const chars = [...characters]
    chars[i] = { ...chars[i], name: editValue.trim() }
    updated.characters = chars
    onUpdate(updated)
    setEditingChar(null)
    setEditValue('')
  }

  const removeChar = (i) => {
    const updated = { ...analyzedEntities }
    updated.characters = characters.filter((_, idx) => idx !== i)
    onUpdate(updated)
  }

  const addChar = () => {
    if (!newCharName.trim()) return
    const updated = { ...analyzedEntities }
    updated.characters = [...characters, { name: newCharName.trim(), role: newCharRole.trim() || 'nhân vật' }]
    onUpdate(updated)
    setNewCharName('')
    setNewCharRole('')
    setAddingChar(false)
  }

  // -- Location helpers --
  const startEditLoc = (i) => {
    const loc = locations[i]
    setEditingLoc(i)
    setEditValue(loc.name || loc)
  }

  const saveEditLoc = (i) => {
    if (!editValue.trim()) return
    const updated = { ...analyzedEntities }
    const locs = [...locations]
    locs[i] = { ...locs[i], name: editValue.trim() }
    updated.locations = locs
    onUpdate(updated)
    setEditingLoc(null)
    setEditValue('')
  }

  const removeLoc = (i) => {
    const updated = { ...analyzedEntities }
    updated.locations = locations.filter((_, idx) => idx !== i)
    onUpdate(updated)
  }

  const addLoc = () => {
    if (!newLocName.trim()) return
    const updated = { ...analyzedEntities }
    updated.locations = [...locations, { name: newLocName.trim(), description: newLocDesc.trim() }]
    onUpdate(updated)
    setNewLocName('')
    setNewLocDesc('')
    setAddingLoc(false)
  }

  const handleConfirm = () => {
    if (onLink) {
      onLink()        // StoryDetail: link + close
    } else {
      onClose?.()     // Create-story: just close modal, entities stay in state
    }
  }

  const handleClear = () => {
    onClear?.()
    onClose?.()
  }

  return (
    <div className="z-50 fixed inset-0 flex justify-center items-center bg-black/40" onClick={onClose}>
      <div
        className="relative bg-base-100 shadow-2xl mx-4 p-6 rounded-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h3 className="flex items-center gap-2 font-bold text-lg">
            <span className="flex justify-center items-center bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-full w-8 h-8 text-emerald-600">
              <OpenAILogo className="w-4 h-4" />
            </span>
            Kết quả phân tích GPT
          </h3>
          <button
            type="button"
            className="btn btn-sm btn-circle btn-ghost"
            onClick={onClose}
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          {/* Characters */}
          {characters.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="opacity-70 text-sm">
                <UserIcon className="inline w-3.5 h-3.5" /> Nhân vật
                <span className="opacity-50"> ({characters.length})</span>
              </span>
              <button
                type="button"
                className="text-primary btn btn-xs btn-ghost"
                onClick={() => setAddingChar(!addingChar)}
                title="Thêm nhân vật"
              >
                <PlusIcon className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {characters.map((char, i) => {
                const name = char.name || char
                const role = char.role || ''

                if (editingChar === i) {
                  return (
                    <div key={i} className="flex items-center gap-1">
                      <input
                        type="text"
                        className="w-28 input input-xs input-bordered"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && saveEditChar(i)}
                        autoFocus
                      />
                      <button
                        type="button"
                        className="text-success btn btn-xs btn-ghost"
                        onClick={() => saveEditChar(i)}
                      >
                        <CheckCircleIcon className="w-3.5 h-3.5" />
                      </button>
                      <button
                        type="button"
                        className="btn btn-xs btn-ghost"
                        onClick={() => setEditingChar(null)}
                      >
                        ✕
                      </button>
                    </div>
                  )
                }

                return (
                  <span
                    key={i}
                    className="group flex items-center gap-1 bg-primary/10 px-2.5 py-1.5 border border-primary/30 rounded-lg font-medium text-primary text-sm"
                  >
                    {name}
                    {role && <span className="opacity-40 text-xs">({role})</span>}
                    <button
                      type="button"
                      className="opacity-0 group-hover:opacity-70 ml-0.5 transition-opacity btn btn-xs btn-ghost btn-circle"
                      onClick={() => startEditChar(i)}
                      title="Sửa tên"
                    >
                      <PencilIcon className="w-3 h-3" />
                    </button>
                    <button
                      type="button"
                      className="opacity-0 group-hover:opacity-70 text-error transition-opacity btn btn-xs btn-ghost btn-circle"
                      onClick={() => removeChar(i)}
                      title="Xóa"
                    >
                      <TrashIcon className="w-3 h-3" />
                    </button>
                  </span>
                )
              })}
            </div>
            {/* Add character form */}
            {addingChar && (
              <div className="flex items-center gap-2 mt-2">
                <input
                  type="text"
                  className="w-32 input input-xs input-bordered"
                  placeholder="Tên nhân vật"
                  value={newCharName}
                  onChange={(e) => setNewCharName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addChar()}
                  autoFocus
                />
                <input
                  type="text"
                  className="w-24 input input-xs input-bordered"
                  placeholder="Vai trò"
                  value={newCharRole}
                  onChange={(e) => setNewCharRole(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addChar()}
                />
                <button type="button" className="btn btn-xs btn-success" onClick={addChar}>Thêm</button>
                <button type="button" className="btn btn-xs btn-ghost" onClick={() => setAddingChar(false)}>Hủy</button>
              </div>
            )}
          </div>
        )}

        {/* Locations */}
        {locations.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="opacity-70 text-sm">
                <MapPinIcon className="inline w-3.5 h-3.5" /> Địa điểm
                <span className="opacity-50"> ({locations.length})</span>
              </span>
              <button
                type="button"
                className="text-secondary btn btn-xs btn-ghost"
                onClick={() => setAddingLoc(!addingLoc)}
                title="Thêm địa điểm"
              >
                <PlusIcon className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {locations.map((loc, i) => {
                const name = loc.name || loc
                const desc = loc.description || ''

                if (editingLoc === i) {
                  return (
                    <div key={i} className="flex items-center gap-1">
                      <input
                        type="text"
                        className="w-28 input input-xs input-bordered"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && saveEditLoc(i)}
                        autoFocus
                      />
                      <button
                        type="button"
                        className="text-success btn btn-xs btn-ghost"
                        onClick={() => saveEditLoc(i)}
                      >
                        <CheckCircleIcon className="w-3.5 h-3.5" />
                      </button>
                      <button
                        type="button"
                        className="btn btn-xs btn-ghost"
                        onClick={() => setEditingLoc(null)}
                      >
                        ✕
                      </button>
                    </div>
                  )
                }

                return (
                  <span
                    key={i}
                    className="group flex items-center gap-1 bg-secondary/10 px-2.5 py-1.5 border border-secondary/30 rounded-lg font-medium text-secondary text-sm"
                  >
                    {name}
                    <button
                      type="button"
                      className="opacity-0 group-hover:opacity-70 ml-0.5 transition-opacity btn btn-xs btn-ghost btn-circle"
                      onClick={() => startEditLoc(i)}
                      title="Sửa tên"
                    >
                      <PencilIcon className="w-3 h-3" />
                    </button>
                    <button
                      type="button"
                      className="opacity-0 group-hover:opacity-70 text-error transition-opacity btn btn-xs btn-ghost btn-circle"
                      onClick={() => removeLoc(i)}
                      title="Xóa"
                    >
                      <TrashIcon className="w-3 h-3" />
                    </button>
                  </span>
                )
              })}
            </div>
            {/* Add location form */}
            {addingLoc && (
              <div className="flex items-center gap-2 mt-2">
                <input
                  type="text"
                  className="w-32 input input-xs input-bordered"
                  placeholder="Tên địa điểm"
                  value={newLocName}
                  onChange={(e) => setNewLocName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addLoc()}
                  autoFocus
                />
                <input
                  type="text"
                  className="w-32 input input-xs input-bordered"
                  placeholder="Mô tả (tùy chọn)"
                  value={newLocDesc}
                  onChange={(e) => setNewLocDesc(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addLoc()}
                />
                <button type="button" className="btn btn-xs btn-success" onClick={addLoc}>Thêm</button>
                <button type="button" className="btn btn-xs btn-ghost" onClick={() => setAddingLoc(false)}>Hủy</button>
              </div>
            )}
          </div>
        )}

        {/* No character/location add buttons when both lists are empty */}
        {!hasEntities && (
          <div className="text-center">
            <p className="opacity-60 mb-2 text-sm">Không tìm thấy nhân vật hoặc địa điểm cụ thể.</p>
            <div className="flex justify-center gap-2">
              <button type="button" className="text-primary btn btn-xs btn-ghost" onClick={() => setAddingChar(true)}>
                <PlusIcon className="w-3.5 h-3.5" /> Thêm nhân vật
              </button>
              <button type="button" className="text-secondary btn btn-xs btn-ghost" onClick={() => setAddingLoc(true)}>
                <PlusIcon className="w-3.5 h-3.5" /> Thêm địa điểm
              </button>
            </div>
            {/* Inline add forms when empty */}
            {addingChar && (
              <div className="flex justify-center items-center gap-2 mt-2">
                <input type="text" className="w-32 input input-xs input-bordered" placeholder="Tên nhân vật" value={newCharName} onChange={(e) => setNewCharName(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addChar()} autoFocus />
                <input type="text" className="w-24 input input-xs input-bordered" placeholder="Vai trò" value={newCharRole} onChange={(e) => setNewCharRole(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addChar()} />
                <button type="button" className="btn btn-xs btn-success" onClick={addChar}>Thêm</button>
                <button type="button" className="btn btn-xs btn-ghost" onClick={() => setAddingChar(false)}>Hủy</button>
              </div>
            )}
            {addingLoc && (
              <div className="flex justify-center items-center gap-2 mt-2">
                <input type="text" className="w-32 input input-xs input-bordered" placeholder="Tên địa điểm" value={newLocName} onChange={(e) => setNewLocName(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addLoc()} autoFocus />
                <input type="text" className="w-32 input input-xs input-bordered" placeholder="Mô tả" value={newLocDesc} onChange={(e) => setNewLocDesc(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addLoc()} />
                <button type="button" className="btn btn-xs btn-success" onClick={addLoc}>Thêm</button>
                <button type="button" className="btn btn-xs btn-ghost" onClick={() => setAddingLoc(false)}>Hủy</button>
              </div>
            )}
          </div>
        )}
      </div>

        {/* Footer buttons */}
        <div className="flex justify-end items-center gap-2 mt-5 pt-4 border-base-300 border-t">
          <button
            type="button"
            className="text-error btn btn-sm btn-ghost"
            onClick={handleClear}
          >
            <TrashIcon className="w-4 h-4" /> Xóa kết quả
          </button>
          {hasEntities && (
            <button
              type="button"
              onClick={handleConfirm}
              className="bg-gradient-to-r from-success hover:from-success/90 to-emerald-500 hover:to-emerald-500/90 shadow-sm border-0 text-white btn btn-sm"
            >
              <CheckCircleIcon className="w-4 h-4" /> {linkLabel}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default AnalyzedEntitiesEditor
