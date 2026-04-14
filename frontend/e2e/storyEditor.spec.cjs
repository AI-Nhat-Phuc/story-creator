// @ts-check
const { test, expect } = require('@playwright/test')

const ADMIN = { username: 'admin', password: 'Admin@123' }

// ── Helpers ───────────────────────────────────────────────────────────────

// Login API can be slow on cold starts — give login redirect 20 s.
const LOGIN_TIMEOUT = 20000

async function login(page, user = ADMIN) {
  await page.goto('/login')
  await page.getByLabel(/tên đăng nhập/i).fill(user.username)
  await page.getByLabel(/mật khẩu/i).fill(user.password)
  await page.getByRole('button', { name: /đăng nhập/i }).last().click()
  await expect(page).not.toHaveURL(/\/login/, { timeout: LOGIN_TIMEOUT })
}

/** Get auth token from localStorage and ensure a world exists; returns worldId. */
async function ensureWorld(page) {
  const token = await page.evaluate(() => localStorage.getItem('auth_token'))

  // Try to find an existing world first
  const listRes = await page.request.get('/api/worlds', {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (listRes.ok()) {
    const body = await listRes.json()
    const worlds = body.data?.worlds ?? body.data ?? []
    if (worlds.length > 0) return worlds[0].world_id
  }

  // Create a world if none exist
  const createRes = await page.request.post('/api/worlds', {
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    data: { name: 'E2E Test World', world_type: 'modern', description: 'Created by e2e tests' },
  })
  const body = await createRes.json()
  return body.data?.world_id
}

/** Navigate to the story editor (new story) and wait for it to be ready. */
async function openEditor(page, worldId) {
  await page.goto(`/stories/new?worldId=${worldId}`)
  await expect(page.locator('.ProseMirror')).toBeVisible({ timeout: 15000 })
}

// ── Suite ─────────────────────────────────────────────────────────────────

test.describe('Story Editor', () => {
  let worldId

  test.beforeEach(async ({ page }) => {
    await login(page)
    worldId = await ensureWorld(page)
    await openEditor(page, worldId)
  })

  // ── Layout ──────────────────────────────────────────────────────────────

  test('renders editor layout: header, toolbar, left panel, editor area', async ({ page }) => {
    // Header elements
    await expect(page.locator('input[placeholder*="tiêu đề"], input[placeholder*="Tiêu đề"], input[placeholder*="title"], input[placeholder*="Title"]').first()).toBeVisible()

    // Formatting toolbar
    await expect(page.getByTitle('Bold (Ctrl+B)')).toBeVisible()
    await expect(page.getByTitle('Italic (Ctrl+I)')).toBeVisible()
    await expect(page.getByTitle('Underline (Ctrl+U)')).toBeVisible()

    // Left panel GPT section
    await expect(page.getByRole('button', { name: /diễn đạt lại/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /mở rộng/i })).toBeVisible()

    // Editor area
    await expect(page.locator('.ProseMirror')).toBeVisible()
  })

  // ── Title ───────────────────────────────────────────────────────────────

  test('can edit story title', async ({ page }) => {
    const titleInput = page.locator('input[placeholder*="tiêu đề"], input[placeholder*="Tiêu đề"], input[placeholder*="title"], input[placeholder*="Title"]').first()
    await titleInput.fill('My E2E Test Story')
    await expect(titleInput).toHaveValue('My E2E Test Story')
  })

  // ── Editor text input ────────────────────────────────────────────────────

  test('can type text in the editor', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('Hello, this is a test story.')
    await expect(editor).toContainText('Hello, this is a test story.')
  })

  test('clicking empty area below text focuses the editor', async ({ page }) => {
    const editor = page.locator('.ProseMirror')

    // Type a small amount of text (ProseMirror will be ~24px tall)
    await editor.click()
    await editor.type('Hi')

    // Blur using the title input (reliably focusable)
    await page.locator('input').first().click()
    await expect(editor).not.toBeFocused({ timeout: 2000 })

    // Click in the editor area well below the text, but within the visible viewport.
    // main can extend below viewport (clipped by outer overflow-hidden), so we use
    // main.top + 300px which is guaranteed to be: (a) below ProseMirror (~24px from top)
    // and (b) inside the visible area (main.top ~193, +300 = ~493 < viewport 720).
    const main = page.locator('main.cursor-text')
    const mainBox = await main.boundingBox()
    await page.mouse.click(mainBox.x + mainBox.width / 2, mainBox.y + 300)

    // Verify focus: if the handler fired, ProseMirror should be focused
    await expect(editor).toBeFocused({ timeout: 3000 })
  })

  // ── Formatting toolbar ───────────────────────────────────────────────────

  test('Bold button toggles bold formatting on selected text', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('Bold me')

    // Select all text
    await page.keyboard.press('Control+A')

    // Click Bold button
    await page.getByTitle('Bold (Ctrl+B)').click()

    // Check that a <strong> tag exists in the editor
    await expect(editor.locator('strong')).toBeVisible()
  })

  test('Italic button toggles italic formatting', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('Italic me')
    await page.keyboard.press('Control+A')
    await page.getByTitle('Italic (Ctrl+I)').click()
    await expect(editor.locator('em')).toBeVisible()
  })

  test('Underline button toggles underline formatting', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('Underline me')
    await page.keyboard.press('Control+A')
    await page.getByTitle('Underline (Ctrl+U)').click()
    await expect(editor.locator('u')).toBeVisible()
  })

  test('Strikethrough button applies strikethrough', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('Strike me')
    await page.keyboard.press('Control+A')
    await page.getByTitle('Strikethrough').click()
    await expect(editor.locator('s')).toBeVisible()
  })

  test('Highlight button applies yellow background', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('Highlight me')
    await page.keyboard.press('Control+A')
    await page.getByTitle('Highlight').click()
    await expect(editor.locator('mark')).toBeVisible()
  })

  test('H1 button applies heading 1', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('My Heading')
    await page.keyboard.press('Control+A')
    await page.getByTitle('Heading 1').click()
    await expect(editor.locator('h1')).toContainText('My Heading')
  })

  test('H2 button applies heading 2', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('Sub Heading')
    await page.keyboard.press('Control+A')
    await page.getByTitle('Heading 2').click()
    await expect(editor.locator('h2')).toContainText('Sub Heading')
  })

  test('Bullet list button creates a list', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('List item')
    await page.keyboard.press('Control+A')
    await page.getByTitle('Bullet list').click()
    await expect(editor.locator('ul li')).toBeVisible()
  })

  test('Numbered list button creates an ordered list', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('Ordered item')
    await page.keyboard.press('Control+A')
    await page.getByTitle('Numbered list').click()
    await expect(editor.locator('ol li')).toBeVisible()
  })

  test('Align center applies text-align center', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('Center me')
    await page.keyboard.press('Control+A')
    await page.getByTitle('Align center').click()
    await expect(editor.locator('[style*="text-align: center"], [style*="text-align:center"]')).toBeVisible()
  })

  test('toolbar active state updates when cursor moves into bold text', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()

    // Type bold text via keyboard shortcut
    await page.keyboard.press('Control+B')
    await editor.type('bold word')
    await page.keyboard.press('Control+B')

    // Place cursor inside the bold word
    await page.keyboard.press('ArrowLeft')

    // Bold button should now have active styling
    const boldBtn = page.getByTitle('Bold (Ctrl+B)')
    await expect(boldBtn).toHaveClass(/btn-active|bg-base-300/)
  })

  // ── GPT tools panel ──────────────────────────────────────────────────────

  test('GPT Paraphrase and Expand buttons are disabled with no selection', async ({ page }) => {
    await expect(page.getByRole('button', { name: /diễn đạt lại/i })).toBeDisabled()
    await expect(page.getByRole('button', { name: /mở rộng/i })).toBeDisabled()
  })

  test('GPT buttons enable after selecting ≥10 characters', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('This is enough text to select')

    // Select all — more than 10 chars
    await page.keyboard.press('Control+A')

    // Buttons should become enabled
    await expect(page.getByRole('button', { name: /diễn đạt lại/i })).toBeEnabled({ timeout: 3000 })
    await expect(page.getByRole('button', { name: /mở rộng/i })).toBeEnabled({ timeout: 3000 })
  })

  test('GPT buttons remain disabled when fewer than 10 characters selected', async ({ page }) => {
    const editor = page.locator('.ProseMirror')
    await editor.click()
    await editor.type('Short')   // 5 chars — below threshold

    await page.keyboard.press('Control+A')

    await expect(page.getByRole('button', { name: /diễn đạt lại/i })).toBeDisabled()
    await expect(page.getByRole('button', { name: /mở rộng/i })).toBeDisabled()
  })
})
