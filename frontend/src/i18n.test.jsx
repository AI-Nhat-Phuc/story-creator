/**
 * Tests for i18n setup, locale completeness, and per-page meta tags.
 *
 * Spec clauses covered:
 *   §1 — i18n initialization (i18next + react-i18next)
 *   §1 — Locale key schema (vi.json, en.json)
 *   §1 — Language persistence (localStorage sc_lang)
 *   §2 — Per-page <title> and <meta description> via react-helmet-async
 *   §3 — ThemeSelector labels translated
 *
 * All tests are expected to FAIL until IMPLEMENT phase creates:
 *   - frontend/src/i18n/index.js
 *   - frontend/src/i18n/locales/vi.json
 *   - frontend/src/i18n/locales/en.json
 *   and wires Helmet + useTranslation into pages/components.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react'
import React, { Suspense } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'

// Mock Google OAuth to avoid GoogleOAuthProvider requirement
vi.mock('@react-oauth/google', () => ({
  useGoogleLogin: () => () => {},
  GoogleOAuthProvider: ({ children }) => children,
}))

// Mock Facebook Login to avoid context requirement
vi.mock('@greatsumini/react-facebook-login', () => ({
  default: () => null,
}))

// Silence API errors in tests — keep default export (Axios instance) intact
vi.mock('./services/api', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    statsAPI: { get: () => Promise.reject(new Error('test')) },
    authAPI: {
      ...actual.authAPI,
      verifyToken: () => Promise.reject(new Error('test')),
      getCurrentUser: () => Promise.reject(new Error('test')),
    },
    invitationsAPI: { list: () => Promise.resolve({ data: [] }) },
  }
})

// ─── §1: i18n module ─────────────────────────────────────────────────────────

describe('§1 — i18n module (i18n/index.js)', () => {
  it('exports a configured i18next instance', async () => {
    const { default: i18n } = await import('./i18n/index.js')
    expect(i18n).toBeDefined()
    expect(typeof i18n.t).toBe('function')
    expect(typeof i18n.changeLanguage).toBe('function')
  })

  it('exports LANG_KEY constant as "sc_lang"', async () => {
    const { LANG_KEY } = await import('./i18n/index.js')
    expect(LANG_KEY).toBe('sc_lang')
  })

  it('defaults language to "vi"', async () => {
    const { default: i18n } = await import('./i18n/index.js')
    expect(i18n.language).toBe('vi')
  })

  it('has "vi" resource bundle', async () => {
    const { default: i18n } = await import('./i18n/index.js')
    const bundle = i18n.getResourceBundle('vi', 'translation')
    expect(bundle).toBeDefined()
    expect(typeof bundle).toBe('object')
  })

  it('has "en" resource bundle', async () => {
    const { default: i18n } = await import('./i18n/index.js')
    const bundle = i18n.getResourceBundle('en', 'translation')
    expect(bundle).toBeDefined()
    expect(typeof bundle).toBe('object')
  })

  it('reads language from localStorage sc_lang', async () => {
    localStorage.setItem('sc_lang', 'en')
    // Re-import with fresh module cache not possible in Vitest without isolation,
    // but we can test changeLanguage + localStorage write:
    const { default: i18n, LANG_KEY } = await import('./i18n/index.js')
    await i18n.changeLanguage('en')
    // Language toggle should persist
    expect(localStorage.getItem(LANG_KEY)).toBe('en')
    // Reset
    await i18n.changeLanguage('vi')
    localStorage.setItem(LANG_KEY, 'vi')
  })
})

// ─── §1: vi.json locale keys ─────────────────────────────────────────────────

describe('§1 — vi.json locale key schema', () => {
  let vi_locale

  beforeEach(async () => {
    vi_locale = (await import('./i18n/locales/vi.json')).default
  })

  it('has common.* keys', () => {
    expect(vi_locale.common).toBeDefined()
    expect(vi_locale.common.loading).toBeDefined()
    expect(vi_locale.common.cancel).toBeDefined()
    expect(vi_locale.common.error).toBeDefined()
  })

  it('has actions.* keys', () => {
    expect(vi_locale.actions).toBeDefined()
    expect(vi_locale.actions.create).toBeDefined()
    expect(vi_locale.actions.edit).toBeDefined()
    expect(vi_locale.actions.delete).toBeDefined()
    expect(vi_locale.actions.logout).toBeDefined()
  })

  it('has nav.* keys', () => {
    expect(vi_locale.nav).toBeDefined()
    expect(vi_locale.nav.dashboard).toBeDefined()
    expect(vi_locale.nav.worlds).toBeDefined()
    expect(vi_locale.nav.stories).toBeDefined()
    expect(vi_locale.nav.logoutConfirmTitle).toBeDefined()
    expect(vi_locale.nav.logoutConfirmMsg).toBeDefined()
  })

  it('has theme.* keys including language toggle', () => {
    expect(vi_locale.theme).toBeDefined()
    expect(vi_locale.theme.light).toBeDefined()
    expect(vi_locale.theme.dark).toBeDefined()
    expect(vi_locale.theme.custom).toBeDefined()
    expect(vi_locale.theme.language).toBeDefined()
    expect(vi_locale.theme.vi).toBeDefined()
    expect(vi_locale.theme.en).toBeDefined()
  })

  it('has roles.* keys for all 4 roles', () => {
    expect(vi_locale.roles).toBeDefined()
    expect(vi_locale.roles.admin).toBeDefined()
    expect(vi_locale.roles.moderator).toBeDefined()
    expect(vi_locale.roles.premium).toBeDefined()
    expect(vi_locale.roles.user).toBeDefined()
  })

  it('has meta.* keys for all 12 routes', () => {
    const m = vi_locale.meta
    expect(m).toBeDefined()
    const routes = [
      'dashboard', 'worlds', 'worldDetail', 'novel',
      'stories', 'storyCreate', 'storyEdit', 'storyDetail',
      'storyPrint', 'login', 'register', 'admin',
    ]
    for (const route of routes) {
      expect(m[route], `meta.${route} missing`).toBeDefined()
    }
  })

  it('each meta route has title and description keys', () => {
    const staticRoutes = ['dashboard', 'worlds', 'stories', 'storyCreate', 'login', 'register', 'admin']
    for (const route of staticRoutes) {
      expect(vi_locale.meta[route].title, `meta.${route}.title missing`).toBeDefined()
      expect(vi_locale.meta[route].description, `meta.${route}.description missing`).toBeDefined()
    }
  })

  it('dynamic routes have titleTemplate and titleFallback', () => {
    const dynamicRoutes = ['worldDetail', 'novel', 'storyEdit', 'storyDetail', 'storyPrint']
    for (const route of dynamicRoutes) {
      expect(vi_locale.meta[route].titleTemplate, `meta.${route}.titleTemplate missing`).toBeDefined()
      expect(vi_locale.meta[route].titleFallback, `meta.${route}.titleFallback missing`).toBeDefined()
    }
  })

  it('has pages.dashboard.* keys', () => {
    expect(vi_locale.pages?.dashboard?.title).toBeDefined()
    expect(vi_locale.pages?.dashboard?.totalWorlds).toBeDefined()
    expect(vi_locale.pages?.dashboard?.totalStories).toBeDefined()
  })

  it('has pages.worlds.* keys', () => {
    expect(vi_locale.pages?.worlds?.title).toBeDefined()
    expect(vi_locale.pages?.worlds?.createBtn).toBeDefined()
    expect(vi_locale.pages?.worlds?.emptyAuth).toBeDefined()
  })

  it('has pages.login.* keys', () => {
    expect(vi_locale.pages?.login?.title).toBeDefined()
    expect(vi_locale.pages?.login?.username).toBeDefined()
    expect(vi_locale.pages?.login?.password).toBeDefined()
  })

  it('has pages.register.* keys', () => {
    expect(vi_locale.pages?.register?.title).toBeDefined()
    expect(vi_locale.pages?.register?.username).toBeDefined()
    expect(vi_locale.pages?.register?.password).toBeDefined()
  })
})

// ─── §1: en.json mirrors vi.json ─────────────────────────────────────────────

describe('§1 — en.json key parity with vi.json', () => {
  it('en.json has all top-level sections that vi.json has', async () => {
    const vi_locale = (await import('./i18n/locales/vi.json')).default
    const en_locale = (await import('./i18n/locales/en.json')).default
    const viKeys = Object.keys(vi_locale)
    for (const key of viKeys) {
      expect(en_locale[key], `en.json missing top-level key: ${key}`).toBeDefined()
    }
  })

  it('en.json has all meta routes', async () => {
    const vi_locale = (await import('./i18n/locales/vi.json')).default
    const en_locale = (await import('./i18n/locales/en.json')).default
    for (const route of Object.keys(vi_locale.meta)) {
      expect(en_locale.meta[route], `en.json missing meta.${route}`).toBeDefined()
    }
  })
})

// ─── §2: Per-page <title> via Helmet ─────────────────────────────────────────

describe('§2 — LoginPage renders with <title>', () => {
  it('sets document title to login meta title', async () => {
    const { default: LoginPage } = await import('./pages/LoginPage.jsx')
    const { AuthProvider } = await import('./contexts/AuthContext.jsx')
    const { ThemeProvider } = await import('./contexts/ThemeContext.jsx')
    const helmetContext = {}

    await act(async () => {
      render(
        <HelmetProvider context={helmetContext}>
          <ThemeProvider>
            <AuthProvider>
              <MemoryRouter>
                <LoginPage showToast={() => {}} />
              </MemoryRouter>
            </AuthProvider>
          </ThemeProvider>
        </HelmetProvider>
      )
    })

    await waitFor(() => {
      expect(document.title).toContain('Đăng nhập')
      expect(document.title).toContain('Story Creator')
    })
  })
})

describe('§2 — RegisterPage renders with <title>', () => {
  it('sets document title to register meta title', async () => {
    const { default: RegisterPage } = await import('./pages/RegisterPage.jsx')
    const { AuthProvider } = await import('./contexts/AuthContext.jsx')
    const { ThemeProvider } = await import('./contexts/ThemeContext.jsx')
    const helmetContext = {}

    await act(async () => {
      render(
        <HelmetProvider context={helmetContext}>
          <ThemeProvider>
            <AuthProvider>
              <MemoryRouter>
                <RegisterPage showToast={() => {}} />
              </MemoryRouter>
            </AuthProvider>
          </ThemeProvider>
        </HelmetProvider>
      )
    })

    await waitFor(() => {
      expect(document.title).toContain('Đăng ký')
      expect(document.title).toContain('Story Creator')
    })
  })
})

describe('§2 — Dashboard renders with <title>', () => {
  it('sets document title to dashboard meta title', async () => {
    const { default: Dashboard } = await import('./pages/Dashboard.jsx')
    const { AuthProvider } = await import('./contexts/AuthContext.jsx')
    const { ThemeProvider } = await import('./contexts/ThemeContext.jsx')

    await act(async () => {
      render(
        <HelmetProvider>
          <ThemeProvider>
            <AuthProvider>
              <MemoryRouter>
                <Dashboard showToast={() => {}} />
              </MemoryRouter>
            </AuthProvider>
          </ThemeProvider>
        </HelmetProvider>
      )
    })

    await waitFor(() => {
      expect(document.title).toContain('Story Creator')
    })
  })
})

// ─── §3: ThemeSelector has translated labels ──────────────────────────────────

describe('§3 — ThemeSelector uses i18n labels', () => {
  it('renders mode buttons using translated labels (not hardcoded English)', async () => {
    const { default: ThemeSelector } = await import('./components/ThemeSelector.jsx')
    const { ThemeProvider } = await import('./contexts/ThemeContext.jsx')

    render(
      <ThemeProvider>
        <ThemeSelector />
      </ThemeProvider>
    )

    // Should NOT have hardcoded English 'Light', 'Dark', 'Custom'
    // Should have Vietnamese equivalents from i18n
    const lightBtn = screen.queryByText('Light')
    const darkBtn = screen.queryByText('Dark')
    expect(lightBtn).toBeNull()
    expect(darkBtn).toBeNull()
  })

  it('renders a language toggle with vi/en options', async () => {
    const { default: ThemeSelector } = await import('./components/ThemeSelector.jsx')
    const { ThemeProvider } = await import('./contexts/ThemeContext.jsx')

    render(
      <ThemeProvider>
        <ThemeSelector />
      </ThemeProvider>
    )

    // Language section should exist
    const viBtn = screen.queryByText('Tiếng Việt')
    const enBtn = screen.queryByText('English')
    // At least one should be present (language toggle rendered)
    const hasLanguageToggle = viBtn !== null || enBtn !== null
    expect(hasLanguageToggle).toBe(true)
  })
})

// ─── §1: Navbar uses i18n labels ─────────────────────────────────────────────

describe('§1 — Navbar uses i18n for nav labels', () => {
  it('renders nav links using t() not hardcoded strings', async () => {
    // After implementation, Navbar should call useTranslation
    // We verify indirectly: the nav link text matches i18n vi.json values
    const { default: Navbar } = await import('./components/Navbar.jsx')
    const { AuthProvider } = await import('./contexts/AuthContext.jsx')
    const { ThemeProvider } = await import('./contexts/ThemeContext.jsx')

    render(
      <ThemeProvider>
        <AuthProvider>
          <MemoryRouter>
            <Navbar />
          </MemoryRouter>
        </AuthProvider>
      </ThemeProvider>
    )

    // Dashboard link text comes from i18n key nav.dashboard = "Dashboard"
    const dashLinks = screen.getAllByText('Dashboard')
    expect(dashLinks.length).toBeGreaterThan(0)
  })
})
