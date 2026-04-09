import { useState, useEffect, lazy, Suspense } from 'react'
import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'
import { statsAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import RoleBadge from '../components/RoleBadge'
import Tag from '../components/Tag'
import {
  ChartBarIcon,
  LockClosedIcon,
  GlobeAltIcon,
  ChartPieIcon,
} from '@heroicons/react/24/outline'

// Lazy-load heavy @xyflow/react bundle — only fetched when timeline is rendered
const EventTimelineSection = lazy(() => import('../components/timeline/EventTimelineSection'))
function Dashboard({ showToast }) {
  const { t } = useTranslation()
  const { isAuthenticated, user, loading: authLoading } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  // Wait for auth to settle before loading stats, then reload if auth state changes.
  // The !authLoading guard prevents a double-fetch when auth resolves.
  useEffect(() => {
    if (!authLoading) {
      loadStats()
    }
  }, [authLoading, isAuthenticated]) // Reload khi login/logout

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

  const helmet = (
    <Helmet>
      <title>{t('meta.dashboard.title')}</title>
      <meta name="description" content={t('meta.dashboard.description')} />
    </Helmet>
  )

  if (loading) return <>{helmet}<LoadingSpinner /></>

  if (!stats) {
    return (
      <>
        {helmet}
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <p className="mb-4 text-xl">{t('pages.dashboard.noStats')}</p>
            <button onClick={loadStats} className="btn btn-primary">{t('actions.refresh')}</button>
          </div>
        </div>
      </>
    )
  }

  return (
    <div>
      {helmet}
      <div className="flex justify-between items-center mb-4 md:mb-6">
        <h1 className="font-bold text-2xl md:text-3xl"><ChartBarIcon className="inline w-7 h-7 md:w-8 md:h-8" /> {t('pages.dashboard.title')}</h1>
        <button onClick={loadStats} className="btn btn-circle btn-ghost btn-sm md:btn-md">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      {!isAuthenticated && (
        <div className="mb-4 md:mb-6 alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current w-6 h-6 shrink-0" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <h3 className="font-bold">{t('pages.dashboard.publicNote')}</h3>
            <div className="text-sm">
              <Link to="/login" className="link">{t('actions.login')}</Link> {t('pages.dashboard.publicNoteDetail')}
            </div>
          </div>
        </div>
      )}

      <div className="gap-3 md:gap-4 grid grid-cols-1 md:grid-cols-2">
        <Link to="/worlds" className="bg-base-100 hover:bg-primary/10 shadow rounded-box transition cursor-pointer stat">
          <div className="text-primary stat-figure">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="stat-title">{t('pages.dashboard.totalWorlds')}</div>
          <div className="text-primary stat-value">{stats?.total_worlds || 0}</div>
          <div className="stat-desc">{t('pages.dashboard.totalWorldsDesc')}</div>
        </Link>

        <Link to="/stories" className="group bg-base-100 hover:bg-secondary/10 shadow rounded-box transition cursor-pointer stat">
          <div className="text-secondary stat-figure">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div className="stat-title">{t('pages.dashboard.totalStories')}</div>
          <div className="text-secondary group-hover:text-secondary-content transition-colors stat-value">{stats?.total_stories || 0}</div>
          <div className="stat-desc">{t('pages.dashboard.totalStoriesDesc')}</div>
        </Link>
      </div>

      {stats?.breakdown && (
        <div className="bg-base-100 shadow mt-4 md:mt-8 p-4 md:p-6 rounded-box">
          <h2 className="mb-4 font-bold text-xl md:text-2xl">
            {isAuthenticated
              ? <><LockClosedIcon className="inline w-5 h-5" /> {t('pages.dashboard.breakdown')}</>
              : <><GlobeAltIcon className="inline w-5 h-5" /> {t('pages.dashboard.publicBreakdown')}</>}
          </h2>

          <div className="gap-4 md:gap-6 grid grid-cols-1 md:grid-cols-2">
            <div className="bg-base-200 p-4 rounded-lg">
              <h3 className="mb-3 font-semibold text-lg">{t('pages.dashboard.totalWorlds')}</h3>
              <div className="space-y-2">
                {isAuthenticated && stats.breakdown.worlds.private !== undefined && (
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <Tag color="primary" size="sm">{t('common.private')}</Tag>
                      <span className="text-sm">{t('common.yours')}</span>
                    </span>
                    <span className="font-bold">{stats.breakdown.worlds.private}</span>
                  </div>
                )}
                {isAuthenticated && stats.breakdown.worlds.shared !== undefined && (
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <Tag color="info" size="sm">{t('common.shared')}</Tag>
                      <span className="text-sm">{t('common.fromOthers')}</span>
                    </span>
                    <span className="font-bold">{stats.breakdown.worlds.shared}</span>
                  </div>
                )}
                <div className="flex justify-between items-center">
                  <span className="flex items-center gap-2">
                    <Tag color="success" size="sm">{t('common.public')}</Tag>
                    <span className="text-sm">{t('common.everyoneSee')}</span>
                  </span>
                  <span className="font-bold">{stats.breakdown.worlds.public}</span>
                </div>
              </div>
            </div>

            <div className="bg-base-200 p-4 rounded-lg">
              <h3 className="mb-3 font-semibold text-lg">{t('pages.dashboard.totalStories')}</h3>
              <div className="space-y-2">
                {isAuthenticated && stats.breakdown.stories.private !== undefined && (
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <Tag color="primary" size="sm">{t('common.private')}</Tag>
                      <span className="text-sm">{t('common.yours')}</span>
                    </span>
                    <span className="font-bold">{stats.breakdown.stories.private}</span>
                  </div>
                )}
                {isAuthenticated && stats.breakdown.stories.shared !== undefined && (
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <Tag color="info" size="sm">{t('common.shared')}</Tag>
                      <span className="text-sm">{t('common.fromOthers')}</span>
                    </span>
                    <span className="font-bold">{stats.breakdown.stories.shared}</span>
                  </div>
                )}
                <div className="flex justify-between items-center">
                  <span className="flex items-center gap-2">
                    <Tag color="success" size="sm">{t('common.public')}</Tag>
                    <span className="text-sm">{t('common.everyoneSee')}</span>
                  </span>
                  <span className="font-bold">{stats.breakdown.stories.public}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {isAuthenticated && stats?.user_quota && (
        <div className="bg-base-100 shadow mt-4 md:mt-6 p-4 md:p-6 rounded-box">
          <h2 className="mb-4 font-bold text-xl md:text-2xl"><ChartPieIcon className="inline w-6 h-6" /> {t('pages.dashboard.quota')}</h2>
          <div className="gap-4 md:gap-6 grid grid-cols-1 md:grid-cols-2">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold">{t('pages.dashboard.publicWorlds')}</span>
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
                {t('pages.dashboard.slotsRemaining', { count: stats.user_quota.worlds.limit - stats.user_quota.worlds.current })}
              </p>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold">{t('pages.dashboard.publicStories')}</span>
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
                {t('pages.dashboard.slotsRemaining', { count: stats.user_quota.stories.limit - stats.user_quota.stories.current })}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Event Timeline Section - Only show if there are worlds (lazy-loaded) */}
      {stats?.total_worlds > 0 && (
        <Suspense fallback={<LoadingSpinner />}>
          <EventTimelineSection
            showToast={showToast}
            worldsList={stats?.worlds_summary || []}
          />
        </Suspense>
      )}
    </div>
  )
}

export default Dashboard
