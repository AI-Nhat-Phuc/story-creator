import { useState, useEffect } from 'react'
import { adminAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'
import {
  ShieldCheckIcon,
  UsersIcon,
  GlobeAltIcon,
  BookOpenIcon,
  NoSymbolIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline'

function AdminPanel({ showToast }) {
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])
  const [stats, setStats] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [showRoleModal, setShowRoleModal] = useState(false)
  const [showBanModal, setShowBanModal] = useState(false)
  const [banReason, setBanReason] = useState('')

  useEffect(() => {
    // Check if user is admin or moderator
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    if (user?.role !== 'admin' && user?.role !== 'moderator') {
      showToast('Bạn không có quyền truy cập trang này', 'error')
      navigate('/')
      return
    }

    loadData()
  }, [isAuthenticated, user])

  const loadData = async () => {
    try {
      setLoading(true)
      const [usersRes, rolesRes, statsRes] = await Promise.all([
        adminAPI.getAllUsers({ role: roleFilter, search: searchQuery }),
        adminAPI.getRoles(),
        adminAPI.getAdminStats()
      ])

      setUsers(usersRes.data.users || [])
      setRoles(rolesRes.data.roles || [])
      setStats(statsRes.data.stats || {})
    } catch (error) {
      console.error('Error loading admin data:', error)
      if (error.response?.status === 403) {
        showToast('Không có quyền truy cập', 'error')
        navigate('/')
      } else {
        showToast('Không thể tải dữ liệu quản trị', 'error')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    loadData()
  }

  const handleChangeRole = async (newRole) => {
    if (!selectedUser) return

    try {
      await adminAPI.changeUserRole(selectedUser.user_id, newRole)
      showToast(`Đã đổi role của ${selectedUser.username} thành ${newRole}`, 'success')
      setShowRoleModal(false)
      setSelectedUser(null)
      loadData()
    } catch (error) {
      showToast(error.response?.data?.message || 'Không thể đổi role', 'error')
    }
  }

  const handleBanUser = async (banned) => {
    if (!selectedUser) return

    try {
      await adminAPI.banUser(selectedUser.user_id, banned, banReason)
      showToast(`Đã ${banned ? 'ban' : 'unban'} user ${selectedUser.username}`, 'success')
      setShowBanModal(false)
      setSelectedUser(null)
      setBanReason('')
      loadData()
    } catch (error) {
      showToast(error.response?.data?.message || `Không thể ${banned ? 'ban' : 'unban'} user`, 'error')
    }
  }

  const getRoleBadge = (role) => {
    const roleInfo = roles.find(r => r.role === role)
    if (!roleInfo) return <span className="badge">{role}</span>

    return (
      <span className={`badge ${roleInfo.badge_color} gap-1`}>
        <span>{roleInfo.icon}</span>
        {roleInfo.label}
      </span>
    )
  }

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="mb-6">
        <h1 className="flex items-center gap-2 mb-2 font-bold text-3xl">
          <span><ShieldCheckIcon className="inline w-7 h-7" /></span>
          <span>Quản trị hệ thống</span>
        </h1>
        <p className="opacity-70">Quản lý người dùng và phân quyền</p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="gap-4 grid grid-cols-1 md:grid-cols-4 mb-6">
          <div className="bg-base-100 shadow rounded-box stat">
            <div className="text-primary stat-figure"><UsersIcon className="w-8 h-8" /></div>
            <div className="stat-title">Tổng users</div>
            <div className="text-primary stat-value">{stats.total_users}</div>
          </div>

          <div className="bg-base-100 shadow rounded-box stat">
            <div className="text-secondary stat-figure"><GlobeAltIcon className="w-8 h-8" /></div>
            <div className="stat-title">Thế giới</div>
            <div className="text-secondary stat-value">{stats.total_worlds}</div>
            <div className="stat-desc">{stats.public_worlds} công khai</div>
          </div>

          <div className="bg-base-100 shadow rounded-box stat">
            <div className="text-accent stat-figure"><BookOpenIcon className="w-8 h-8" /></div>
            <div className="stat-title">Câu chuyện</div>
            <div className="text-accent stat-value">{stats.total_stories}</div>
            <div className="stat-desc">{stats.public_stories} công khai</div>
          </div>

          <div className="bg-base-100 shadow rounded-box stat">
            <div className="text-error stat-figure"><NoSymbolIcon className="w-8 h-8" /></div>
            <div className="stat-title">Users bị ban</div>
            <div className="text-error stat-value">{stats.banned_users}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-base-100 shadow mb-6 p-4 rounded-box">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px] form-control">
            <div className="input-group">
              <input
                type="text"
                placeholder="Tìm username hoặc email..."
                className="flex-1 input input-bordered"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button className="btn btn-square" onClick={handleSearch}>
                <MagnifyingGlassIcon className="w-5 h-5" />
              </button>
            </div>
          </div>

          <select
            className="select-bordered select"
            value={roleFilter}
            onChange={(e) => { setRoleFilter(e.target.value); handleSearch() }}
          >
            <option value="">Tất cả roles</option>
            {roles.map(role => (
              <option key={role.role} value={role.role}>
                {role.icon} {role.label}
              </option>
            ))}
          </select>

          <button className="btn btn-primary" onClick={loadData}>
                        <ArrowPathIcon className="inline w-4 h-4" /> Tải lại
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-base-100 shadow rounded-box overflow-x-auto">
        <table className="table w-full">
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th>Quota</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.user_id} className={u.metadata?.banned ? 'opacity-50' : ''}>
                <td>
                  <div className="font-bold">{u.username}</div>
                  <div className="opacity-50 text-sm">{u.user_id.slice(0, 8)}</div>
                </td>
                <td>{u.email}</td>
                <td>{getRoleBadge(u.role)}</td>
                <td>
                  {u.role === 'admin' ? (
                    <div className="opacity-70 text-sm">Quản lý hệ thống</div>
                  ) : (
                    <div className="text-sm">
                      <div><GlobeAltIcon className="inline w-4 h-4" /> {u.metadata?.public_worlds_count || 0}/{u.metadata?.public_worlds_limit || 0}</div>
                      <div><BookOpenIcon className="inline w-4 h-4" /> {u.metadata?.public_stories_count || 0}/{u.metadata?.public_stories_limit || 0}</div>
                    </div>
                  )}
                </td>
                <td>
                  {u.metadata?.banned ? (
                    <span className="badge badge-error">Banned</span>
                  ) : (
                    <span className="badge badge-success">Active</span>
                  )}
                </td>
                <td>
                  <div className="flex gap-2">
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => { setSelectedUser(u); setShowRoleModal(true) }}
                      disabled={u.user_id === user.user_id}
                    >
                      Đổi role
                    </button>
                    <button
                      className={`btn btn-sm ${u.metadata?.banned ? 'btn-success' : 'btn-error'}`}
                      onClick={() => { setSelectedUser(u); setShowBanModal(true) }}
                      disabled={u.user_id === user.user_id || (user.role === 'moderator' && u.role === 'admin')}
                    >
                      {u.metadata?.banned ? 'Unban' : 'Ban'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {users.length === 0 && (
          <div className="py-8 text-center">
            <p className="opacity-60">Không tìm thấy user nào</p>
          </div>
        )}
      </div>

      {/* Change Role Modal */}
      {showRoleModal && selectedUser && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="mb-4 font-bold text-lg">
              Đổi role cho {selectedUser.username}
            </h3>

            <div className="mb-4">
              <p className="opacity-70 mb-2">Role hiện tại: {getRoleBadge(selectedUser.role)}</p>
              <p className="font-semibold">Chọn role mới:</p>
            </div>

            <div className="gap-2 grid grid-cols-1">
              {roles.map(role => {
                const isCurrentRole = role.role === selectedUser.role
                return (
                  <button
                    key={role.role}
                    className={`btn justify-start ${isCurrentRole ? 'btn-disabled' : 'btn-outline'}`}
                    onClick={() => !isCurrentRole && handleChangeRole(role.role)}
                    disabled={isCurrentRole}
                  >
                    <span className="text-2xl">{role.icon}</span>
                    <div className="flex-1 text-left">
                      <div className="font-bold">{role.label}</div>
                      <div className="opacity-70 text-xs">{role.description}</div>
                      {role.quotas && (
                        <div className="opacity-60 mt-1 text-xs">
                          {role.role === 'admin' ? (
                            <span>Không tạo nội dung</span>
                          ) : (
                            <span>
                              <GlobeAltIcon className="inline w-3.5 h-3.5" /> {role.quotas.public_worlds} ·
                              <BookOpenIcon className="inline w-3.5 h-3.5" /> {role.quotas.public_stories} ·
                              <CpuChipIcon className="inline w-3.5 h-3.5" /> {role.quotas.gpt_per_day}/ngày
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    {isCurrentRole && <span className="badge badge-sm">Hiện tại</span>}
                  </button>
                )
              })}
            </div>

            <div className="modal-action">
              <button className="btn" onClick={() => { setShowRoleModal(false); setSelectedUser(null) }}>
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Ban/Unban Modal */}
      {showBanModal && selectedUser && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="mb-4 font-bold text-lg">
              {selectedUser.metadata?.banned ? 'Unban' : 'Ban'} user {selectedUser.username}
            </h3>

            {!selectedUser.metadata?.banned && (
              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">Lý do ban:</span>
                </label>
                <textarea
                  className="textarea textarea-bordered"
                  placeholder="Nhập lý do..."
                  value={banReason}
                  onChange={(e) => setBanReason(e.target.value)}
                />
              </div>
            )}

            {selectedUser.metadata?.banned && (
              <div className="mb-4 alert alert-info">
                <div>
                  <p className="font-semibold">Lý do ban hiện tại:</p>
                  <p>{selectedUser.metadata?.ban_reason || 'Không có lý do'}</p>
                </div>
              </div>
            )}

            <div className="modal-action">
              <button
                className={`btn ${selectedUser.metadata?.banned ? 'btn-success' : 'btn-error'}`}
                onClick={() => handleBanUser(!selectedUser.metadata?.banned)}
              >
                {selectedUser.metadata?.banned ? 'Unban' : 'Ban'} user
              </button>
              <button className="btn" onClick={() => { setShowBanModal(false); setSelectedUser(null); setBanReason('') }}>
                Hủy
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminPanel
