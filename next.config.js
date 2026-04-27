/** @type {import('next').NextConfig} */
const path = require('path')

// Load .env so NEXT_PUBLIC_* values are available during build/dev.
require('dotenv').config({ path: path.resolve(__dirname, '.env') })

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    if (process.env.NODE_ENV === 'production') {
      // Vercel routes /api/* to Flask via vercel.json. Nothing else to do.
      return []
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
