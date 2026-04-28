'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useTranslation } from 'react-i18next'
import '../src/i18n'
import {
  BookOpenIcon,
  HomeIcon,
  ArrowPathIcon,
  WrenchScrewdriverIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline'

/* ─── Branded illustration ────────────────────────────────────────────────── */
function ServerErrorIllustration() {
  return (
    <div className="relative w-64 h-56 mx-auto select-none" aria-hidden="true">
      {/* Ghost "500" backdrop */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <span className="text-9xl font-black text-warning/8 leading-none tracking-tighter">
          500
        </span>
      </div>

      <svg
        viewBox="0 0 220 180"
        className="w-full h-full drop-shadow-sm"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* ── Server rack units ──────────────────────────────────────────── */}
        {/* Server unit 1 — OK */}
        <rect
          x="54" y="60" width="112" height="24"
          rx="5"
          className="fill-base-100 stroke-base-content/25"
          strokeWidth="1.5"
        />
        {/* Screws */}
        <circle cx="64" cy="72" r="3" className="fill-base-200 stroke-base-content/20" strokeWidth="1" />
        <circle cx="156" cy="72" r="3" className="fill-base-200 stroke-base-content/20" strokeWidth="1" />
        {/* Vents */}
        <line x1="76" y1="65" x2="76" y2="79" strokeOpacity="0.08" stroke="currentColor" strokeWidth="1.5" />
        <line x1="82" y1="65" x2="82" y2="79" strokeOpacity="0.08" stroke="currentColor" strokeWidth="1.5" />
        <line x1="88" y1="65" x2="88" y2="79" strokeOpacity="0.08" stroke="currentColor" strokeWidth="1.5" />
        {/* Status LED — green */}
        <circle cx="140" cy="72" r="4" className="fill-success" />
        <circle cx="140" cy="72" r="2" className="fill-success-content/40" />

        {/* Server unit 2 — warning */}
        <rect
          x="54" y="90" width="112" height="24"
          rx="5"
          className="fill-base-100 stroke-base-content/25"
          strokeWidth="1.5"
        />
        <circle cx="64" cy="102" r="3" className="fill-base-200 stroke-base-content/20" strokeWidth="1" />
        <circle cx="156" cy="102" r="3" className="fill-base-200 stroke-base-content/20" strokeWidth="1" />
        <line x1="76" y1="95" x2="76" y2="109" strokeOpacity="0.08" stroke="currentColor" strokeWidth="1.5" />
        <line x1="82" y1="95" x2="82" y2="109" strokeOpacity="0.08" stroke="currentColor" strokeWidth="1.5" />
        <line x1="88" y1="95" x2="88" y2="109" strokeOpacity="0.08" stroke="currentColor" strokeWidth="1.5" />
        {/* Status LED — warning, pulsing */}
        <circle cx="140" cy="102" r="4" className="fill-warning animate-pulse" />
        <circle cx="140" cy="102" r="2" className="fill-warning-content/30" />

        {/* Server unit 3 — error */}
        <rect
          x="54" y="120" width="112" height="24"
          rx="5"
          className="fill-base-100 stroke-base-content/25"
          strokeWidth="1.5"
        />
        <circle cx="64" cy="132" r="3" className="fill-base-200 stroke-base-content/20" strokeWidth="1" />
        <circle cx="156" cy="132" r="3" className="fill-base-200 stroke-base-content/20" strokeWidth="1" />
        <line x1="76" y1="125" x2="76" y2="139" strokeOpacity="0.08" stroke="currentColor" strokeWidth="1.5" />
        <line x1="82" y1="125" x2="82" y2="139" strokeOpacity="0.08" stroke="currentColor" strokeWidth="1.5" />
        <line x1="88" y1="125" x2="88" y2="139" strokeOpacity="0.08" stroke="currentColor" strokeWidth="1.5" />
        {/* Status LED — error, pulsing */}
        <circle
          cx="140" cy="132" r="4"
          className="fill-error animate-pulse"
          style={{ animationDelay: '0.3s' }}
        />
        <circle cx="140" cy="132" r="2" className="fill-error-content/30" />

        {/* ── Lightning bolt (floating above server) ──────────────────── */}
        <g className="animate-float" style={{ transformOrigin: '110px 36px' }}>
          <path
            d="M116 12 L106 36 L114 36 L104 60 L124 28 L116 28 Z"
            className="fill-warning stroke-warning/60"
            strokeWidth="1"
            strokeLinejoin="round"
          />
        </g>

        {/* ── Spark particles ──────────────────────────────────────────── */}
        <circle
          cx="152" cy="44" r="3"
          className="fill-warning/50 animate-ping"
          style={{ animationDuration: '1.6s' }}
        />
        <circle
          cx="68" cy="54" r="2.5"
          className="fill-accent/40 animate-ping"
          style={{ animationDuration: '2.1s', animationDelay: '0.4s' }}
        />
        <circle
          cx="162" cy="80" r="2"
          className="fill-warning/35 animate-ping"
          style={{ animationDuration: '1.9s', animationDelay: '0.7s' }}
        />
        <circle
          cx="50" cy="96" r="2"
          className="fill-error/30 animate-ping"
          style={{ animationDuration: '2.4s', animationDelay: '1s' }}
        />
      </svg>
    </div>
  )
}

/* ─── Page ─────────────────────────────────────────────────────────────────── */
export default function ErrorPage({ error, reset }) {
  const { t } = useTranslation()
  const [isRetrying, setIsRetrying] = useState(false)

  useEffect(() => {
    // Forward to any error monitoring service here
    console.error('[Story Creator] Runtime error:', error)
  }, [error])

  const handleRetry = async () => {
    setIsRetrying(true)
    await new Promise((r) => setTimeout(r, 700))
    reset()
    setIsRetrying(false)
  }

  return (
    <div className="flex flex-col min-h-screen bg-base-200">
      {/* Minimal branded header */}
      <header className="bg-primary text-primary-content px-5 py-3 flex items-center gap-2 shadow-md">
        <BookOpenIcon className="w-5 h-5 flex-shrink-0" />
        <span className="font-bold text-base tracking-wide">Story Creator</span>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-12 text-center">
        <div className="w-full max-w-md space-y-8">

          {/* Illustration */}
          <div className="animate-fade-in-up">
            <ServerErrorIllustration />
          </div>

          {/* Heading + description */}
          <div className="space-y-3 animate-fade-in-up animation-delay-100">
            {/* Status badge */}
            <div className="flex justify-center">
              <span className="badge badge-warning badge-outline gap-1.5 py-3">
                <WrenchScrewdriverIcon className="w-3.5 h-3.5" />
                {t('errors.serverError.badge')}
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-base-content">
              {t('errors.serverError.title')}
            </h1>
            <p className="text-base-content/60 leading-relaxed max-w-xs mx-auto text-sm md:text-base">
              {t('errors.serverError.description')}
            </p>
          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center animate-fade-in-up animation-delay-200">
            <button
              onClick={handleRetry}
              disabled={isRetrying}
              className="btn btn-primary gap-2 shadow-sm hover:shadow-md transition-shadow disabled:opacity-70"
            >
              {isRetrying ? (
                <>
                  <span className="loading loading-spinner loading-sm" />
                  {t('errors.serverError.retrying')}
                </>
              ) : (
                <>
                  <ArrowPathIcon className="w-4 h-4" />
                  {t('errors.serverError.retry')}
                </>
              )}
            </button>
            <Link
              href="/"
              className="btn btn-ghost gap-2 hover:bg-base-300 transition-colors"
            >
              <HomeIcon className="w-4 h-4" />
              {t('errors.serverError.goHome')}
            </Link>
          </div>

          {/* Reassurance card */}
          <div className="card bg-base-100 shadow-sm animate-fade-in-up animation-delay-300">
            <div className="card-body py-5 px-6">
              {/* Data safety note */}
              <div className="flex items-start gap-3 text-left">
                <div className="mt-0.5 flex-shrink-0">
                  <ShieldCheckIcon className="w-5 h-5 text-success" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-base-content">
                    {t('errors.serverError.dataNote')}
                  </p>
                  <p className="text-xs text-base-content/60 mt-1 leading-relaxed">
                    {t('errors.serverError.dataDescription')}
                  </p>
                </div>
              </div>

              <div className="divider my-2" />

              {/* What to do next */}
              <ul className="space-y-2 text-left">
                <li className="flex items-start gap-2.5 text-sm text-base-content/70">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-warning flex-shrink-0" />
                  {t('errors.serverError.tip1')}
                </li>
                <li className="flex items-start gap-2.5 text-sm text-base-content/70">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-warning flex-shrink-0" />
                  {t('errors.serverError.tip2')}
                </li>
              </ul>
            </div>
          </div>

          {/* Dev-only error details */}
          {error?.message && process.env.NODE_ENV !== 'production' && (
            <details className="text-left animate-fade-in-up">
              <summary className="text-xs text-base-content/40 cursor-pointer hover:text-base-content/60 transition-colors select-none">
                {t('errors.serverError.devDetails')}
              </summary>
              <pre className="mt-2 p-3 bg-base-100 rounded-xl text-xs text-error/80 overflow-auto max-h-36 whitespace-pre-wrap break-words">
                {error.message}
                {error.digest ? `\n\nDigest: ${error.digest}` : ''}
              </pre>
            </details>
          )}

        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-xs text-base-content/35">
        © {new Date().getFullYear()} Story Creator
      </footer>
    </div>
  )
}
