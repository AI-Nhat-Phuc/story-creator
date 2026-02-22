import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { statsAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import RoleBadge from '../components/RoleBadge'
import EventTimelineSection from '../components/timeline/EventTimelineSection'
import {
  ChartBarIcon,
  LockClosedIcon,
  GlobeAltIcon,
  ChartPieIcon,
  ChartBarSquareIcon,
} from '@heroicons/react/24/outline'

function Dashboard({ showToast }) {
  const { isAuthenticated, user } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [isAuthenticated]) // Reload khi login/logout

  const loadStats = async () => {
    try {
      setLoading(true)
      const response = await statsAPI.get()
      console.log('[DEBUG] Stats response:', response.data)
      setStats(response.data)
    } catch (error) {
      showToast('Không thể tải thống kê', 'error')
      console.error('Error loading stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingSpinner />

  if (!stats) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <p className="mb-4 text-xl">Không có dữ liệu thống kê</p>
          <button onClick={loadStats} className="btn btn-primary">Tải lại</button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="font-bold text-3xl"><ChartBarIcon className="inline w-8 h-8" /> Dashboard</h1>
        <button onClick={loadStats} className="btn btn-circle btn-ghost">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      {/* Note for anonymous users */}
      {!isAuthenticated && (
        <div className="mb-6 alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current w-6 h-6 shrink-0" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <h3 className="font-bold">Bạn đang xem dữ liệu công khai</h3>
            <div className="text-sm">
              <Link to="/login" className="link">Đăng nhập</Link> để xem thêm nội dung riêng tư của bạn và được chia sẻ
            </div>
          </div>
        </div>
      )}

      <div className="gap-4 grid grid-cols-1 md:grid-cols-2">
        <Link to="/worlds" className="bg-base-100 hover:bg-primary/10 shadow rounded-box transition cursor-pointer stat">
          <div className="text-primary stat-figure">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="stat-title">Thế giới</div>
          <div className="text-primary stat-value">{stats?.total_worlds || 0}</div>
          <div className="stat-desc">Tổng số thế giới đã tạo</div>
        </Link>

        <Link to="/stories" className="group bg-base-100 hover:bg-secondary/10 shadow rounded-box transition cursor-pointer stat">
          <div className="text-secondary stat-figure">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div className="stat-title">Câu chuyện</div>
          <div className="text-secondary group-hover:text-secondary-content transition-colors stat-value">{stats?.total_stories || 0}</div>
          <div className="stat-desc">Tổng số câu chuyện</div>
        </Link>
      </div>

      {/* Privacy Breakdown Section */}
      {stats?.breakdown && (
        <div className="bg-base-100 shadow mt-8 p-6 rounded-box">
          <h2 className="mb-4 font-bold text-2xl">
            {isAuthenticated ? <><LockClosedIcon className="inline w-5 h-5" /> Phân loại dữ liệu</> : <><GlobeAltIcon className="inline w-5 h-5" /> Dữ liệu công khai</>}
          </h2>

          <div className="gap-6 grid grid-cols-1 md:grid-cols-2">
            {/* Worlds Breakdown */}
            <div className="bg-base-200 p-4 rounded-lg">
              <h3 className="mb-3 font-semibold text-lg">Thế giới</h3>
              <div className="space-y-2">
                {isAuthenticated && stats.breakdown.worlds.private !== undefined && (
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <span className="badge badge-primary badge-sm">Riêng tư</span>
                      <span className="text-sm">Của bạn</span>
                    </span>
                    <span className="font-bold">{stats.breakdown.worlds.private}</span>
                  </div>
                )}
                {isAuthenticated && stats.breakdown.worlds.shared !== undefined && (
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <span className="badge badge-info badge-sm">Được chia sẻ</span>
                      <span className="text-sm">Từ người khác</span>
                    </span>
                    <span className="font-bold">{stats.breakdown.worlds.shared}</span>
                  </div>
                )}
                <div className="flex justify-between items-center">
                  <span className="flex items-center gap-2">
                    <span className="badge badge-success badge-sm">Công khai</span>
                    <span className="text-sm">Mọi người xem được</span>
                  </span>
                  <span className="font-bold">{stats.breakdown.worlds.public}</span>
                </div>
              </div>
            </div>

            {/* Stories Breakdown */}
            <div className="bg-base-200 p-4 rounded-lg">
              <h3 className="mb-3 font-semibold text-lg">Câu chuyện</h3>
              <div className="space-y-2">
                {isAuthenticated && stats.breakdown.stories.private !== undefined && (
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <span className="badge badge-primary badge-sm">Riêng tư</span>
                      <span className="text-sm">Của bạn</span>
                    </span>
                    <span className="font-bold">{stats.breakdown.stories.private}</span>
                  </div>
                )}
                {isAuthenticated && stats.breakdown.stories.shared !== undefined && (
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <span className="badge badge-info badge-sm">Được chia sẻ</span>
                      <span className="text-sm">Từ người khác</span>
                    </span>
                    <span className="font-bold">{stats.breakdown.stories.shared}</span>
                  </div>
                )}
                <div className="flex justify-between items-center">
                  <span className="flex items-center gap-2">
                    <span className="badge badge-success badge-sm">Công khai</span>
                    <span className="text-sm">Mọi người xem được</span>
                  </span>
                  <span className="font-bold">{stats.breakdown.stories.public}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* User Quota Section (Only for authenticated users) */}
      {isAuthenticated && stats?.user_quota && (
        <div className="bg-base-100 shadow mt-6 p-6 rounded-box">
          <h2 className="mb-4 font-bold text-2xl"><ChartPieIcon className="inline w-6 h-6" /> Quota của bạn</h2>
          <div className="gap-6 grid grid-cols-1 md:grid-cols-2">
            {/* Worlds Quota */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold">Thế giới công khai</span>
                <span className="text-sm">
                  {stats.user_quota.worlds.current} / {stats.user_quota.worlds.limit}
                </span>
              </div>
              <progress
                className="w-full progress progress-primary"
                value={stats.user_quota.worlds.current}
                max={stats.user_quota.worlds.limit}
              ></progress>
              <p className="opacity-70 mt-1 text-xs">
                Còn {stats.user_quota.worlds.limit - stats.user_quota.worlds.current} slot
              </p>
            </div>

            {/* Stories Quota */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold">Câu chuyện công khai</span>
                <span className="text-sm">
                  {stats.user_quota.stories.current} / {stats.user_quota.stories.limit}
                </span>
              </div>
              <progress
                className="w-full progress progress-secondary"
                value={stats.user_quota.stories.current}
                max={stats.user_quota.stories.limit}
              ></progress>
              <p className="opacity-70 mt-1 text-xs">
                Còn {stats.user_quota.stories.limit - stats.user_quota.stories.current} slot
              </p>
            </div>
          </div>
        </div>
      )}

      {stats && (
        <div className="bg-base-100 shadow mt-8 p-6 rounded-box">
          <h2 className="mb-4 font-bold text-2xl"><ChartBarSquareIcon className="inline w-6 h-6" /> Thông tin hệ thống</h2>
          <div className="overflow-x-auto">
            <table className="table table-zebra w-full">
              <tbody>
                <tr>
                  <td className="font-semibold">Hệ thống lưu trữ</td>
                  <td>{stats.storage_type}</td>
                </tr>
                <tr>
                  <td className="font-semibold">Tích hợp GPT</td>
                  <td>
                    {stats.has_gpt ? (
                      <span className="badge badge-success">Đã kích hoạt</span>
                    ) : (
                      <span className="badge badge-error">Chưa kích hoạt</span>
                    )}
                  </td>
                </tr>
                {isAuthenticated && (
                  <>
                    <tr>
                      <td className="font-semibold">Tài khoản</td>
                      <td>
                        <span className="badge badge-primary">{user?.username}</span>
                      </td>
                    </tr>
                    <tr>
                      <td className="font-semibold">Vai trò</td>
                      <td>
                        <RoleBadge role={user?.role} />
                      </td>
                    </tr>
                  </>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Event Timeline Section - Only show if there are worlds */}
      {stats?.total_worlds > 0 && (
        <EventTimelineSection showToast={showToast} />
      )}
    </div>
  )
}

export default Dashboard
