// @ts-check
/**
 * Playwright global setup — runs once before all tests.
 *
 * Ensures test accounts exist on the target server regardless of
 * VERCEL_ENV. On Vercel production the backend only auto-seeds 'admin',
 * so we register 'testuser' here (ignores 409 = already exists).
 */
const { request } = require('@playwright/test')

module.exports = async function globalSetup(config) {
  const baseURL =
    process.env.BASE_URL ||
    config.projects?.[0]?.use?.baseURL ||
    'http://localhost:3000'

  const extraHeaders = process.env.VERCEL_BYPASS_SECRET
    ? { 'x-vercel-protection-bypass': process.env.VERCEL_BYPASS_SECRET }
    : {}

  const ctx = await request.newContext({ baseURL, extraHTTPHeaders: extraHeaders })

  try {
    // Register testuser — 201 = created, 409 = already exists, both are fine
    const res = await ctx.post('/api/auth/register', {
      data: {
        username: 'testuser',
        email: 'test@storycreator.local',
        password: 'Test@123',
      },
    })

    if (res.status() === 201) {
      console.log('[global-setup] testuser registered')
    } else if (res.status() === 409 || res.status() === 400) {
      console.log('[global-setup] testuser already exists — skipping')
    } else {
      console.warn(`[global-setup] register testuser returned HTTP ${res.status()}`)
    }

    // Verify admin login works (admin is always seeded by the backend)
    const loginRes = await ctx.post('/api/auth/login', {
      data: { username: 'admin', password: 'Admin@123' },
    })
    if (loginRes.ok()) {
      console.log('[global-setup] admin login verified ✓')
    } else {
      console.error('[global-setup] admin login failed — tests will likely fail')
    }
  } finally {
    await ctx.dispose()
  }
}
