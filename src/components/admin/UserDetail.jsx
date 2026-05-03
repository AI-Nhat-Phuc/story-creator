'use client'

import { useState, useEffect, useCallback } from 'react'
import { adminAPI } from '../../services/api'
import PermissionEditor from './PermissionEditor'
import ActivityLogTable from './ActivityLogTable'
import {
  ShieldCheckIcon,
  ClockIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline'

const TABS = ['Info', 'Permissions', 'Activity']

/**
 * Right-panel detail view for a selected user.
 *
 * Props:
 *   user       – user object (from the users list)
 *   roles      – array of role objects (from /api/admin/roles)
 *   onUpdate   – called after any mutation so the parent can refresh
 *   showToast  – (message, type) => void
 */
function UserDetail({ user, roles, onUpdate, showToast }) {
  const [activeTab, setActiveTab] = useState('Info')
  const [logs, setLogs] = useState([])
  const [logsLoading, setLogsLoading] = useState(false)
  const [savingStatus, setSavingStatus] = useState(false)
  const [savingPerms, setSavingPerms] = useState(false)

  const roleInfo = roles.find((r) => r.role === user.role)
  const isActive = user.metadata?.active !== false
  const isBanned = user.metadata?.banned

  // Load activity logs when the Activity tab is opened
  const loadLogs = useCallback(async () => {
    if (logs.length > 0) return // already loaded
    setLogsLoading(true)
    try {
      const res = await adminAPI.getUserActivityLogs(user.user_id)
      setLogs(res.data.logs || [])
    } catch {
      showToast('Failed to load activity logs', 'error')
    } finally {
      setLogsLoading(false)
    }
  }, [user.user_id, logs.length, showToast])

  // Reset state when a different user is selected
  useEffect(() => {
    setActiveTab('Info')
    setLogs([])
  }, [user.user_id])

  const handleTabChange = (tab) => {
    setActiveTab(tab)
    if (tab === 'Activity') loadLogs()
  }

  // Toggle active / inactive
  const handleToggleStatus = async () => {
    setSavingStatus(true)
    try {
      await adminAPI.toggleUserStatus(user.user_id, !isActive)
      showToast(
        `User ${user.username} marked as ${!isActive ? 'active' : 'inactive'}`,
        'success'
      )
      onUpdate()
    } catch (err) {
      showToast(err.response?.data?.message || 'Failed to update status', 'error')
    } finally {
      setSavingStatus(false)
    }
  }

  // Save permission overrides
  const handleSavePermissions = async (overrides) => {
    setSavingPerms(true)
    try {
      await adminAPI.updateUserPermissions(user.user_id, overrides)
      showToast('Permissions updated', 'success')
      onUpdate()
    } catch (err) {
      showToast(err.response?.data?.message || 'Failed to update permissions', 'error')
    } finally {
      setSavingPerms(false)
    }
  }

  return (
    <div className="flex flex-col h-full" data-testid="user-detail">
      {/* Header */}
      <div className="p-4 border-b border-base-300 bg-base-200">
        <div className="flex items-center gap-3">
          <div className="avatar placeholder">
            <div className="bg-neutral text-neutral-content rounded-full w-12">
              <span className="text-lg">{user.username?.[0]?.toUpperCase() ?? '?'}</span>
            </div>
          </div>
          <div className="flex-1">
            <h2 className="font-bold text-lg leading-tight">{user.username}</h2>
            <p className="opacity-60 text-sm">{user.email}</p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <span
              className={`badge ${roleInfo?.badge_color ?? 'badge-ghost'}`}
              title={roleInfo?.description}
            >
              {roleInfo?.icon} {roleInfo?.label ?? user.role}
            </span>
            <span
              className={`badge badge-sm ${
                isBanned ? 'badge-error' : isActive ? 'badge-success' : 'badge-warning'
              }`}
              data-testid="user-status-badge"
            >
              {isBanned ? 'Banned' : isActive ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs tabs-bordered px-4 pt-2">
        {TABS.map((tab) => (
          <button
            key={tab}
            className={`tab tab-sm ${activeTab === tab ? 'tab-active' : ''}`}
            onClick={() => handleTabChange(tab)}
            data-testid={`tab-${tab.toLowerCase()}`}
          >
            {tab === 'Info' && <UserCircleIcon className="w-4 h-4 mr-1 inline" />}
            {tab === 'Permissions' && <ShieldCheckIcon className="w-4 h-4 mr-1 inline" />}
            {tab === 'Activity' && <ClockIcon className="w-4 h-4 mr-1 inline" />}
            {tab}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'Info' && (
          <div className="space-y-4" data-testid="tab-info-content">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <span className="opacity-60">User ID</span>
              <span className="font-mono text-xs break-all">{user.user_id}</span>

              <span className="opacity-60">Role</span>
              <span>{user.role}</span>

              <span className="opacity-60">Status</span>
              <span>{isBanned ? 'Banned' : isActive ? 'Active' : 'Inactive'}</span>

              <span className="opacity-60">Public worlds</span>
              <span>
                {user.metadata?.public_worlds_count ?? 0} /{' '}
                {user.metadata?.public_worlds_limit ?? '—'}
              </span>

              <span className="opacity-60">Public stories</span>
              <span>
                {user.metadata?.public_stories_count ?? 0} /{' '}
                {user.metadata?.public_stories_limit ?? '—'}
              </span>

              <span className="opacity-60">GPT access</span>
              <span>{user.metadata?.gpt_enabled ? 'Enabled' : 'Disabled'}</span>
            </div>

            {/* Status toggle */}
            {!isBanned && (
              <div className="divider my-2" />
            )}
            {!isBanned && (
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-sm">Account status</p>
                  <p className="opacity-60 text-xs">
                    Inactive users cannot log in or perform any actions.
                  </p>
                </div>
                <button
                  className={`btn btn-sm ${isActive ? 'btn-warning' : 'btn-success'}`}
                  onClick={handleToggleStatus}
                  disabled={savingStatus}
                  data-testid="toggle-status-btn"
                >
                  {savingStatus && <span className="loading loading-spinner loading-xs" />}
                  {isActive ? 'Deactivate' : 'Activate'}
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'Permissions' && (
          <div data-testid="tab-permissions-content">
            <p className="mb-3 text-xs opacity-60">
              Override individual permissions on top of the role's defaults. Changes take effect
              on the user's next API request.
            </p>
            <PermissionEditor
              rolePermissions={roleInfo?.permissions ?? []}
              customPermissions={user.metadata?.custom_permissions ?? {}}
              onSave={handleSavePermissions}
              saving={savingPerms}
            />
          </div>
        )}

        {activeTab === 'Activity' && (
          <div data-testid="tab-activity-content">
            <ActivityLogTable logs={logs} loading={logsLoading} />
          </div>
        )}
      </div>
    </div>
  )
}

export default UserDetail
