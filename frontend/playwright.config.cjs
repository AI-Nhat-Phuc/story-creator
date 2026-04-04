// @ts-check
const { defineConfig, devices } = require('@playwright/test')
const fs = require('fs')

// Resolve the correct chromium headless shell executable path.
// In this dev environment, the binary may live under /root/.cache/ms-playwright
// instead of /opt/pw-browsers (the default PLAYWRIGHT_BROWSERS_PATH).
// We probe both locations so the config works across sessions without manual symlinks.
function resolveChromiumExecutable() {
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
    // /opt/pw-browsers/<latest headless shell>/
    ...(() => {
      try {
        const base = '/opt/pw-browsers'
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
