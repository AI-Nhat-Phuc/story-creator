// @ts-check
/**
 * Shared authentication helpers for e2e specs.
 *
 * Centralises the UI login flow so every spec uses the same selectors
 * and timeout. The login API can be slow on Vercel cold starts, so the
 * post-submit redirect gets a generous 20 s window.
 */
const { expect } = require('@playwright/test')

// Login API can be slow on cold starts — give login redirect 20 s.
const LOGIN_TIMEOUT = 20000

// Test credentials (from api/test_api.py)
const ADMIN = { username: 'admin', password: 'Admin@123' }
const TEST_USER = { username: 'testuser', password: 'Test@123' }

/**
 * Log in via the UI and wait for redirect away from /login.
 * @param {import('@playwright/test').Page} page
 * @param {{ username: string, password: string }} [user]
 */
async function login(page, user = ADMIN) {
  await page.goto('/login')
  await page.getByLabel(/tên đăng nhập/i).fill(user.username)
  await page.getByLabel(/mật khẩu/i).fill(user.password)
  await page.getByRole('button', { name: /đăng nhập/i }).last().click()
  await expect(page).not.toHaveURL(/\/login/, { timeout: LOGIN_TIMEOUT })
}

module.exports = { login, ADMIN, TEST_USER, LOGIN_TIMEOUT }
