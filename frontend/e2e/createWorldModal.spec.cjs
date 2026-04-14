// @ts-check
const { test, expect } = require('@playwright/test')
const { login, TEST_USER } = require('./utils/auth.cjs')

// ── Helpers ────────────────────────────────────────────────────────────────

const loginAsTestUser = (page) => login(page, TEST_USER)

/** Navigate to /worlds, wait for the enabled create button, open the modal. */
async function openCreateModal(page) {
  await page.goto('/worlds')
  // Wait for auth to settle and the enabled create button to appear.
  // testuser is non-admin, so the button is clickable (no btn-disabled class).
  const createBtn = page.locator('button.btn-primary:not(.btn-disabled)', {
    hasText: /tạo thế giới mới/i,
  })
  await expect(createBtn).toBeVisible({ timeout: 15000 })
  await createBtn.click()
  // Dialog should open (native <dialog open> attribute)
  await expect(page.locator('dialog.modal[open]')).toBeVisible({ timeout: 5000 })
}

// Scoped selectors inside the open dialog
const dialogSel = 'dialog.modal[open]'
const nameInput = (page) => page.locator(`${dialogSel} input[name="name"]`)
const descTextarea = (page) => page.locator(`${dialogSel} textarea[name="description"]`)
const worldTypeSelect = (page) => page.locator(`${dialogSel} select[name="world_type"]`)
const createBtn = (page) => page.locator(`${dialogSel} button`).filter({ hasText: /phân tích/i })
const cancelBtn = (page) => page.locator(`${dialogSel} button`).filter({ hasText: /hủy/i })

// ── Suite ──────────────────────────────────────────────────────────────────

test.describe('Create World Modal', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsTestUser(page)
  })

  // ── Modal Open / Close ────────────────────────────────────────────────────

  test('opens create-world modal when button is clicked', async ({ page }) => {
    await openCreateModal(page)
    await expect(page.locator(dialogSel)).toBeVisible()
    // Modal heading is inside the open dialog
    await expect(page.locator(`${dialogSel} h3`)).toContainText(/tạo thế giới mới/i)
  })

  test('cancel button closes the modal', async ({ page }) => {
    await openCreateModal(page)
    await expect(cancelBtn(page)).toBeVisible()
    await expect(cancelBtn(page)).toBeEnabled()
    await cancelBtn(page).click()
    await expect(page.locator('dialog.modal[open]')).not.toBeVisible({ timeout: 3000 })
  })

  test('cancel button resets form on close', async ({ page }) => {
    await openCreateModal(page)

    // Fill in some data
    await nameInput(page).fill('Test World Name')
    await expect(nameInput(page)).toHaveValue('Test World Name')

    // Cancel
    await cancelBtn(page).click()
    await expect(page.locator('dialog.modal[open]')).not.toBeVisible({ timeout: 3000 })

    // Re-open: form should be empty
    await openCreateModal(page)
    await expect(nameInput(page)).toHaveValue('')
  })

  test('ESC key closes the modal', async ({ page }) => {
    await openCreateModal(page)
    await page.keyboard.press('Escape')
    await expect(page.locator('dialog.modal[open]')).not.toBeVisible({ timeout: 3000 })
  })

  // ── Button States ─────────────────────────────────────────────────────────

  test('create-and-analyze button is visible and enabled in initial state', async ({ page }) => {
    await openCreateModal(page)
    await expect(createBtn(page)).toBeVisible()
    await expect(createBtn(page)).toBeEnabled()
  })

  test('cancel button is visible and enabled in initial state', async ({ page }) => {
    await openCreateModal(page)
    await expect(cancelBtn(page)).toBeVisible()
    await expect(cancelBtn(page)).toBeEnabled()
  })

  test('both action buttons are clickable immediately after modal opens', async ({ page }) => {
    await openCreateModal(page)
    // Neither button should be disabled or hidden initially
    await expect(createBtn(page)).toBeEnabled()
    await expect(cancelBtn(page)).toBeEnabled()
  })

  test('clicking create with empty fields keeps modal open (validation)', async ({ page }) => {
    await openCreateModal(page)
    await createBtn(page).click()
    // Modal stays open after failed validation
    await expect(page.locator(dialogSel)).toBeVisible({ timeout: 2000 })
    // Buttons should still be enabled
    await expect(cancelBtn(page)).toBeEnabled()
  })

  // ── Form Interaction ──────────────────────────────────────────────────────

  test('can type in name and description fields', async ({ page }) => {
    await openCreateModal(page)

    await nameInput(page).fill('Thế giới Tây du')
    await expect(nameInput(page)).toHaveValue('Thế giới Tây du')

    await descTextarea(page).fill('Thế giới tu tiên với nhiều nhân vật')
    await expect(descTextarea(page)).toHaveValue('Thế giới tu tiên với nhiều nhân vật')
  })

  test('world type select has expected options', async ({ page }) => {
    await openCreateModal(page)
    const sel = worldTypeSelect(page)
    await expect(sel).toBeVisible()
    await expect(sel.locator('option[value="fantasy"]')).toHaveCount(1)
    await expect(sel.locator('option[value="sci-fi"]')).toHaveCount(1)
    await expect(sel.locator('option[value="modern"]')).toHaveCount(1)
    await expect(sel.locator('option[value="historical"]')).toHaveCount(1)
  })

  test('can change world type', async ({ page }) => {
    await openCreateModal(page)
    const sel = worldTypeSelect(page)
    await sel.selectOption('sci-fi')
    await expect(sel).toHaveValue('sci-fi')
  })

  // ── Dialog element ────────────────────────────────────────────────────────

  test('modal renders as native <dialog> element', async ({ page }) => {
    await openCreateModal(page)
    const tagName = await page.locator(dialogSel).evaluate((el) => el.tagName.toLowerCase())
    expect(tagName).toBe('dialog')
  })

  test('buttons remain enabled after cancel-and-reopen cycle', async ({ page }) => {
    await openCreateModal(page)
    await cancelBtn(page).click()
    await expect(page.locator('dialog.modal[open]')).not.toBeVisible({ timeout: 3000 })

    await openCreateModal(page)
    await expect(createBtn(page)).toBeEnabled()
    await expect(cancelBtn(page)).toBeEnabled()
  })
})
