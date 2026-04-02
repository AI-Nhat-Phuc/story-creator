// @ts-check
const { defineConfig, devices } = require('@playwright/test')

// Vercel Deployment Protection bypass:
// Set VERCEL_BYPASS_SECRET env var if the deployment URL is protected.
// See: https://vercel.com/docs/security/deployment-protection/methods-to-bypass-deployment-protection
const extraHTTPHeaders = process.env.VERCEL_BYPASS_SECRET
  ? { 'x-vercel-protection-bypass': process.env.VERCEL_BYPASS_SECRET }
  : {}

module.exports = defineConfig({
  testDir: './e2e',
  testMatch: '**/*.spec.cjs',
  timeout: 30000,
  retries: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.BASE_URL || 'https://story-creator-mxg40480n-nhat-phuc-phams-projects.vercel.app',
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    extraHTTPHeaders,
    launchOptions: {
      executablePath:
        process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH ||
        '/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome',
    },
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
