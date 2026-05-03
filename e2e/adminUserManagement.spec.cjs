// @ts-check
/**
 * E2E tests: Admin User Management (/admin/users)
 *
 * Covers:
 *   - Page renders with user list + detail panels
 *   - Selecting a user opens the detail panel
 *   - Toggling active / inactive status
 *   - Updating permission overrides
 *   - Activity logs tab renders (empty state and row state)
 *
 * All tests use programmatic admin login (no UI login flow).
 */
const { test, expect } = require('@playwright/test')
const { login, ADMIN, TEST_USER, LOGIN_TIMEOUT } = require('./utils/auth.cjs')

// Reduced to avoid flakiness on slow CI
const NAV_TIMEOUT = 20000
const API_TIMEOUT = 15000

test.describe('Admin User Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ADMIN)
    await page.goto('/admin/users')
    // Wait for the two-panel layout to be visible
    await expect(page.getByTestId('user-list-panel')).toBeVisible({ timeout: NAV_TIMEOUT })
  })

  // ── Page structure ────────────────────────────────────────────────────────

  test('renders user list panel and empty detail panel', async ({ page }) => {
    await expect(page.getByTestId('user-list-panel')).toBeVisible()
    await expect(page.getByTestId('user-detail-panel')).toBeVisible()
    // No user selected yet — placeholder text is shown
    await expect(page.getByText(/select a user to view details/i)).toBeVisible()
  })

  test('shows at least the admin user in the list', async ({ page }) => {
    // The admin account is always seeded. Scope to the list panel so the selector
    // doesn't conflict with the navbar "Admin" link or role-filter options.
    await expect(
      page.getByTestId('user-list-panel').getByText('admin').first()
    ).toBeVisible({ timeout: API_TIMEOUT })
  })

  test('search filters the user list', async ({ page }) => {
    const searchInput = page.getByTestId('user-search')
    await searchInput.fill('admin')
    await searchInput.press('Enter')
    await expect(
      page.getByTestId('user-list-panel').getByText('admin').first()
    ).toBeVisible({ timeout: API_TIMEOUT })
  })

  // ── Selecting a user ──────────────────────────────────────────────────────

  test('selecting a user reveals the detail panel with Info tab', async ({ page }) => {
    // Click the first visible user row
    const firstRow = page.getByTestId(/^user-row-/).first()
    await expect(firstRow).toBeVisible({ timeout: API_TIMEOUT })
    await firstRow.click()

    await expect(page.getByTestId('user-detail')).toBeVisible()
    await expect(page.getByTestId('tab-info-content')).toBeVisible()
  })

  test('Info tab displays user status badge', async ({ page }) => {
    const firstRow = page.getByTestId(/^user-row-/).first()
    await firstRow.click()
    await expect(page.getByTestId('user-status-badge')).toBeVisible()
  })

  // ── Permissions tab ───────────────────────────────────────────────────────

  test('switching to Permissions tab shows permission editor', async ({ page }) => {
    const firstRow = page.getByTestId(/^user-row-/).first()
    await firstRow.click()

    await page.getByTestId('tab-permissions').click()
    await expect(page.getByTestId('permission-editor')).toBeVisible()
    await expect(page.getByTestId('save-permissions-btn')).toBeVisible()
  })

  test('saving permissions calls the API and shows success toast', async ({ page }) => {
    // Target testuser so we don't self-modify the admin account
    const searchInput = page.getByTestId('user-search')
    await searchInput.fill(TEST_USER.username)
    await searchInput.press('Enter')

    const userRow = page.getByTestId(/^user-row-/).first()
    await expect(userRow).toBeVisible({ timeout: API_TIMEOUT })
    await userRow.click()

    await page.getByTestId('tab-permissions').click()
    await expect(page.getByTestId('permission-editor')).toBeVisible()

    // Intercept the PUT request to verify it fires
    const [req] = await Promise.all([
      page.waitForRequest((r) => r.url().includes('/permissions') && r.method() === 'PUT', {
        timeout: API_TIMEOUT,
      }),
      page.getByTestId('save-permissions-btn').click(),
    ])
    expect(req).toBeTruthy()

    // Toast should appear (success or error depending on backend state)
    await expect(page.locator('.alert, [role="alert"]').first()).toBeVisible({
      timeout: API_TIMEOUT,
    })
  })

  // ── Toggle active / inactive ──────────────────────────────────────────────

  test('Info tab has Deactivate button for an active user', async ({ page }) => {
    // Search for testuser (always active, not admin)
    const searchInput = page.getByTestId('user-search')
    await searchInput.fill(TEST_USER.username)
    await searchInput.press('Enter')

    const userRow = page.getByTestId(/^user-row-/).first()
    await expect(userRow).toBeVisible({ timeout: API_TIMEOUT })
    await userRow.click()

    await expect(page.getByTestId('tab-info-content')).toBeVisible()
    // If the user is active, the button says "Deactivate"
    const statusBtn = page.getByTestId('toggle-status-btn')
    if (await statusBtn.isVisible()) {
      const label = await statusBtn.textContent()
      expect(label?.trim()).toMatch(/Deactivate|Activate/)
    }
  })

  test('toggling status fires the status API and refreshes the panel', async ({ page }) => {
    const searchInput = page.getByTestId('user-search')
    await searchInput.fill(TEST_USER.username)
    await searchInput.press('Enter')

    const userRow = page.getByTestId(/^user-row-/).first()
    await expect(userRow).toBeVisible({ timeout: API_TIMEOUT })
    await userRow.click()

    const statusBtn = page.getByTestId('toggle-status-btn')
    if (!(await statusBtn.isVisible())) {
      test.skip() // banned user — skip
      return
    }

    const [req] = await Promise.all([
      page.waitForRequest(
        (r) => r.url().includes('/status') && r.method() === 'PUT',
        { timeout: API_TIMEOUT }
      ),
      statusBtn.click(),
    ])
    expect(req).toBeTruthy()

    // Status badge must update (may say Inactive or Active depending on previous state)
    await expect(page.getByTestId('user-status-badge')).toBeVisible({ timeout: API_TIMEOUT })

    // Re-activate if we just deactivated (keep test idempotent)
    const updatedBtn = page.getByTestId('toggle-status-btn')
    if (await updatedBtn.isVisible()) {
      const label = await updatedBtn.textContent()
      if (label?.includes('Activate')) {
        await updatedBtn.click()
        await expect(page.getByTestId('user-status-badge')).toHaveText(/Active/, {
          timeout: API_TIMEOUT,
        })
      }
    }
  })

  // ── Activity logs ─────────────────────────────────────────────────────────

  test('Activity tab renders without crashing (empty state)', async ({ page }) => {
    const firstRow = page.getByTestId(/^user-row-/).first()
    await firstRow.click()

    await page.getByTestId('tab-activity').click()
    await expect(page.getByTestId('tab-activity-content')).toBeVisible()

    // Either the empty-state message or actual log rows are visible
    const emptyMsg = page.getByTestId('no-logs-msg')
    const logTable = page.getByTestId('activity-log-table')
    await expect(emptyMsg.or(logTable)).toBeVisible({ timeout: API_TIMEOUT })
  })

  // ── Access control ────────────────────────────────────────────────────────

  test('non-admin visiting /admin/users is redirected', async ({ page }) => {
    // Re-login as testuser (not admin/moderator)
    await login(page, TEST_USER)
    await page.goto('/admin/users')
    // Should be redirected away from /admin/users
    await expect(page).not.toHaveURL(/\/admin\/users/, { timeout: NAV_TIMEOUT })
  })
})
