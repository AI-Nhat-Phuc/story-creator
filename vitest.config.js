import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'node:path'

// Vitest config extracted from the old vite.config.js. Keeps the same test
// environment + setup; uses @vitejs/plugin-react for JSX transform (vitest
// depends on vite internally even though the dev server is now Next.js).
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.js',
    exclude: ['**/node_modules/**', '**/e2e/**', '**/.next/**'],
  },
})
