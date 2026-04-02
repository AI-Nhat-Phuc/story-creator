// @ts-check
const { test, expect } = require('@playwright/test')

const BASE_URL = process.env.BASE_URL || 'https://story-creator-mxg40480n-nhat-phuc-phams-projects.vercel.app'
const LOGIN_URL = `${BASE_URL}/login`

// Test credentials (from api/test_api.py)
const ADMIN = { username: 'admin', password: 'Admin@123' }
const TEST_USER = { username: 'testuser', password: 'Test@1234' }

test.describe('Login Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(LOGIN_URL)
  })

  // ── UI Rendering ──────────────────────────────────────────────────────────

  test('renders login page with correct elements', async ({ page }) => {
    // Header
    await expect(page.getByRole('heading', { name: /story creator/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /đăng nhập/i })).toBeVisible()

    // Form fields
    await expect(page.getByLabel(/tên đăng nhập/i)).toBeVisible()
    await expect(page.getByLabel(/mật khẩu/i)).toBeVisible()

    // Submit button
    await expect(page.getByRole('button', { name: /đăng nhập/i }).last()).toBeVisible()

    // Register link
    await expect(page.getByRole('link', { name: /đăng ký ngay/i })).toBeVisible()
  })

  test('shows Google OAuth button', async ({ page }) => {
    const googleBtn = page.locator('button', { hasText: /đăng nhập/ }).first()
    await expect(googleBtn).toBeVisible()
  })

  // ── Validation ────────────────────────────────────────────────────────────

  test('requires username and password fields', async ({ page }) => {
    const submitBtn = page.getByRole('button', { name: /đăng nhập/i }).last()
    await submitBtn.click()

    // HTML5 validation prevents submission — fields should still be visible
    await expect(page.getByLabel(/tên đăng nhập/i)).toBeVisible()
    // URL should not have changed away from login
    await expect(page).toHaveURL(/\/login/)
  })

  test('shows error for wrong credentials', async ({ page }) => {
    await page.getByLabel(/tên đăng nhập/i).fill('nonexistent_user')
    await page.getByLabel(/mật khẩu/i).fill('WrongPassword123')

    await page.getByRole('button', { name: /đăng nhập/i }).last().click()

    // Expect error alert to appear
    const errorAlert = page.locator('.alert-error')
    await expect(errorAlert).toBeVisible({ timeout: 10000 })
  })

  test('clears error message when user starts typing', async ({ page }) => {
    // Trigger an error first
    await page.getByLabel(/tên đăng nhập/i).fill('baduser')
    await page.getByLabel(/mật khẩu/i).fill('badpass')
    await page.getByRole('button', { name: /đăng nhập/i }).last().click()

    const errorAlert = page.locator('.alert-error')
    await expect(errorAlert).toBeVisible({ timeout: 10000 })

    // Start typing — error should disappear
    await page.getByLabel(/tên đăng nhập/i).fill('a')
    await expect(errorAlert).not.toBeVisible()
  })

  // ── Successful Login ──────────────────────────────────────────────────────

  test('logs in successfully as admin and redirects to home', async ({ page }) => {
    await page.getByLabel(/tên đăng nhập/i).fill(ADMIN.username)
    await page.getByLabel(/mật khẩu/i).fill(ADMIN.password)

    await page.getByRole('button', { name: /đăng nhập/i }).last().click()

    // Should redirect away from /login on success
    await expect(page).not.toHaveURL(/\/login/, { timeout: 15000 })
  })

  test('logs in successfully as testuser and redirects to home', async ({ page }) => {
    await page.getByLabel(/tên đăng nhập/i).fill(TEST_USER.username)
    await page.getByLabel(/mật khẩu/i).fill(TEST_USER.password)

    await page.getByRole('button', { name: /đăng nhập/i }).last().click()

    await expect(page).not.toHaveURL(/\/login/, { timeout: 15000 })
  })

  // ── Navigation ────────────────────────────────────────────────────────────

  test('navigates to register page via link', async ({ page }) => {
    await page.getByRole('link', { name: /đăng ký ngay/i }).click()
    await expect(page).toHaveURL(/\/register/, { timeout: 10000 })
  })

  test('already authenticated users are redirected away from login', async ({ page }) => {
    // Login first
    await page.getByLabel(/tên đăng nhập/i).fill(ADMIN.username)
    await page.getByLabel(/mật khẩu/i).fill(ADMIN.password)
    await page.getByRole('button', { name: /đăng nhập/i }).last().click()
    await expect(page).not.toHaveURL(/\/login/, { timeout: 15000 })

    // Try to go back to /login — should redirect away
    await page.goto(LOGIN_URL)
    await expect(page).not.toHaveURL(/\/login/, { timeout: 10000 })
  })
})
