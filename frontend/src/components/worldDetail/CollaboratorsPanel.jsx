import React, { useState } from 'react'
import { UserPlusIcon, XMarkIcon, UsersIcon } from '@heroicons/react/24/outline'

function CollaboratorsPanel({ collaborators, canEdit, inviteLoading, onInvite, onRemove }) {
  const [inviteInput, setInviteInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const val = inviteInput.trim()
    if (!val) return
    onInvite(val)
    setInviteInput('')
  }

  const handleRemove = (userId, username) => {
    if (!window.confirm(`Remove ${username} as co-author?`)) return
    onRemove(userId)
  }

  return (
    <div className="card bg-base-200 shadow-sm">
      <div className="card-body p-4 gap-3">
        <h3 className="card-title text-sm flex items-center gap-2">
          <UsersIcon className="w-4 h-4" />
          Collaborators
        </h3>

        {collaborators.length === 0 ? (
          <p className="text-xs text-base-content/50 italic">No co-authors yet.</p>
        ) : (
          <ul className="space-y-1">
            {collaborators.map((c) => (
              <li key={c.user_id} className="flex items-center justify-between gap-2 text-sm">
                <span className="font-medium truncate">{c.username}</span>
                {canEdit && (
                  <button
                    onClick={() => handleRemove(c.user_id, c.username)}
                    className="btn btn-ghost btn-xs text-error"
                    aria-label={`Remove ${c.username}`}
                  >
                    <XMarkIcon className="w-4 h-4" />
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}

        {canEdit && (
          <form onSubmit={handleSubmit} className="flex gap-2 mt-1">
            <input
              type="text"
              value={inviteInput}
              onChange={(e) => setInviteInput(e.target.value)}
              placeholder="Username or email"
              className="input input-bordered input-xs flex-1"
              disabled={inviteLoading}
            />
            <button
              type="submit"
              disabled={inviteLoading || !inviteInput.trim()}
              className="btn btn-primary btn-xs gap-1"
            >
              <UserPlusIcon className="w-4 h-4" />
              {inviteLoading ? <span className="loading loading-spinner loading-xs" /> : 'Invite'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

export default CollaboratorsPanel
