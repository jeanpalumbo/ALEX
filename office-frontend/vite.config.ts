import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Dev-only proxy to the real FastAPI console backend, so the browser never
// needs CORS configured and the console token stays off any public origin.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8420',
        changeOrigin: true,
      },
    },
  },
})
