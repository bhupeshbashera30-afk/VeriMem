import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/sessions': 'http://localhost:8000',
      '/memories': 'http://localhost:8000',
      '/policies': 'http://localhost:8000',
      '/users': 'http://localhost:8000',
      '/audit': 'http://localhost:8000',
      '/pipeline': 'http://localhost:8000'
    }
  }
})
