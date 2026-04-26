'use client'

import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from '../utils/router-compat'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import { invitationsAPI } from '../services/api'
import ThemeSelector from './ThemeSelector'
import InvitationsDropdown from './InvitationsDropdown'
import Modal from './Modal'
import {
  BookOpenIcon,
  ShieldCheckIcon,
  StarIcon,
  UserIcon,
  Bars3Icon,
  SwatchIcon,
} from '@heroicons/react/24/solid'

function Navbar() {
  const { t } = useTranslation()
  const { user, isAuthenticated, loading: authLoading, logout } = useAuth()
  const navigate = useNavigate()
  const [showLogoutModal, setShowLogoutModal] = useState(false)
  const [invitations, setInvitations] = useState([])

  useEffect(() => {
    if (!isAuthenticated) return
    invitationsAPI.list().then(res => setInvitations(res.data || [])).catch(() => {})
  }, [isAuthenticated])

  const handleInvitationAction = (action) => async (id) => {
    try {
      await action(id)
      setInvitations(prev => prev.filter(i => i.invitation_id !== id))
    } catch {
      // silent — user can retry
    }
  }

  const handleAcceptInvitation = handleInvitationAction(invitationsAPI.accept)
  const handleDeclineInvitation = handleInvitationAction(invitationsAPI.decline)

  const handleLogoutClick = () => {
    setShowLogoutModal(true)
  }

  const confirmLogout = () => {
    logout()
    setShowLogoutModal(false)
    // Giữ nguyên trang hiện tại, không redirect
  }

  const cancelLogout = () => {
    setShowLogoutModal(false)
  }

  const navLinks = (
    <>
      <li>
        <Link to="/">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          {user?.role === 'admin' ? t('nav.dashboard') : t('nav.home')}
        </Link>
      </li>
      <li>
        <Link to="/worlds">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {t('nav.worlds')}
        </Link>
      </li>
      <li>
        <Link to="/stories">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          {t('nav.stories')}
        </Link>
      </li>
      {isAuthenticated && (user?.role === 'admin' || user?.role === 'moderator') && (
        <li>
          <Link to="/admin">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            {t('nav.admin')}
          </Link>
        </li>
      )}
    </>
  )

  return (
    <div className="bg-primary shadow-lg text-primary-content navbar">
      <div className="flex-1">
        <Link to="/" className="text-xl normal-case btn btn-ghost">
          <BookOpenIcon className="inline w-5 h-5" /> Story Creator
        </Link>
      </div>

      {/* Desktop nav links */}
      <div className="hidden md:flex flex-none">
        <ul className="px-1 menu menu-horizontal">
          {navLinks}
        </ul>

        {/* Theme selector - desktop */}
        <div className="dropdown dropdown-end ml-1">
          <label tabIndex={0} className="btn btn-ghost btn-circle">
            <SwatchIcon className="w-5 h-5" />
          </label>
          <div tabIndex={0} className="dropdown-content bg-base-100 shadow rounded-box z-50 mt-3 w-64 text-base-content">
            <ThemeSelector />
          </div>
        </div>

        {/* Invitations bell - desktop */}
        {isAuthenticated && (
          <InvitationsDropdown
            invitations={invitations}
            onAccept={handleAcceptInvitation}
            onDecline={handleDeclineInvitation}
          />
        )}

        {/* User menu - desktop */}
        {authLoading ? (
          <div className="ml-2 btn btn-ghost btn-circle">
            <span className="loading loading-spinner loading-sm"></span>
          </div>
        ) : isAuthenticated ? (
          <div className="ml-2 dropdown dropdown-end">
            <label tabIndex={0} className="btn btn-ghost btn-circle avatar placeholder">
              <div className="bg-neutral-focus rounded-full w-10 text-neutral-content">
                <span className="text-xl">{user?.username?.[0]?.toUpperCase() || 'U'}</span>
              </div>
            </label>
            <ul tabIndex={0} className="bg-base-100 shadow mt-3 p-2 rounded-box w-52 text-base-content menu menu-compact dropdown-content">
              <li className="menu-title">
                <span>{user?.username}</span>
              </li>
              {user?.role && (
                <li className="menu-title">
                  <span className="flex items-center gap-1">
                    {user.role === 'admin' && <ShieldCheckIcon className="inline w-4 h-4" />}
                    {user.role === 'moderator' && <ShieldCheckIcon className="inline w-4 h-4" />}
                    {user.role === 'premium' && <StarIcon className="inline w-4 h-4" />}
                    {user.role === 'user' && <UserIcon className="inline w-4 h-4" />}
                    <span className="capitalize">{user.role}</span>
                  </span>
                </li>
              )}
              <li><a onClick={handleLogoutClick}>{t('actions.logout')}</a></li>
            </ul>
          </div>
        ) : (
          <Link to="/login" className="ml-2 btn btn-ghost">
            {t('nav.login')}
          </Link>
        )}
      </div>

      {/* Mobile: hamburger dropdown */}
      <div className="flex md:hidden flex-none">
        {authLoading ? (
          <div className="btn btn-ghost btn-circle">
            <span className="loading loading-spinner loading-sm"></span>
          </div>
        ) : (
          <div className="dropdown dropdown-end">
            <label tabIndex={0} className="btn btn-ghost btn-circle">
              <Bars3Icon className="w-6 h-6" />
            </label>
            <ul tabIndex={0} className="bg-base-100 shadow mt-3 p-2 rounded-box w-56 text-base-content menu dropdown-content z-50">
              {navLinks}
              <div className="divider my-1"></div>
              <div className="px-1 pb-1">
                <ThemeSelector />
              </div>
              <div className="divider my-1"></div>
              {isAuthenticated ? (
                <>
                  <li className="menu-title px-4 py-1">
                    <span className="flex items-center gap-1">
                      {user?.role === 'admin' && <ShieldCheckIcon className="inline w-4 h-4" />}
                      {user?.role === 'premium' && <StarIcon className="inline w-4 h-4" />}
                      {(!user?.role || user?.role === 'user') && <UserIcon className="inline w-4 h-4" />}
                      {user?.username}
                    </span>
                  </li>
                  <li><a onClick={handleLogoutClick}>{t('actions.logout')}</a></li>
                </>
              ) : (
                <li><Link to="/login">{t('nav.login')}</Link></li>
              )}
            </ul>
          </div>
        )}
      </div>

      {/* Logout Confirmation Modal */}
      <Modal open={showLogoutModal} onClose={cancelLogout} title={t('nav.logoutConfirmTitle')} className="max-w-sm">
        <p className="text-sm opacity-80 mb-6">{t('nav.logoutConfirmMsg')}</p>
        <div className="flex justify-end gap-2">
          <button className="btn btn-ghost btn-sm" onClick={cancelLogout}>
            {t('common.cancel')}
          </button>
          <button className="btn btn-error btn-sm" onClick={confirmLogout}>
            {t('actions.logout')}
          </button>
        </div>
      </Modal>
    </div>
  )
}

export default Navbar
