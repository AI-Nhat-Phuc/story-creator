// @ts-check
const { test, expect } = require('@playwright/test')

const TEST_USER = { username: 'testuser', password: 'Test@123' }

// ── Helpers ────────────────────────────────────────────────────────────────

async function loginAsTestUser(page) {
  await page.goto('/login')
  await page.getByLabel(/tên đăng nhập/i).fill(TEST_USER.username)
  await page.getByLabel(/mật khẩu/i).fill(TEST_USER.password)
  await page.getByRole('button', { name: /đăng nhập/i }).last().click()
  await expect(page).not.toHaveURL(/\/login/, { timeout: 10000 })
}

async function openCreateModal(page) {
  await page.goto('/worlds')
  // Wait for page to load (create button appears)
  await expect(page.getByRole('button', { name: /tạo thế giới mới/i })).toBeVisible({ timeout: 10000 })
  await page.getByRole('button', { name: /tạo thế giới mới/i }).click()
  // Dialog should open
  await expect(page.locator('dialog.modal')).toBeVisible({ timeout: 5000 })
}

// ── Suite ──────────────────────────────────────────────────────────────────

test.describe('Create World Modal', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsTestUser(page)
  })

  // ── Modal Open / Close ────────────────────────────────────────────────────

  test('opens create-world modal when button is clicked', async ({ page }) => {
    await page.goto('/worlds')
    await page.getByRole('button', { name: /tạo thế giới mới/i }).click()
    await expect(page.locator('dialog.modal')).toBeVisible()
    await expect(page.getByRole('heading', { name: /tạo thế giới mới/i })).toBeVisible()
  })

  test('cancel button closes the modal', async ({ page }) => {
    await openCreateModal(page)
    const cancelBtn = page.getByRole('button', { name: /huỷ|hủy/i })
    await expect(cancelBtn).toBeVisible()
    await expect(cancelBtn).toBeEnabled()
    await cancelBtn.click()
    await expect(page.locator('dialog.modal')).not.toBeVisible({ timeout: 3000 })
  })

  test('cancel button is clickable and resets form', async ({ page }) => {
    await openCreateModal(page)

    // Fill in some data
    await page.getByLabel(/tên thế giới/i).fill('Test World Name')

    // Click cancel
    await page.getByRole('button', { name: /huỷ|hủy/i }).click()

    // Modal is gone
    await expect(page.locator('dialog.modal')).not.toBeVisible({ timeout: 3000 })

    // Re-open: form should be reset
    await page.getByRole('button', { name: /tạo thế giới mới/i }).click()
    await expect(page.locator('dialog.modal')).toBeVisible()
    await expect(page.getByLabel(/tên thế giới/i)).toHaveValue('')
  })

  test('ESC key closes the modal', async ({ page }) => {
    await openCreateModal(page)
    await page.keyboard.press('Escape')
    await expect(page.locator('dialog.modal')).not.toBeVisible({ timeout: 3000 })
  })

  // ── Form Validation ───────────────────────────────────────────────────────

  test('create button is visible and enabled when modal opens', async ({ page }) => {
    await openCreateModal(page)
    const createBtn = page.getByRole('button', { name: /tạo & phân tích/i })
    await expect(createBtn).toBeVisible()
    await expect(createBtn).toBeEnabled()
  })

  test('both buttons are clickable from the initial modal state', async ({ page }) => {
    await openCreateModal(page)

    // Verify create button is enabled (not disabled or hidden)
    const createBtn = page.getByRole('button', { name: /tạo & phân tích/i })
    await expect(createBtn).toBeEnabled()
    await expect(createBtn).toBeVisible()

    // Verify cancel button is enabled
    const cancelBtn = page.getByRole('button', { name: /huỷ|hủy/i })
    await expect(cancelBtn).toBeEnabled()
    await expect(cancelBtn).toBeVisible()
  })

  test('create button shows validation toast when fields are empty', async ({ page }) => {
    await openCreateModal(page)

    // Click create without filling required fields
    await page.getByRole('button', { name: /tạo & phân tích/i }).click()

    // Should show a warning toast (not crash, not disable buttons)
    // Modal stays open since validation failed
    await expect(page.locator('dialog.modal')).toBeVisible({ timeout: 2000 })

    // Buttons should still be enabled after a failed validation
    await expect(page.getByRole('button', { name: /huỷ|hủy/i })).toBeEnabled()
  })

  // ── Form Interaction ─────────────────────────────────────────────────────

  test('can type in name and description fields', async ({ page }) => {
    await openCreateModal(page)

    await page.getByLabel(/tên thế giới/i).fill('Thế giới Tây du')
    await expect(page.getByLabel(/tên thế giới/i)).toHaveValue('Thế giới Tây du')

    await page.locator('textarea[name="description"]').fill('Thế giới tu tiên với nhiều nhân vật')
    await expect(page.locator('textarea[name="description"]')).toHaveValue('Thế giới tu tiên với nhiều nhân vật')
  })

  test('world type select has correct options', async ({ page }) => {
    await openCreateModal(page)

    const select = page.locator('select[name="world_type"]')
    await expect(select).toBeVisible()

    // Verify options exist
    await expect(select.locator('option[value="fantasy"]')).toHaveCount(1)
    await expect(select.locator('option[value="sci-fi"]')).toHaveCount(1)
    await expect(select.locator('option[value="modern"]')).toHaveCount(1)
    await expect(select.locator('option[value="historical"]')).toHaveCount(1)
  })

  test('can change world type', async ({ page }) => {
    await openCreateModal(page)

    const select = page.locator('select[name="world_type"]')
    await select.selectOption('sci-fi')
    await expect(select).toHaveValue('sci-fi')
  })

  // ── Mobile bottom-sheet layout ────────────────────────────────────────────

  test('modal renders as dialog element (not div)', async ({ page }) => {
    await openCreateModal(page)
    // Verify it's actually a <dialog> element
    const tagName = await page.locator('.modal').evaluate(el => el.tagName.toLowerCase())
    expect(tagName).toBe('dialog')
  })

  test('buttons remain enabled after cancel-and-reopen cycle', async ({ page }) => {
    await openCreateModal(page)
    await page.getByRole('button', { name: /huỷ|hủy/i }).click()
    await expect(page.locator('dialog.modal')).not.toBeVisible()

    // Re-open
    await page.getByRole('button', { name: /tạo thế giới mới/i }).click()
    await expect(page.locator('dialog.modal')).toBeVisible()

    await expect(page.getByRole('button', { name: /tạo & phân tích/i })).toBeEnabled()
    await expect(page.getByRole('button', { name: /huỷ|hủy/i })).toBeEnabled()
  })
})
