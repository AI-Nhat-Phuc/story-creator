'use client'

import React from 'react'
import { BellIcon } from '@heroicons/react/24/outline'

function InvitationsDropdown({ invitations, onAccept, onDecline }) {
  const count = invitations.length

  return (
    <div className="dropdown dropdown-end">
      <label tabIndex={0} className="btn btn-ghost btn-circle relative">
        <BellIcon className="w-5 h-5" />
        {count > 0 && (
          <span className="badge badge-error badge-xs absolute -top-1 -right-1">
            {count}
          </span>
        )}
      </label>

      <div tabIndex={0} className="dropdown-content bg-base-100 shadow rounded-box z-50 mt-3 w-72 text-base-content p-2">
        <p className="text-xs font-semibold text-base-content/60 uppercase tracking-wider px-2 py-1">
          Invitations
        </p>

        {count === 0 ? (
          <p className="text-sm text-base-content/50 italic px-2 py-3">No pending invitations</p>
        ) : (
          <ul className="space-y-2">
            {invitations.map((inv) => (
              <li key={inv.invitation_id} className="bg-base-200 rounded p-2 text-sm space-y-1">
                <p className="font-medium truncate">{inv.world_title}</p>
                <p className="text-xs text-base-content/60">from {inv.invited_by}</p>
                <div className="flex gap-2 mt-1">
                  <button
                    onClick={() => onAccept(inv.invitation_id)}
                    className="btn btn-success btn-xs flex-1"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => onDecline(inv.invitation_id)}
                    className="btn btn-ghost btn-xs flex-1"
                  >
                    Decline
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default InvitationsDropdown
