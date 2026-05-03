'use client'

import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

function StatusBadge({ active, banned }) {
  if (banned) return <span className="badge badge-error badge-sm">Banned</span>
  if (!active) return <span className="badge badge-warning badge-sm">Inactive</span>
  return <span className="badge badge-success badge-sm">Active</span>
}

/**
 * Left-panel user list for the Admin Users page.
 *
 * Props:
 *   users          – array of user objects
 *   selectedUserId – currently selected user id (or null)
 *   onSelect       – called with a user object when a row is clicked
 *   search         – controlled search string
 *   onSearchChange – called with new search string
 *   onSearch       – called when the search is submitted
 *   loading        – show skeleton rows when true
 */
function UserList({ users, selectedUserId, onSelect, search, onSearchChange, onSearch, loading }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') onSearch()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Search bar */}
      <div className="p-3 border-b border-base-300">
        <div className="flex gap-2">
          <input
            type="text"
            className="input input-bordered input-sm flex-1"
            placeholder="Search users…"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyDown={handleKeyDown}
            data-testid="user-search"
          />
          <button className="btn btn-sm btn-square" onClick={onSearch} aria-label="Search">
            <MagnifyingGlassIcon className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* User rows */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex gap-3 items-center p-3 animate-pulse">
              <div className="bg-base-300 rounded-full w-8 h-8 shrink-0" />
              <div className="flex-1 space-y-1">
                <div className="bg-base-300 rounded h-3 w-24" />
                <div className="bg-base-300 rounded h-2 w-32" />
              </div>
            </div>
          ))
        ) : users.length === 0 ? (
          <p className="p-4 text-center opacity-50 text-sm">No users found.</p>
        ) : (
          users.map((u) => {
            const isSelected = u.user_id === selectedUserId
            const banned = u.metadata?.banned
            const active = u.metadata?.active !== false

            return (
              <button
                key={u.user_id}
                className={`w-full text-left flex items-center gap-3 px-3 py-2.5 border-b border-base-200 hover:bg-base-200 transition-colors ${
                  isSelected ? 'bg-primary/10 border-l-2 border-l-primary' : ''
                }`}
                onClick={() => onSelect(u)}
                data-testid={`user-row-${u.user_id}`}
              >
                <div className="avatar placeholder shrink-0">
                  <div className="bg-neutral text-neutral-content rounded-full w-8">
                    <span className="text-xs">{u.username?.[0]?.toUpperCase() ?? '?'}</span>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm truncate">{u.username}</p>
                  <p className="opacity-60 text-xs truncate">{u.email}</p>
                </div>
                <StatusBadge active={active} banned={banned} />
              </button>
            )
          })
        )}
      </div>
    </div>
  )
}

export default UserList
