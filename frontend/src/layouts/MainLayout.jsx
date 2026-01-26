import React from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'

function MainLayout() {
  return (
    <div className="bg-base-200 min-h-screen">
      <Navbar />
      <div className="mx-auto px-4 py-8 container">
        <Outlet />
      </div>
    </div>
  )
}

export default MainLayout
