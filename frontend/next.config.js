/** @type {import('next').NextConfig} */
const path = require('path')

// Load root .env so NEXT_PUBLIC_* values are available during build/dev,
// matching the Vite setup that used envDir: '../'.
require('dotenv').config({ path: path.resolve(__dirname, '../.env') })

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    if (process.env.NODE_ENV === 'production') {
      // @vercel/next is registered with `src: "frontend/package.json"`, so
      // its routes (and everything that hands off to Next.js) live under
      // /frontend/...  vercel.json catch-all rewrites every user URL into
      // that namespace; we strip the prefix here so the App Router matches
      // pages at the URLs the user actually visited.
      //
      // beforeFiles is critical: with afterFiles, Next.js checks the route
      // tree first and 404s on /frontend/worlds/[id] before the rewrite
      // ever runs (no app/frontend/* routes exist).
      return {
        beforeFiles: [
          { source: '/frontend', destination: '/' },
          { source: '/frontend/:path*', destination: '/:path*' },
        ],
      }
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
