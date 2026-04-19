/** @type {import('next').NextConfig} */
const path = require('path')

// Load root .env so NEXT_PUBLIC_* values are available during build/dev,
// matching the Vite setup that used envDir: '../'.
require('dotenv').config({ path: path.resolve(__dirname, '../.env') })

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // Dev-only: proxy /api/* to Flask on :5000. In production Vercel's
    // vercel.json rewrite sends /api/* to api/app.py instead.
    if (process.env.NODE_ENV === 'production') return []
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
