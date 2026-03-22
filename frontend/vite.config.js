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
  // Expose GOOGLE_* và FACEBOOK_* env vars cho frontend (ngoài VITE_ mặc định)
  envPrefix: ['VITE_', 'GOOGLE_', 'FACEBOOK_'],
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
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-xyflow': ['@xyflow/react'],
          'vendor-ui': ['@heroicons/react', 'axios'],
        },
      },
    },
  }
})
