'use client'

import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import Dashboard from './Dashboard'
import DiscoveryContainer from '../containers/DiscoveryContainer'

function HomePage({ showToast }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  if (user?.role === 'admin') {
    return <Dashboard showToast={showToast} />
  }

  return <DiscoveryContainer showToast={showToast} />
}

export default HomePage
