'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslation } from 'react-i18next'
import '../src/i18n'
import {
  BookOpenIcon,
  HomeIcon,
  ArrowLeftIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline'

/* ─── Branded illustration ────────────────────────────────────────────────── */
function NotFoundIllustration() {
  return (
    <div className="relative w-64 h-56 mx-auto select-none" aria-hidden="true">
      {/* Ghost "404" backdrop */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <span className="text-9xl font-black text-primary/8 leading-none tracking-tighter">
          404
        </span>
      </div>

      <svg
        viewBox="0 0 220 180"
        className="w-full h-full drop-shadow-sm"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* ── Open book base ─────────────────────────────────────────────── */}
        {/* Spine */}
        <rect
          x="104" y="54" width="12" height="88"
          rx="3"
          className="fill-primary/25 stroke-primary/60"
          strokeWidth="1.5"
        />

        {/* Left cover */}
        <rect
          x="34" y="52" width="72" height="92"
          rx="5"
          className="fill-base-100 stroke-primary/50"
          strokeWidth="1.5"
        />
        {/* Left cover shadow strip */}
        <rect
          x="34" y="52" width="10" height="92"
          rx="3"
          className="fill-primary/10"
        />
        {/* Left page lines */}
        <line x1="52" y1="78" x2="92" y2="78" strokeOpacity="0.12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <line x1="52" y1="90" x2="92" y2="90" strokeOpacity="0.12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <line x1="52" y1="102" x2="85" y2="102" strokeOpacity="0.12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <line x1="52" y1="114" x2="90" y2="114" strokeOpacity="0.12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <line x1="52" y1="126" x2="78" y2="126" strokeOpacity="0.12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />

        {/* Right cover */}
        <rect
          x="114" y="52" width="72" height="92"
          rx="5"
          className="fill-base-100 stroke-primary/50"
          strokeWidth="1.5"
        />
        {/* Right cover shadow strip */}
        <rect
          x="176" y="52" width="10" height="92"
          rx="3"
          className="fill-primary/10"
        />
        {/* Right page — empty with large "?" */}
        <text
          x="150" y="110"
          textAnchor="middle"
          className="fill-primary/20"
          fontSize="52"
          fontWeight="900"
          fontFamily="system-ui, sans-serif"
        >
          ?
        </text>

        {/* ── Flying page 1 (top-right) ──────────────────────────────────── */}
        <g className="animate-float" style={{ transformOrigin: '176px 24px' }}>
          <rect
            x="158" y="8" width="34" height="44"
            rx="4"
            transform="rotate(-18 175 30)"
            className="fill-base-100 stroke-secondary/80"
            strokeWidth="1.5"
          />
          <line x1="166" y1="22" x2="186" y2="16" strokeOpacity="0.18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="164" y1="31" x2="181" y2="25" strokeOpacity="0.18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="163" y1="40" x2="175" y2="35" strokeOpacity="0.18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </g>

        {/* ── Flying page 2 (top-left) ──────────────────────────────────── */}
        <g className="animate-float-alt" style={{ transformOrigin: '30px 30px' }}>
          <rect
            x="10" y="16" width="30" height="40"
            rx="4"
            transform="rotate(14 25 36)"
            className="fill-base-100 stroke-secondary/70"
            strokeWidth="1.5"
          />
          <line x1="16" y1="30" x2="34" y2="26" strokeOpacity="0.18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="15" y1="40" x2="31" y2="36" strokeOpacity="0.18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </g>

        {/* ── Magnifying glass ──────────────────────────────────────────── */}
        <g className="animate-float-delay" style={{ transformOrigin: '182px 136px' }}>
          <circle
            cx="182" cy="134" r="16"
            className="stroke-accent fill-accent/8"
            strokeWidth="2"
          />
          {/* Inner glint */}
          <circle cx="177" cy="128" r="3" className="fill-accent/20" />
          {/* Handle */}
          <line
            x1="194" y1="146" x2="205" y2="157"
            className="stroke-accent"
            strokeWidth="3"
            strokeLinecap="round"
          />
        </g>

        {/* ── Small decorative dots ────────────────────────────────────── */}
        <circle cx="22" cy="110" r="3" className="fill-primary/15 animate-pulse" />
        <circle cx="198" cy="74" r="2" className="fill-secondary/25 animate-pulse" style={{ animationDelay: '0.4s' }} />
        <circle cx="12" cy="70" r="2" className="fill-accent/20 animate-pulse" style={{ animationDelay: '0.8s' }} />
      </svg>
    </div>
  )
}

/* ─── Page ─────────────────────────────────────────────────────────────────── */
export default function NotFound() {
  const { t } = useTranslation()
  const router = useRouter()

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
            <NotFoundIllustration />
          </div>

          {/* Heading + description */}
          <div className="space-y-3 animate-fade-in-up animation-delay-100">
            <h1 className="text-2xl md:text-3xl font-bold text-base-content">
              {t('errors.notFound.title')}
            </h1>
            <p className="text-base-content/60 leading-relaxed max-w-xs mx-auto text-sm md:text-base">
              {t('errors.notFound.description')}
            </p>
          </div>

          {/* Primary CTAs */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center animate-fade-in-up animation-delay-200">
            <Link
              href="/"
              className="btn btn-primary gap-2 shadow-sm hover:shadow-md transition-shadow"
            >
              <HomeIcon className="w-4 h-4" />
              {t('errors.notFound.goHome')}
            </Link>
            <button
              onClick={() => router.back()}
              className="btn btn-ghost gap-2 hover:bg-base-300 transition-colors"
            >
              <ArrowLeftIcon className="w-4 h-4" />
              {t('errors.notFound.goBack')}
            </button>
          </div>

          {/* Recovery suggestions card */}
          <div className="card bg-base-100 shadow-sm text-left animate-fade-in-up animation-delay-300">
            <div className="card-body py-5 px-6">
              <h2 className="text-xs font-semibold uppercase tracking-widest text-base-content/50 mb-3">
                {t('errors.notFound.suggestionsTitle')}
              </h2>
              <ul className="space-y-2.5">
                {/* Suggestion 1 */}
                <li className="flex items-start gap-2.5 text-sm text-base-content/70">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                  {t('errors.notFound.suggestion1')}
                </li>
                {/* Suggestion 2 — link to stories */}
                <li className="flex items-start gap-2.5 text-sm">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                  <Link
                    href="/stories"
                    className="link link-primary hover:link-hover transition-opacity"
                  >
                    {t('errors.notFound.suggestion2')}
                  </Link>
                </li>
                {/* Suggestion 3 — link to worlds */}
                <li className="flex items-start gap-2.5 text-sm">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                  <Link
                    href="/worlds"
                    className="link link-primary hover:link-hover transition-opacity"
                  >
                    {t('errors.notFound.suggestion3')}
                  </Link>
                </li>
              </ul>
            </div>
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-xs text-base-content/35">
        © {new Date().getFullYear()} Story Creator
      </footer>
    </div>
  )
}
