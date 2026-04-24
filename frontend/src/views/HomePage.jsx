'use client'

import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import Dashboard from './Dashboard'
import DiscoveryContainer from '../containers/DiscoveryContainer'

function HomePage({ initialStories = [], initialWorlds = [] }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  if (user?.role === 'admin') {
    return <Dashboard />
  }

  return <DiscoveryContainer initialStories={initialStories} initialWorlds={initialWorlds} />
}

export default HomePage
