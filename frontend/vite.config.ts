import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const strip = (p: string) => p.replace(/^\/api/, '')

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/api/auth':          { target: 'http://127.0.0.1:8001', rewrite: strip },
      '/api/chat':          { target: 'http://127.0.0.1:8002', rewrite: strip },
      '/api/conversations': { target: 'http://127.0.0.1:8004', rewrite: strip },
    },
  },
})