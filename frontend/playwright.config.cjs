// @ts-check
const { defineConfig, devices } = require('@playwright/test')

// BASE_URL must be provided — no fallback to avoid silently targeting a
// protected preview URL and getting confusing auth/timeout failures.
const baseURL = process.env.BASE_URL
if (!baseURL) {
  throw new Error('BASE_URL environment variable is required. Example: BASE_URL=https://your-deploy.vercel.app')
}

// Optional: set VERCEL_BYPASS_SECRET to bypass Vercel Deployment Protection.
// https://vercel.com/docs/security/deployment-protection/methods-to-bypass-deployment-protection
const extraHTTPHeaders = process.env.VERCEL_BYPASS_SECRET
  ? { 'x-vercel-protection-bypass': process.env.VERCEL_BYPASS_SECRET }
  : {}

module.exports = defineConfig({
  testDir: './e2e',
  testMatch: '**/*.spec.cjs',
  // Vercel cold starts can take 10-20 s; give each test enough headroom.
  timeout: 60000,
  // Each navigation gets up to 20 s before Playwright times out.
  use: {
    baseURL,
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15000,
    navigationTimeout: 20000,
    extraHTTPHeaders,
    // In local dev the pre-cached binary is used; in CI let Playwright resolve it.
    ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
      ? { launchOptions: { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH } }
      : !process.env.CI
        ? { launchOptions: { executablePath: '/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome' } }
        : {}),
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
