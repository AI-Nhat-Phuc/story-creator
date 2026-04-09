// @ts-check
const { defineConfig, devices } = require('@playwright/test')
const fs = require('fs')

// Ensure Playwright finds its browsers without downloading new ones.
// /opt/pw-browsers contains pre-installed Playwright browser builds for this environment.
if (!process.env.PLAYWRIGHT_BROWSERS_PATH) {
  if (fs.existsSync('/opt/pw-browsers')) {
    process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/pw-browsers'
  }
}

// Resolve the correct chromium headless-shell executable path for environments
// where the browsers are cached at a non-default location (/root/.cache/ms-playwright).
// Only probes the NEW headless-shell format (Playwright ≥1.46):
//   chromium_headless_shell-NNN/chrome-headless-shell-linux64/chrome-headless-shell
// When PLAYWRIGHT_BROWSERS_PATH is already set (e.g. /opt/pw-browsers), Playwright
// resolves its own browser paths and this function returns undefined (no override).
function resolveChromiumExecutable() {
  // If PLAYWRIGHT_BROWSERS_PATH is set, let Playwright handle browser discovery
  if (process.env.PLAYWRIGHT_BROWSERS_PATH) return undefined

  const candidates = [
    // /root/.cache/ms-playwright/<latest headless shell>/
    ...(() => {
      try {
        const base = '/root/.cache/ms-playwright'
        return fs.readdirSync(base)
          .filter(d => d.startsWith('chromium_headless_shell-'))
          .map(d => `${base}/${d}/chrome-headless-shell-linux64/chrome-headless-shell`)
      } catch { return [] }
    })(),
  ]
  return candidates.find(p => { try { return fs.existsSync(p) } catch { return false } })
}

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
  globalSetup: './e2e/global-setup.cjs',
  // In CI emit JSON so the workflow can parse failures and post a PR comment.
  reporter: process.env.CI
    ? [['list'], ['json', { outputFile: 'test-results/results.json' }], ['html', { open: 'never' }]]
    : [['list'], ['html', { open: 'never' }]],
  // Auto-start servers when running locally (skipped in CI where BASE_URL is pre-deployed)
  ...(!process.env.CI && !process.env.BASE_URL ? {
    webServer: [
      {
        // React frontend (Vite)
        command: 'npm run dev',
        url: 'http://localhost:3000',
        reuseExistingServer: true,
        timeout: 30000,
      },
      {
        // Flask API backend
        command: 'python ../api/main.py -i api',
        url: 'http://localhost:5000/api/health',
        reuseExistingServer: true,
        timeout: 30000,
      },
    ],
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
    // Resolve chromium executable: env var > auto-probe > default Playwright resolution.
    ...(() => {
      const path = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || (!process.env.CI && resolveChromiumExecutable())
      return path ? { launchOptions: { executablePath: path } } : {}
    })(),
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
