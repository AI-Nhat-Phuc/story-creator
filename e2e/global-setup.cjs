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

    // Enable GPT access for testuser so GPT button E2E tests can pass
    if (loginRes.ok()) {
      const adminToken = (await loginRes.json()).token
      const adminCtx = await request.newContext({
        baseURL,
        extraHTTPHeaders: {
          ...extraHeaders,
          Authorization: `Bearer ${adminToken}`,
        },
      })
      try {
        // Look up testuser's ID via the admin users list
        const usersRes = await adminCtx.get('/api/admin/users?search=testuser')
        if (usersRes.ok()) {
          const usersData = await usersRes.json()
          const testUser = (usersData.data?.users || usersData.users || []).find(
            (u) => u.username === 'testuser'
          )
          if (testUser) {
            const gptRes = await adminCtx.put(
              `/api/admin/users/${testUser.user_id}/gpt-access`,
              { data: { enabled: true } }
            )
            if (gptRes.ok()) {
              console.log('[global-setup] testuser GPT access enabled ✓')
            } else {
              console.warn(`[global-setup] failed to enable GPT for testuser: ${gptRes.status()}`)
            }
          } else {
            console.warn('[global-setup] testuser not found in admin users list')
          }
        }
      } finally {
        await adminCtx.dispose()
      }
    }

    // Warm up the Vercel Python lambda before tests start.
    // A cold-start can take 5-15 s; hitting /api/health forces the instance
    // to finish initialising so the first storyEditor test's API calls
    // (verifyToken + checkForDraft) don't time out.
    const healthRes = await ctx.get('/api/health')
    if (healthRes.ok()) {
      console.log('[global-setup] backend warm ✓')
    } else {
      console.warn(`[global-setup] health check returned HTTP ${healthRes.status()}`)
    }
  } finally {
    await ctx.dispose()
  }
}
