'use client'

import { useState } from 'react'

// All permission names from api/core/permissions.py
const ALL_PERMISSIONS = [
  'manage_users',
  'view_users',
  'ban_users',
  'manage_all_content',
  'delete_any_content',
  'view_all_content',
  'create_world',
  'edit_own_world',
  'delete_own_world',
  'share_world',
  'create_story',
  'edit_own_story',
  'delete_own_story',
  'share_story',
  'create_event',
  'edit_own_event',
  'delete_own_event',
  'use_gpt',
  'use_gpt_unlimited',
  'unlimited_public_worlds',
  'unlimited_public_stories',
  'increased_quota',
]

/**
 * Displays effective role permissions and lets an admin add/remove overrides.
 *
 * Props:
 *   rolePermissions  – string[] of permissions granted by the user's role
 *   customPermissions – {[name]: bool} overrides stored in metadata
 *   onSave           – async (newOverrides: {[name]: bool}) => void
 *   saving           – bool, disables save button while request is in flight
 */
function PermissionEditor({ rolePermissions = [], customPermissions = {}, onSave, saving }) {
  // Local draft of overrides (mirrors server state on open, tracks user edits)
  const [overrides, setOverrides] = useState({ ...customPermissions })

  const toggle = (perm, value) => {
    setOverrides((prev) => {
      const next = { ...prev }
      if (value === null) {
        // null = remove override (fall back to role default)
        delete next[perm]
      } else {
        next[perm] = value
      }
      return next
    })
  }

  const handleSave = () => onSave(overrides)

  return (
    <div data-testid="permission-editor">
      <div className="overflow-x-auto max-h-72 overflow-y-auto">
        <table className="table table-xs w-full">
          <thead className="sticky top-0 bg-base-100 z-10">
            <tr>
              <th>Permission</th>
              <th className="text-center">Role default</th>
              <th className="text-center">Override</th>
            </tr>
          </thead>
          <tbody>
            {ALL_PERMISSIONS.map((perm) => {
              const roleHas = rolePermissions.includes(perm)
              const override = overrides[perm] // true | false | undefined
              const effective = override !== undefined ? override : roleHas

              return (
                <tr key={perm} className={effective ? '' : 'opacity-40'}>
                  <td className="font-mono text-xs">{perm}</td>
                  <td className="text-center">
                    {roleHas ? (
                      <span className="text-success text-xs">✓</span>
                    ) : (
                      <span className="text-error text-xs">✗</span>
                    )}
                  </td>
                  <td>
                    <div className="flex justify-center gap-1">
                      <button
                        title="Grant"
                        className={`btn btn-xs ${override === true ? 'btn-success' : 'btn-ghost'}`}
                        onClick={() => toggle(perm, override === true ? null : true)}
                        data-testid={`grant-${perm}`}
                      >
                        +
                      </button>
                      <button
                        title="Revoke"
                        className={`btn btn-xs ${override === false ? 'btn-error' : 'btn-ghost'}`}
                        onClick={() => toggle(perm, override === false ? null : false)}
                        data-testid={`revoke-${perm}`}
                      >
                        –
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center mt-3">
        <p className="text-xs opacity-50">
          + grants regardless of role · – revokes regardless of role · no button = role default
        </p>
        <button
          className="btn btn-primary btn-sm"
          onClick={handleSave}
          disabled={saving}
          data-testid="save-permissions-btn"
        >
          {saving ? <span className="loading loading-spinner loading-xs" /> : 'Save'}
        </button>
      </div>
    </div>
  )
}

export default PermissionEditor
