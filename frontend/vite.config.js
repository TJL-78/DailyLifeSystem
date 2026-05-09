import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/uploads': 'http://127.0.0.1:5000',
    }
  },
  build: {
    outDir: '../daily_activity_manager/static/vue',
    emptyOutDir: true,
  }
})
