// @ts-check
/**
 * Shared authentication helpers for e2e specs.
 *
 * Centralises login so every spec uses the same credentials and approach.
 *
 * `login()` performs a PROGRAMMATIC login (POST /api/auth/login + set
 * localStorage token) rather than driving the UI. On Vercel cold starts
 * the login UI redirect can take 20–30 s, which makes the UI-based login
 * flaky in every spec that only needs an authenticated session. The UI
 * login flow is still exercised directly by login.spec.cjs.
 */
const { expect } = require('@playwright/test')

// Upper bound for the programmatic login API request — Vercel cold starts
// can take 15–20 s on the first request, so give this room to breathe.
const LOGIN_TIMEOUT = 30000

// Test credentials (from api/test_api.py)
const ADMIN = { username: 'admin', password: 'Admin@123' }
const TEST_USER = { username: 'testuser', password: 'Test@123' }

/**
 * Programmatic login: POST credentials, stash the JWT in localStorage.
 * After calling this, any full navigation (`page.goto`) will load the app
 * as an authenticated session — AuthContext re-mounts and picks up the token.
 *
 * @param {import('@playwright/test').Page} page
 * @param {{ username: string, password: string }} [user]
 */
async function login(page, user = ADMIN) {
  // Navigate to establish the app origin so localStorage is writable.
  await page.goto('/login')

  // Retry on transient failures:
  //   5xx — Vercel/Mongo cold-start burp; short backoff.
  //   429 — shared GH Actions IP hits the auth rate limit (10/min);
  //         wait past the 60 s window before retrying.
  //   4xx (other) — real auth error; fail fast.
  const backoffs5xx = [2000, 4000]
  const backoff429 = 20000
  let res
  let lastBody = ''
  for (let attempt = 0; attempt < 3; attempt++) {
    res = await page.request.post('/api/auth/login', {
      data: { username: user.username, password: user.password },
      timeout: LOGIN_TIMEOUT,
    })
    if (res.ok()) break
    lastBody = (await res.text().catch(() => '')).slice(0, 500)
    console.error(`[login] attempt ${attempt + 1} HTTP ${res.status()}: ${lastBody}`)
    if (res.status() === 429) {
      await page.waitForTimeout(backoff429)
      continue
    }
    if (res.status() >= 500 && attempt < backoffs5xx.length) {
      await page.waitForTimeout(backoffs5xx[attempt])
      continue
    }
    break
  }
  expect(res.ok(), `login API failed: HTTP ${res.status()} — ${lastBody}`).toBeTruthy()

  const body = await res.json()
  const token = body.token ?? body.data?.token
  expect(token, 'login API did not return a token').toBeTruthy()

  await page.evaluate((t) => {
    localStorage.setItem('auth_token', t)
    // Force English locale so text-based selectors match English strings.
    localStorage.setItem('sc_lang', 'en')
    document.cookie = 'sc_lang=en; path=/; max-age=31536000; samesite=lax'
  }, token)
}

module.exports = { login, ADMIN, TEST_USER, LOGIN_TIMEOUT }
