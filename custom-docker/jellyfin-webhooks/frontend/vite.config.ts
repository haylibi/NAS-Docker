import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // This ensures assets are loaded from /jellyfin-webhooks/assets/...
  base: '/jellyfin-webhooks/', 
  server: {
    // This proxy is for LOCAL development (npm run dev) only
    proxy: {
      '/jellyfin-webhooks/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})