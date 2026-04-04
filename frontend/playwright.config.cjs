// @ts-check
const { defineConfig, devices } = require('@playwright/test')

// In CI BASE_URL must be set explicitly (the deployed Vercel URL).
// In local dev it defaults to localhost so you can run without extra config.
const baseURL = process.env.BASE_URL
  || (process.env.CI ? (() => { throw new Error('BASE_URL is required in CI') })() : 'http://localhost:3000')

// Optional: set VERCEL_BYPASS_SECRET to bypass Vercel Deployment Protection.
// https://vercel.com/docs/security/deployment-protection/methods-to-bypass-deployment-protection
const extraHTTPHeaders = process.env.VERCEL_BYPASS_SECRET
  ? { 'x-vercel-protection-bypass': process.env.VERCEL_BYPASS_SECRET }
  : {}

module.exports = defineConfig({
  testDir: './e2e',
  testMatch: '**/*.spec.cjs',
  // Auto-start the dev server when running locally (skipped in CI where BASE_URL is pre-deployed)
  ...(!process.env.CI && !process.env.BASE_URL ? {
    webServer: {
      command: 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: true,   // reuse if already running (avoids double-start)
      timeout: 30000,
    },
  } : {}),
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
        ? {} // let Playwright resolve the local binary automatically
        : {}),
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
