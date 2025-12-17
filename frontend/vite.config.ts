import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 8088,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL?.replace('/api/v1', '') || 'http://localhost:8001',
        changeOrigin: true,
      },
      '/storage': {
        target: process.env.VITE_API_URL?.replace('/api/v1', '') || 'http://localhost:8001',
        changeOrigin: true,
      }
    }
  }
})

