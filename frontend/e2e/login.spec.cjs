// @ts-check
const { test, expect } = require('@playwright/test')

// All navigation uses relative paths so baseURL from playwright.config.cjs
// is the single source of truth — no URL constructed here.

// Test credentials (from api/test_api.py)
const ADMIN = { username: 'admin', password: 'Admin@123' }
const TEST_USER = { username: 'testuser', password: 'Test@1234' }

test.describe('Login Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  // ── UI Rendering ──────────────────────────────────────────────────────────

  test('renders login page with correct elements', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /story creator/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /đăng nhập/i })).toBeVisible()
    await expect(page.getByLabel(/tên đăng nhập/i)).toBeVisible()
    await expect(page.getByLabel(/mật khẩu/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /đăng nhập/i }).last()).toBeVisible()
    await expect(page.getByRole('link', { name: /đăng ký ngay/i })).toBeVisible()
  })

  test('shows Google OAuth button', async ({ page }) => {
    await expect(page.locator('button', { hasText: /đăng nhập/ }).first()).toBeVisible()
  })

  // ── Validation ────────────────────────────────────────────────────────────

  test('requires username and password (HTML5 validation blocks submit)', async ({ page }) => {
    await page.getByRole('button', { name: /đăng nhập/i }).last().click()
    // HTML5 required attribute prevents submission — still on /login
    await expect(page).toHaveURL(/\/login/)
  })

  test('shows error for wrong credentials', async ({ page }) => {
    await page.getByLabel(/tên đăng nhập/i).fill('nonexistent_user')
    await page.getByLabel(/mật khẩu/i).fill('WrongPassword123')
    await page.getByRole('button', { name: /đăng nhập/i }).last().click()

    await expect(page.locator('.alert-error')).toBeVisible()
  })

  test('clears error message when user starts typing', async ({ page }) => {
    await page.getByLabel(/tên đăng nhập/i).fill('baduser')
    await page.getByLabel(/mật khẩu/i).fill('badpass')
    await page.getByRole('button', { name: /đăng nhập/i }).last().click()

    await expect(page.locator('.alert-error')).toBeVisible()

    await page.getByLabel(/tên đăng nhập/i).fill('a')
    await expect(page.locator('.alert-error')).not.toBeVisible()
  })

  // ── Successful Login ──────────────────────────────────────────────────────

  test('logs in as admin and redirects away from /login', async ({ page }) => {
    await page.getByLabel(/tên đăng nhập/i).fill(ADMIN.username)
    await page.getByLabel(/mật khẩu/i).fill(ADMIN.password)
    await page.getByRole('button', { name: /đăng nhập/i }).last().click()

    await expect(page).not.toHaveURL(/\/login/)
  })

  test('logs in as testuser and redirects away from /login', async ({ page }) => {
    await page.getByLabel(/tên đăng nhập/i).fill(TEST_USER.username)
    await page.getByLabel(/mật khẩu/i).fill(TEST_USER.password)
    await page.getByRole('button', { name: /đăng nhập/i }).last().click()

    await expect(page).not.toHaveURL(/\/login/)
  })

  // ── Navigation ────────────────────────────────────────────────────────────

  test('navigates to register page via link', async ({ page }) => {
    await page.getByRole('link', { name: /đăng ký ngay/i }).click()
    await expect(page).toHaveURL(/\/register/)
  })

  test('authenticated users visiting /login are redirected away', async ({ page }) => {
    // Login first
    await page.getByLabel(/tên đăng nhập/i).fill(ADMIN.username)
    await page.getByLabel(/mật khẩu/i).fill(ADMIN.password)
    await page.getByRole('button', { name: /đăng nhập/i }).last().click()
    await expect(page).not.toHaveURL(/\/login/)

    // Revisit /login — should redirect away immediately
    await page.goto('/login')
    await expect(page).not.toHaveURL(/\/login/)
  })
})
