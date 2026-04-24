'use client'

import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import Dashboard from './Dashboard'
import DiscoveryContainer from '../containers/DiscoveryContainer'

function HomePage({ initialStories = [], initialWorlds = [] }) {
  const { user, loading } = useAuth()

  // Admins get the Dashboard, but only after auth settles. Until then (and for
  // all non-admin users) we render DiscoveryContainer, which lets SSR paint the
  // server-fetched stories/worlds immediately instead of a loading spinner.
  if (!loading && user?.role === 'admin') {
    return <Dashboard />
  }

  return <DiscoveryContainer initialStories={initialStories} initialWorlds={initialWorlds} />
}

export default HomePage
