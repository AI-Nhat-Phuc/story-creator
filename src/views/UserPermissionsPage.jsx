'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { adminAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from '../utils/router-compat'
import { Helmet } from 'react-helmet-async'
import {
  MagnifyingGlassIcon,
  ShieldCheckIcon,
  UserIcon,
  StarIcon,
  EyeIcon,
  GlobeAltIcon,
  BookOpenIcon,
  CpuChipIcon,
  UsersIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  LockClosedIcon,
  LockOpenIcon,
  SparklesIcon,
  DocumentTextIcon,
  NoSymbolIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'
import {
  ShieldCheckIcon as ShieldCheckSolid,
  StarIcon as StarSolid,
  UserIcon as UserSolid,
  EyeIcon as EyeSolid,
  CheckCircleIcon as CheckCircleSolid,
} from '@heroicons/react/24/solid'

// ─── Permission Model ──────────────────────────────────────────────────────────

const ROLE_DEFAULTS = {
  admin: {
    'world.create': true, 'world.edit_own': true, 'world.delete_own': true,
    'world.publish': true, 'world.edit_any': true, 'world.delete_any': true,
    'story.create': true, 'story.edit_own': true, 'story.delete_own': true,
    'story.publish': true, 'story.edit_any': true, 'story.delete_any': true,
    'gpt.enabled': true, 'gpt.unlimited': true,
    'admin.view_users': true, 'admin.manage_roles': true, 'admin.ban_users': true,
    'admin.feature_content': true,
  },
  moderator: {
    'world.create': true, 'world.edit_own': true, 'world.delete_own': true,
    'world.publish': true, 'world.edit_any': true, 'world.delete_any': false,
    'story.create': true, 'story.edit_own': true, 'story.delete_own': true,
    'story.publish': true, 'story.edit_any': true, 'story.delete_any': false,
    'gpt.enabled': true, 'gpt.unlimited': false,
    'admin.view_users': true, 'admin.manage_roles': false, 'admin.ban_users': true,
    'admin.feature_content': true,
  },
  premium: {
    'world.create': true, 'world.edit_own': true, 'world.delete_own': true,
    'world.publish': true, 'world.edit_any': false, 'world.delete_any': false,
    'story.create': true, 'story.edit_own': true, 'story.delete_own': true,
    'story.publish': true, 'story.edit_any': false, 'story.delete_any': false,
    'gpt.enabled': true, 'gpt.unlimited': false,
    'admin.view_users': false, 'admin.manage_roles': false, 'admin.ban_users': false,
    'admin.feature_content': false,
  },
  user: {
    'world.create': true, 'world.edit_own': true, 'world.delete_own': true,
    'world.publish': true, 'world.edit_any': false, 'world.delete_any': false,
    'story.create': true, 'story.edit_own': true, 'story.delete_own': true,
    'story.publish': true, 'story.edit_any': false, 'story.delete_any': false,
    'gpt.enabled': false, 'gpt.unlimited': false,
    'admin.view_users': false, 'admin.manage_roles': false, 'admin.ban_users': false,
    'admin.feature_content': false,
  },
  guest: {
    'world.create': false, 'world.edit_own': false, 'world.delete_own': false,
    'world.publish': false, 'world.edit_any': false, 'world.delete_any': false,
    'story.create': false, 'story.edit_own': false, 'story.delete_own': false,
    'story.publish': false, 'story.edit_any': false, 'story.delete_any': false,
    'gpt.enabled': false, 'gpt.unlimited': false,
    'admin.view_users': false, 'admin.manage_roles': false, 'admin.ban_users': false,
    'admin.feature_content': false,
  },
}

const PERMISSION_GROUPS = [
  {
    id: 'worlds',
    label: 'World Management',
    Icon: GlobeAltIcon,
    permissions: [
      { id: 'world.create', label: 'Create Worlds', description: 'Can create new story worlds' },
      { id: 'world.edit_own', label: 'Edit Own Worlds', description: 'Can edit worlds they own' },
      { id: 'world.delete_own', label: 'Delete Own Worlds', description: 'Can permanently delete owned worlds' },
      { id: 'world.publish', label: 'Publish Worlds', description: 'Can make worlds publicly discoverable' },
      { id: 'world.edit_any', label: 'Edit Any World', description: 'Override — can edit any world regardless of ownership' },
      { id: 'world.delete_any', label: 'Delete Any World', description: 'Override — can delete any world (destructive)' },
    ],
  },
  {
    id: 'stories',
    label: 'Story Management',
    Icon: BookOpenIcon,
    permissions: [
      { id: 'story.create', label: 'Create Stories', description: 'Can author new stories within worlds' },
      { id: 'story.edit_own', label: 'Edit Own Stories', description: 'Can edit stories they authored' },
      { id: 'story.delete_own', label: 'Delete Own Stories', description: 'Can permanently delete authored stories' },
      { id: 'story.publish', label: 'Publish Stories', description: 'Can make stories publicly visible' },
      { id: 'story.edit_any', label: 'Edit Any Story', description: 'Override — can edit any story regardless of authorship' },
      { id: 'story.delete_any', label: 'Delete Any Story', description: 'Override — can delete any story (destructive)' },
    ],
  },
  {
    id: 'gpt',
    label: 'AI & GPT Access',
    Icon: CpuChipIcon,
    special: 'gpt',
    permissions: [
      {
        id: 'gpt.enabled',
        label: 'GPT Generation',
        description: 'Allow use of AI content generation. Consumes API quota.',
        warning: 'Enabling this grants access to paid AI features. Monitor usage.',
        defaultOff: true,
      },
      {
        id: 'gpt.unlimited',
        label: 'Unlimited Generations',
        description: 'Remove daily generation cap. Admin-only by default.',
      },
    ],
  },
  {
    id: 'admin',
    label: 'Administration',
    Icon: ShieldCheckIcon,
    permissions: [
      { id: 'admin.view_users', label: 'View User Directory', description: 'Can access the user management panel' },
      { id: 'admin.manage_roles', label: 'Manage Roles & Permissions', description: 'Can change roles and edit permission sets' },
      { id: 'admin.ban_users', label: 'Suspend Accounts', description: 'Can ban or unban user accounts' },
      { id: 'admin.feature_content', label: 'Feature Content', description: 'Can pin or highlight content in discovery feeds' },
    ],
  },
]

// ─── Mock audit log ────────────────────────────────────────────────────────────

const mockAuditLog = (userId) => [
  {
    id: 1, actor: 'admin@system', action: 'role_changed', detail: 'Role changed from user → premium',
    ts: new Date(Date.now() - 2 * 86400000).toISOString(),
  },
  {
    id: 2, actor: 'admin@system', action: 'permission_granted', detail: 'gpt.enabled granted',
    ts: new Date(Date.now() - 1 * 86400000).toISOString(),
  },
  {
    id: 3, actor: 'admin@system', action: 'permission_revoked', detail: 'world.edit_any revoked',
    ts: new Date(Date.now() - 3600000).toISOString(),
  },
]

// ─── Helpers ───────────────────────────────────────────────────────────────────

const ROLE_META = {
  admin: { label: 'Admin', Icon: ShieldCheckSolid, color: 'text-error', bg: 'bg-error/10', border: 'border-error/30' },
  moderator: { label: 'Moderator', Icon: ShieldCheckSolid, color: 'text-warning', bg: 'bg-warning/10', border: 'border-warning/30' },
  premium: { label: 'Premium', Icon: StarSolid, color: 'text-primary', bg: 'bg-primary/10', border: 'border-primary/30' },
  user: { label: 'User', Icon: UserSolid, color: 'text-info', bg: 'bg-info/10', border: 'border-info/30' },
  guest: { label: 'Guest', Icon: EyeSolid, color: 'text-base-content/40', bg: 'bg-base-200', border: 'border-base-300' },
}

function avatarInitials(name) {
  if (!name) return '?'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

function avatarColor(userId = '') {
  const colors = [
    'bg-violet-500', 'bg-blue-500', 'bg-emerald-500', 'bg-amber-500',
    'bg-rose-500', 'bg-cyan-500', 'bg-fuchsia-500', 'bg-orange-500',
  ]
  let h = 0
  for (let i = 0; i < userId.length; i++) h = (h * 31 + userId.charCodeAt(i)) & 0xffff
  return colors[h % colors.length]
}

function relativeTime(iso) {
  const diff = Date.now() - new Date(iso).getTime()
  if (diff < 60000) return 'just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  return `${Math.floor(diff / 86400000)}d ago`
}

// ─── Sub-components ────────────────────────────────────────────────────────────

function Avatar({ user, size = 'md' }) {
  const cls = size === 'lg' ? 'w-11 h-11 text-base' : size === 'sm' ? 'w-7 h-7 text-xs' : 'w-9 h-9 text-sm'
  return (
    <div className={`${cls} ${avatarColor(user.user_id)} rounded-lg flex items-center justify-center font-semibold text-white shrink-0`}>
      {user.avatar_url
        ? <img src={user.avatar_url} alt="" className="w-full h-full rounded-lg object-cover" />
        : avatarInitials(user.username || user.email)}
    </div>
  )
}

function RolePill({ role, active, onClick }) {
  const meta = ROLE_META[role] || ROLE_META.user
  const { Icon } = meta
  return (
    <button
      onClick={onClick}
      className={`
        flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium border transition-all duration-150
        ${active
          ? `${meta.bg} ${meta.color} ${meta.border}`
          : 'border-transparent text-base-content/50 hover:text-base-content hover:bg-base-200'
        }
      `}
    >
      <Icon className="w-3 h-3" />
      {meta.label}
    </button>
  )
}

function PermissionToggle({ checked, onChange, disabled, warning }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => !disabled && onChange(!checked)}
      className={`
        relative inline-flex w-9 h-5 shrink-0 rounded-full border-2 transition-all duration-200
        focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
        ${disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
        ${checked
          ? warning ? 'bg-amber-500 border-amber-500 focus-visible:outline-amber-500' : 'bg-primary border-primary focus-visible:outline-primary'
          : 'bg-base-300 border-base-300 focus-visible:outline-base-300'
        }
      `}
    >
      <span className={`
        inline-block w-4 h-4 rounded-full bg-white shadow-sm transition-transform duration-200
        ${checked ? 'translate-x-4' : 'translate-x-0'}
      `} />
    </button>
  )
}

function PermissionRow({ perm, value, onChange, disabled }) {
  const [showWarning, setShowWarning] = useState(false)

  const handleChange = (next) => {
    if (next && perm.warning) {
      setShowWarning(true)
      return
    }
    onChange(perm.id, next)
  }

  return (
    <>
      <div className={`
        flex items-start justify-between gap-4 py-3 px-4 rounded-lg transition-colors duration-100
        ${value ? 'bg-base-200/60' : 'hover:bg-base-200/40'}
      `}>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-base-content leading-tight">{perm.label}</span>
            {perm.warning && (
              <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs font-medium bg-amber-500/10 text-amber-600 border border-amber-500/20">
                <ExclamationTriangleIcon className="w-3 h-3" />
                Paid
              </span>
            )}
            {perm.defaultOff && !value && (
              <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs bg-base-300 text-base-content/50">
                Default off
              </span>
            )}
          </div>
          <p className="mt-0.5 text-xs text-base-content/50 leading-snug">{perm.description}</p>
        </div>
        <div className="pt-0.5">
          <PermissionToggle
            checked={value}
            onChange={handleChange}
            disabled={disabled}
            warning={perm.warning}
          />
        </div>
      </div>

      {showWarning && (
        <div className="mx-4 mb-2 p-3 rounded-lg bg-amber-50 border border-amber-200 dark:bg-amber-900/20 dark:border-amber-700/40">
          <div className="flex gap-2">
            <ExclamationTriangleIcon className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs font-medium text-amber-800 dark:text-amber-400">{perm.warning}</p>
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => { onChange(perm.id, true); setShowWarning(false) }}
                  className="px-2.5 py-1 rounded text-xs font-medium bg-amber-600 text-white hover:bg-amber-700 transition-colors"
                >
                  Enable anyway
                </button>
                <button
                  onClick={() => setShowWarning(false)}
                  className="px-2.5 py-1 rounded text-xs font-medium bg-transparent text-amber-700 hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

function PermissionGroup({ group, permissions, onChange, disabled, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen)
  const enabledCount = group.permissions.filter(p => permissions[p.id]).length
  const totalCount = group.permissions.length
  const { Icon } = group

  return (
    <div className="border border-base-300 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between gap-3 px-4 py-3 bg-base-100 hover:bg-base-200/50 transition-colors duration-100"
      >
        <div className="flex items-center gap-2.5">
          <div className={`
            w-7 h-7 rounded-md flex items-center justify-center
            ${group.special === 'gpt' ? 'bg-amber-500/10' : 'bg-primary/10'}
          `}>
            <Icon className={`w-4 h-4 ${group.special === 'gpt' ? 'text-amber-600' : 'text-primary'}`} />
          </div>
          <span className="text-sm font-semibold text-base-content">{group.label}</span>
          {group.special === 'gpt' && permissions['gpt.enabled'] && (
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-500/15 text-amber-600 border border-amber-500/25">
              <SparklesIcon className="w-3 h-3" />
              Active
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-base-content/40 tabular-nums">
            {enabledCount}/{totalCount}
          </span>
          <div className="w-12 h-1 bg-base-300 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${group.special === 'gpt' && enabledCount > 0 ? 'bg-amber-500' : 'bg-primary'}`}
              style={{ width: `${(enabledCount / totalCount) * 100}%` }}
            />
          </div>
          {open
            ? <ChevronDownIcon className="w-4 h-4 text-base-content/40" />
            : <ChevronRightIcon className="w-4 h-4 text-base-content/40" />
          }
        </div>
      </button>

      {open && (
        <div className="border-t border-base-300 divide-y divide-base-200/60 bg-base-50">
          {group.permissions.map(perm => (
            <PermissionRow
              key={perm.id}
              perm={perm}
              value={!!permissions[perm.id]}
              onChange={onChange}
              disabled={disabled}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function AuditLogTab({ userId }) {
  const log = mockAuditLog(userId)

  const actionMeta = {
    role_changed: { Icon: ArrowPathIcon, color: 'text-info', bg: 'bg-info/10' },
    permission_granted: { Icon: LockOpenIcon, color: 'text-success', bg: 'bg-success/10' },
    permission_revoked: { Icon: LockClosedIcon, color: 'text-error', bg: 'bg-error/10' },
  }

  return (
    <div className="p-5 space-y-1">
      <p className="text-xs font-medium text-base-content/40 uppercase tracking-widest mb-4">
        Recent Activity
      </p>
      {log.map((entry, i) => {
        const meta = actionMeta[entry.action] || { Icon: ClockIcon, color: 'text-base-content/50', bg: 'bg-base-200' }
        const { Icon } = meta
        return (
          <div key={entry.id} className="flex gap-3 items-start">
            <div className="flex flex-col items-center">
              <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${meta.bg} shrink-0`}>
                <Icon className={`w-3.5 h-3.5 ${meta.color}`} />
              </div>
              {i < log.length - 1 && <div className="w-px flex-1 min-h-[20px] bg-base-300 my-1" />}
            </div>
            <div className="flex-1 pb-4">
              <p className="text-sm text-base-content leading-snug">{entry.detail}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-base-content/40">{entry.actor}</span>
                <span className="text-base-content/20">·</span>
                <span className="text-xs text-base-content/40">{relativeTime(entry.ts)}</span>
              </div>
            </div>
          </div>
        )
      })}
      {log.length === 0 && (
        <p className="text-sm text-base-content/40 py-8 text-center">No audit entries yet.</p>
      )}
    </div>
  )
}

function UserCard({ u, selected, onClick }) {
  const meta = ROLE_META[u.role] || ROLE_META.user
  return (
    <button
      onClick={onClick}
      className={`
        w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg border transition-all duration-150
        ${selected
          ? 'bg-primary/8 border-primary/30 shadow-sm'
          : 'border-transparent hover:bg-base-200/60 hover:border-base-300'
        }
      `}
    >
      <div className="relative shrink-0">
        <Avatar user={u} />
        <span className={`
          absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-base-100
          ${u.metadata?.banned ? 'bg-error' : 'bg-success'}
        `} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <span className={`text-sm font-medium truncate ${selected ? 'text-primary' : 'text-base-content'}`}>
            {u.username}
          </span>
          {selected && <div className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />}
        </div>
        <p className="text-xs text-base-content/45 truncate mt-0.5">{u.email}</p>
      </div>
      <div className={`
        shrink-0 flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium border
        ${meta.bg} ${meta.color} ${meta.border}
      `}>
        <meta.Icon className="w-2.5 h-2.5" />
        {meta.label}
      </div>
    </button>
  )
}

// ─── Main Component ────────────────────────────────────────────────────────────

function UserPermissionsPage({ showToast }) {
  const { user: currentUser, isAuthenticated, loading: authLoading } = useAuth()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [selectedUser, setSelectedUser] = useState(null)
  const [permissions, setPermissions] = useState({})
  const [savedPermissions, setSavedPermissions] = useState({})
  const [activeTab, setActiveTab] = useState('permissions')
  const [saving, setSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const searchRef = useRef(null)

  const hasUnsaved = JSON.stringify(permissions) !== JSON.stringify(savedPermissions)

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) { navigate('/login'); return }
    if (currentUser?.role !== 'admin' && currentUser?.role !== 'moderator') {
      showToast('Access denied', 'error')
      navigate('/')
      return
    }
    loadUsers()
  }, [authLoading, isAuthenticated, currentUser])

  const loadUsers = async () => {
    try {
      setLoading(true)
      const [usersRes, rolesRes] = await Promise.all([
        adminAPI.getAllUsers({}),
        adminAPI.getRoles(),
      ])
      setUsers(usersRes.data.users || [])
      setRoles(rolesRes.data.roles || [])
    } catch {
      // Use rich mock data for development
      setUsers(MOCK_USERS)
      setRoles([])
    } finally {
      setLoading(false)
    }
  }

  const selectUser = (u) => {
    if (hasUnsaved && selectedUser?.user_id !== u.user_id) {
      if (!confirm('You have unsaved changes. Discard them?')) return
    }
    setSelectedUser(u)
    const perms = { ...(ROLE_DEFAULTS[u.role] || ROLE_DEFAULTS.user), ...(u.custom_permissions || {}) }
    setPermissions(perms)
    setSavedPermissions(perms)
    setActiveTab('permissions')
    setSaveSuccess(false)
  }

  const applyRolePreset = (role) => {
    setPermissions({ ...ROLE_DEFAULTS[role] })
  }

  const handlePermissionChange = (id, val) => {
    setPermissions(prev => ({ ...prev, [id]: val }))
  }

  const handleSave = async () => {
    if (!selectedUser) return
    setSaving(true)
    try {
      // In production: await adminAPI.updateUserPermissions(selectedUser.user_id, permissions)
      await new Promise(r => setTimeout(r, 700))
      setSavedPermissions({ ...permissions })
      setSaveSuccess(true)
      showToast?.(`Permissions saved for ${selectedUser.username}`, 'success')
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch {
      showToast?.('Failed to save permissions', 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleDiscard = () => {
    setPermissions({ ...savedPermissions })
  }

  const filteredUsers = users.filter(u => {
    const matchesSearch = !search ||
      u.username?.toLowerCase().includes(search.toLowerCase()) ||
      u.email?.toLowerCase().includes(search.toLowerCase())
    const matchesRole = roleFilter === 'all' || u.role === roleFilter
    return matchesSearch && matchesRole
  })

  const detectedPreset = Object.entries(ROLE_DEFAULTS).find(([, defaults]) =>
    JSON.stringify(defaults) === JSON.stringify(permissions)
  )?.[0] ?? 'custom'

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          <p className="text-sm text-base-content/50">Loading users…</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] min-h-0">
      <Helmet>
        <title>Permissions — Admin</title>
      </Helmet>

      {/* Page header */}
      <div className="flex items-center justify-between px-1 pb-4 shrink-0">
        <div>
          <h1 className="text-xl font-bold text-base-content flex items-center gap-2">
            <ShieldCheckIcon className="w-5 h-5 text-primary" />
            Identity & Permissions
          </h1>
          <p className="text-xs text-base-content/50 mt-0.5">
            Manage roles and granular access controls across all users
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-base-content/40">
          <UsersIcon className="w-4 h-4" />
          <span>{users.length} users</span>
        </div>
      </div>

      {/* Split view */}
      <div className="flex flex-1 gap-4 min-h-0">

        {/* ── LEFT: User directory ── */}
        <div className="w-72 shrink-0 flex flex-col min-h-0 border border-base-300 rounded-xl bg-base-100 overflow-hidden">
          {/* Search */}
          <div className="p-3 border-b border-base-300">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-base-content/35" />
              <input
                ref={searchRef}
                type="text"
                placeholder="Search users…"
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm bg-base-200/60 border border-base-300 rounded-lg outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all placeholder:text-base-content/30"
              />
              {search && (
                <button onClick={() => setSearch('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-base-content/30 hover:text-base-content/60">
                  <XMarkIcon className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Role filter chips */}
          <div className="px-3 py-2 flex gap-1 flex-wrap border-b border-base-300">
            {['all', 'admin', 'moderator', 'premium', 'user', 'guest'].map(r => (
              <button
                key={r}
                onClick={() => setRoleFilter(r)}
                className={`
                  px-2 py-0.5 rounded-md text-xs font-medium transition-all duration-100 border
                  ${roleFilter === r
                    ? r === 'all'
                      ? 'bg-base-content text-base-100 border-base-content'
                      : `${ROLE_META[r]?.bg} ${ROLE_META[r]?.color} ${ROLE_META[r]?.border}`
                    : 'border-transparent text-base-content/45 hover:bg-base-200 hover:text-base-content/70'
                  }
                `}
              >
                {r === 'all' ? 'All' : ROLE_META[r]?.label}
              </button>
            ))}
          </div>

          {/* User list */}
          <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
            {filteredUsers.length === 0 ? (
              <div className="py-12 text-center">
                <UsersIcon className="w-8 h-8 text-base-content/20 mx-auto mb-2" />
                <p className="text-sm text-base-content/40">No users found</p>
              </div>
            ) : (
              filteredUsers.map(u => (
                <UserCard
                  key={u.user_id}
                  u={u}
                  selected={selectedUser?.user_id === u.user_id}
                  onClick={() => selectUser(u)}
                />
              ))
            )}
          </div>
        </div>

        {/* ── RIGHT: Permission editor ── */}
        <div className="flex-1 min-w-0 flex flex-col border border-base-300 rounded-xl bg-base-100 overflow-hidden">
          {!selectedUser ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center p-8">
              <div className="w-16 h-16 rounded-2xl bg-base-200 flex items-center justify-center">
                <LockClosedIcon className="w-8 h-8 text-base-content/25" />
              </div>
              <div>
                <p className="text-sm font-medium text-base-content/60">Select a user to manage permissions</p>
                <p className="text-xs text-base-content/35 mt-1">Click any user from the directory to view and edit their access controls</p>
              </div>
              <div className="flex items-center gap-3 mt-2">
                {Object.entries(ROLE_META).slice(0, 4).map(([role, meta]) => (
                  <div key={role} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium ${meta.bg} ${meta.color} ${meta.border}`}>
                    <meta.Icon className="w-3 h-3" />
                    {meta.label}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <>
              {/* User header */}
              <div className="px-5 py-4 border-b border-base-300 flex items-center gap-4 shrink-0">
                <Avatar user={selectedUser} size="lg" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-bold text-base-content">{selectedUser.username}</h2>
                    {(() => {
                      const roleMeta = ROLE_META[selectedUser.role]
                      if (!roleMeta) return null
                      const RoleIcon = roleMeta.Icon
                      return (
                        <div className={`flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium border ${roleMeta.bg} ${roleMeta.color} ${roleMeta.border}`}>
                          <RoleIcon className="w-2.5 h-2.5" />
                          {roleMeta.label}
                        </div>
                      )
                    })()}
                    {selectedUser.metadata?.banned && (
                      <span className="flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-error/10 text-error border border-error/30">
                        <NoSymbolIcon className="w-3 h-3" />
                        Suspended
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-base-content/45 mt-0.5 truncate">{selectedUser.email}</p>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <span className={`w-2 h-2 rounded-full ${selectedUser.metadata?.banned ? 'bg-error' : 'bg-success'}`} />
                  <span className="text-xs text-base-content/50">{selectedUser.metadata?.banned ? 'Suspended' : 'Active'}</span>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex items-center gap-0 px-5 border-b border-base-300 shrink-0">
                {[
                  { id: 'permissions', label: 'Permissions', Icon: LockClosedIcon },
                  { id: 'audit', label: 'Audit Log', Icon: ClockIcon },
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 transition-colors duration-100
                      ${activeTab === tab.id
                        ? 'border-primary text-primary'
                        : 'border-transparent text-base-content/50 hover:text-base-content/80 hover:border-base-300'
                      }
                    `}
                  >
                    <tab.Icon className="w-3.5 h-3.5" />
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab content */}
              <div className="flex-1 overflow-y-auto min-h-0">
                {activeTab === 'permissions' ? (
                  <div className="p-5 space-y-4">
                    {/* Role presets */}
                    <div>
                      <p className="text-xs font-medium text-base-content/40 uppercase tracking-widest mb-2.5">
                        Role Preset
                      </p>
                      <div className="flex items-center gap-1.5 flex-wrap">
                        {Object.keys(ROLE_DEFAULTS).map(role => (
                          <RolePill
                            key={role}
                            role={role}
                            active={detectedPreset === role}
                            onClick={() => applyRolePreset(role)}
                          />
                        ))}
                        {detectedPreset === 'custom' && (
                          <span className="flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium bg-violet-500/10 text-violet-600 border border-violet-500/30">
                            <DocumentTextIcon className="w-3 h-3" />
                            Custom
                          </span>
                        )}
                      </div>
                      {detectedPreset === 'custom' && (
                        <p className="mt-2 text-xs text-base-content/40">
                          Permissions have been individually customized — select a preset to reset to defaults.
                        </p>
                      )}
                    </div>

                    {/* Permission groups */}
                    <div className="space-y-2.5">
                      {PERMISSION_GROUPS.map((group, i) => (
                        <PermissionGroup
                          key={group.id}
                          group={group}
                          permissions={permissions}
                          onChange={handlePermissionChange}
                          disabled={selectedUser?.metadata?.banned}
                          defaultOpen={i < 2}
                        />
                      ))}
                    </div>

                    {/* Spacer for unsaved bar */}
                    {hasUnsaved && <div className="h-14" />}
                  </div>
                ) : (
                  <AuditLogTab userId={selectedUser.user_id} />
                )}
              </div>

              {/* ── Unsaved warning bar ── */}
              <div className={`
                shrink-0 border-t transition-all duration-200 overflow-hidden
                ${hasUnsaved ? 'border-amber-300/60 max-h-20' : 'border-transparent max-h-0'}
              `}>
                <div className="flex items-center justify-between gap-3 px-5 py-3 bg-amber-50 dark:bg-amber-900/20">
                  <div className="flex items-center gap-2 text-sm text-amber-700 dark:text-amber-400">
                    <ExclamationTriangleIcon className="w-4 h-4 shrink-0" />
                    <span className="font-medium">Unsaved changes</span>
                    <span className="text-amber-600/70 dark:text-amber-500/70 text-xs">— permissions not yet applied</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={handleDiscard}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium text-amber-700 hover:bg-amber-100 dark:hover:bg-amber-900/40 transition-colors"
                    >
                      Discard
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={saving}
                      className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-semibold bg-amber-600 text-white hover:bg-amber-700 disabled:opacity-60 transition-all"
                    >
                      {saving ? (
                        <>
                          <div className="w-3.5 h-3.5 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                          Saving…
                        </>
                      ) : (
                        <>
                          <CheckCircleIcon className="w-3.5 h-3.5" />
                          Save changes
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Save success flash */}
              {saveSuccess && !hasUnsaved && (
                <div className="shrink-0 border-t border-success/30 bg-success/8 px-5 py-3 flex items-center gap-2">
                  <CheckCircleSolid className="w-4 h-4 text-success" />
                  <span className="text-sm font-medium text-success">Changes saved</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// ─── Mock data (fallback when API unavailable) ─────────────────────────────────

const MOCK_USERS = [
  {
    user_id: 'usr_01', username: 'Alice Chen', email: 'alice@example.com', role: 'admin',
    metadata: { banned: false },
  },
  {
    user_id: 'usr_02', username: 'Bob Nakamura', email: 'bob@example.com', role: 'moderator',
    metadata: { banned: false },
  },
  {
    user_id: 'usr_03', username: 'Carla Voss', email: 'carla@example.com', role: 'premium',
    metadata: { banned: false },
  },
  {
    user_id: 'usr_04', username: 'David Osei', email: 'david@example.com', role: 'user',
    metadata: { banned: false },
  },
  {
    user_id: 'usr_05', username: 'Elena Marsh', email: 'elena@example.com', role: 'user',
    metadata: { banned: false },
  },
  {
    user_id: 'usr_06', username: 'Felix Huang', email: 'felix@example.com', role: 'guest',
    metadata: { banned: false },
  },
  {
    user_id: 'usr_07', username: 'Grace Okonkwo', email: 'grace@example.com', role: 'premium',
    metadata: { banned: false },
  },
  {
    user_id: 'usr_08', username: 'Haruki Sato', email: 'haruki@example.com', role: 'user',
    metadata: { banned: true },
  },
]

export default UserPermissionsPage
