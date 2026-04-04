import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.js',
  },
  plugins: [react()],
  // Đọc .env từ root project thay vì frontend/
  envDir: '../',
  // Expose GOOGLE_* env vars cho frontend (ngoài VITE_ mặc định)
  envPrefix: ['VITE_', 'GOOGLE_'],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist', // Vercel expects build output in 'dist'
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // Pin the JSX runtime to vendor-react so it never ends up in vendor-xyflow.
          // Without this, Rollup can assign react/jsx-runtime to the xyflow chunk
          // (because @xyflow/react is the first package processed that needs it),
          // which causes "Tag is not defined" ReferenceErrors in production when
          // chunk evaluation order differs from the local build.
          'vendor-react': [
            'react',
            'react-dom',
            'react-router-dom',
            'react/jsx-runtime',
            'react/jsx-dev-runtime',
          ],
          'vendor-xyflow': ['@xyflow/react'],
          'vendor-ui': ['@heroicons/react', 'axios'],
        },
      },
    },
  }
})
