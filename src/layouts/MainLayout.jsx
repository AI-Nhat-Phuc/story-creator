'use client'

import React from 'react'
import Navbar from '../components/Navbar'

function MainLayout({ children }) {
  return (
    <div className="bg-base-200 min-h-screen">
      <Navbar />
      <div className="mx-auto px-3 py-4 md:px-4 md:py-8 container">
        {children}
      </div>
    </div>
  )
}

export default MainLayout
