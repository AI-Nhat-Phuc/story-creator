'use client'

import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import Dashboard from './Dashboard'

/**
 * Tiny auth gate for the homepage. Receives the server-rendered Discovery
 * section as `children`. Only swaps to Dashboard once auth has settled and
 * the user is confirmed as admin — otherwise it just re-renders the
 * already-server-rendered Discovery, so non-admin users never trigger any
 * client-side fetch or layout shift.
 */
function HomeAuthGate({ children }) {
  const { user, loading } = useAuth()

  if (!loading && user?.role === 'admin') {
    return <Dashboard />
  }

  return children
}

export default HomeAuthGate
