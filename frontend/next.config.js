/** @type {import('next').NextConfig} */
const path = require('path')

// Load root .env so NEXT_PUBLIC_* values are available during build/dev,
// matching the Vite setup that used envDir: '../'.
require('dotenv').config({ path: path.resolve(__dirname, '../.env') })

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    if (process.env.NODE_ENV === 'production') {
      // Vercel's vercel.json catch-all prepends /frontend/ to the incoming
      // URL before it reaches this Next.js app (because @vercel/next is
      // registered at src:"frontend/package.json"). Strip that prefix so
      // app-router page matching (e.g. app/login/page.jsx) works.
      return [
        { source: '/frontend', destination: '/' },
        { source: '/frontend/:path*', destination: '/:path*' },
      ]
    }
    // Dev: proxy /api/* to Flask on :5000.
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5000/api/:path*',
      },
    ]
  },
  eslint: {
    // Next's built-in ESLint is opt-in via `next lint`; skip during `next build`.
    ignoreDuringBuilds: true,
  },
}

module.exports = nextConfig
