import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir: './src/tests/e2e',
  use: { baseURL: 'https://codelens-solid.vercel.app' },
  timeout: 15000,
})
