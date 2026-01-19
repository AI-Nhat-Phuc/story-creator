import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { statsAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

function Dashboard({ showToast }) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

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
        <h1 className="font-bold text-3xl">📊 Dashboard</h1>
        <button onClick={loadStats} className="btn btn-circle btn-ghost">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <div className="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
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

        <Link to="/characters" className="bg-base-100 hover:bg-accent/10 shadow rounded-box transition cursor-pointer stat">
          <div className="text-accent stat-figure">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div className="stat-title">Nhân vật</div>
          <div className="text-accent stat-value">{stats?.total_entities || 0}</div>
          <div className="stat-desc">Tổng số nhân vật</div>
        </Link>

        <Link to="/locations" className="bg-base-100 hover:bg-info/10 shadow rounded-box transition cursor-pointer stat">
          <div className="text-info stat-figure">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div className="stat-title">Địa điểm</div>
          <div className="text-info stat-value">{stats?.total_locations || 0}</div>
          <div className="stat-desc">Tổng số địa điểm</div>
        </Link>
      </div>

      {stats && (
        <div className="bg-base-100 shadow mt-8 p-6 rounded-box">
          <h2 className="mb-4 font-bold text-2xl">📈 Thông tin chi tiết</h2>
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
                <tr>
                  <td className="font-semibold">Câu chuyện được liên kết</td>
                  <td>{stats.linked_stories || 0}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
