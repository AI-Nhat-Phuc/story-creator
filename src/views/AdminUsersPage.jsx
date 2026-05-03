'use client'

import { useState, useEffect, useCallback } from 'react'
import { adminAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from '../utils/router-compat'
import { Helmet } from 'react-helmet-async'
import LoadingSpinner from '../components/LoadingSpinner'
import UserList from '../components/admin/UserList'
import UserDetail from '../components/admin/UserDetail'
import { UsersIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'

/**
 * /admin/users — two-panel admin user management page.
 *
 * Left panel  : UserList (searchable, filterable)
 * Right panel : UserDetail (info / permissions / activity tabs)
 */
function AdminUsersPage({ showToast }) {
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])
  const [selectedUser, setSelectedUser] = useState(null)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [loading, setLoading] = useState(true)

  const isAdmin = user?.role === 'admin'
  const isModerator = user?.role === 'moderator'

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    if (!isAdmin && !isModerator) {
      showToast('Access denied', 'error')
      navigate('/')
      return
    }
    loadAll()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user])

  const loadAll = useCallback(async () => {
    setLoading(true)
    try {
      const [usersRes, rolesRes] = await Promise.all([
        adminAPI.getAllUsers({ search, role: roleFilter || undefined }),
        adminAPI.getRoles(),
      ])
      setUsers(usersRes.data.users ?? [])
      setRoles(rolesRes.data.roles ?? [])
    } catch (err) {
      if (err.response?.status === 403) {
        showToast('Access denied', 'error')
        navigate('/')
      } else {
        showToast('Failed to load users', 'error')
      }
    } finally {
      setLoading(false)
    }
  }, [search, roleFilter]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSearch = () => loadAll()

  // Re-fetch the selected user's record after a mutation so the detail panel
  // reflects the latest server state without requiring a full list reload.
  const handleUpdate = useCallback(async () => {
    await loadAll()
    if (selectedUser) {
      try {
        const res = await adminAPI.getUserDetail(selectedUser.user_id)
        setSelectedUser(res.data.user)
      } catch {
        // swallow — the list reload is enough
      }
    }
  }, [selectedUser, loadAll])

  if (loading && users.length === 0) return <LoadingSpinner />

  return (
    <div className="flex flex-col h-full">
      <Helmet>
        <title>User Management — Admin</title>
      </Helmet>

      {/* Page header */}
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div className="flex items-center gap-2">
          <ShieldCheckIcon className="w-6 h-6 text-primary" />
          <h1 className="font-bold text-2xl">User Management</h1>
          <span className="badge badge-ghost ml-1">{users.length} users</span>
        </div>

        {/* Role filter */}
        <select
          className="select select-bordered select-sm"
          value={roleFilter}
          onChange={(e) => { setRoleFilter(e.target.value); }}
          data-testid="role-filter"
        >
          <option value="">All roles</option>
          {roles.map((r) => (
            <option key={r.role} value={r.role}>
              {r.icon} {r.label}
            </option>
          ))}
        </select>
      </div>

      {/* Two-panel layout */}
      <div className="flex gap-4 flex-1 min-h-0">
        {/* Left: user list */}
        <div
          className="bg-base-100 border border-base-300 rounded-box shadow flex flex-col overflow-hidden"
          style={{ width: '280px', flexShrink: 0 }}
          data-testid="user-list-panel"
        >
          <div className="flex items-center gap-2 px-3 pt-3 pb-1 shrink-0">
            <UsersIcon className="w-4 h-4 opacity-60" />
            <span className="font-semibold text-sm">Users</span>
          </div>
          <UserList
            users={users}
            selectedUserId={selectedUser?.user_id}
            onSelect={(u) => setSelectedUser(u)}
            search={search}
            onSearchChange={setSearch}
            onSearch={handleSearch}
            loading={loading}
          />
        </div>

        {/* Right: user detail */}
        <div
          className="flex-1 bg-base-100 border border-base-300 rounded-box shadow overflow-hidden flex flex-col"
          data-testid="user-detail-panel"
        >
          {selectedUser ? (
            <UserDetail
              user={selectedUser}
              roles={roles}
              onUpdate={handleUpdate}
              showToast={showToast}
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full opacity-40">
              <UsersIcon className="w-12 h-12 mb-2" />
              <p>Select a user to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminUsersPage
