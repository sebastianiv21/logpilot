/// <reference types="vitest" />
import type { UserConfig } from 'vite'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
const config: UserConfig & { test?: import('vitest').InlineConfig } = {
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      // Optional: proxy /api to backend so dev can use VITE_API_BASE='' and path /api
      '/api': {
        target: process.env.VITE_API_BASE ?? 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api/, ''),
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    include: ['src/**/*.{test,spec}.{js,ts,jsx,tsx}', 'tests/**/*.{test,spec}.{js,ts,jsx,tsx}'],
  },
}
export default defineConfig(config)
