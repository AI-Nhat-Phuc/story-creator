import React from 'react'
import {
  ShieldCheckIcon,
  StarIcon,
  UserIcon,
  EyeIcon,
} from '@heroicons/react/24/solid'

/**
 * RoleBadge component - Display user role with icon and color
 *
 * Props:
 *   - role: string - User role (admin, moderator, premium, user, guest)
 *   - size: string - Badge size (xs, sm, md, lg) - default: md
 */
function RoleBadge({ role = 'user', size = 'md' }) {
  const getRoleInfo = (role) => {
    const roleMap = {
      admin: {
        label: 'Quản trị viên',
        icon: <ShieldCheckIcon className="w-3.5 h-3.5" />,
        badgeColor: 'badge-error',
      },
      moderator: {
        label: 'Kiểm duyệt viên',
        icon: <ShieldCheckIcon className="w-3.5 h-3.5" />,
        badgeColor: 'badge-warning',
      },
      premium: {
        label: 'Premium',
        icon: <StarIcon className="w-3.5 h-3.5" />,
        badgeColor: 'badge-primary',
      },
      user: {
        label: 'Người dùng',
        icon: <UserIcon className="w-3.5 h-3.5" />,
        badgeColor: 'badge-info',
      },
      guest: {
        label: 'Khách',
        icon: <EyeIcon className="w-3.5 h-3.5" />,
        badgeColor: 'badge-ghost',
      }
    }

    return roleMap[role] || roleMap.user
  }

  const info = getRoleInfo(role)
  const sizeClass = size ? `badge-${size}` : ''

  return (
    <span className={`badge ${info.badgeColor} ${sizeClass} gap-1`}>
      <span>{info.icon}</span>
      <span>{info.label}</span>
    </span>
  )
}

export default RoleBadge
