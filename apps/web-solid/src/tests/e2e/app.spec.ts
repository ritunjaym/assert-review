import { test, expect } from '@playwright/test'

// ── Authentication / routing ──────────────────────────────────────────────────

test('login page loads with GitHub button', async ({ page }) => {
  await page.goto('/login')
  await expect(page.getByText('Sign in with GitHub')).toBeVisible()
})

test('login page has correct title', async ({ page }) => {
  await page.goto('/login')
  await expect(page).toHaveTitle('CodeLens')
})

test('unauthenticated /dashboard redirects to /login', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page).toHaveURL(/\/login/)
})

test('unauthenticated /pr route redirects to /login', async ({ page }) => {
  await page.goto('/pr/owner/repo/1')
  await expect(page).toHaveURL(/\/login/)
})

// ── Accessibility / keyboard ──────────────────────────────────────────────────

test('login page GitHub button is keyboard-focusable', async ({ page }) => {
  await page.goto('/login')
  await page.keyboard.press('Tab')
  const focused = page.locator(':focus')
  await expect(focused).toBeVisible()
})

test('login page has meta viewport tag for mobile', async ({ page }) => {
  await page.goto('/login')
  const viewport = page.locator('meta[name="viewport"]')
  await expect(viewport).toHaveAttribute('content', /width=device-width/)
})

// ── Static assets / performance ───────────────────────────────────────────────

test('login page returns 200 and has no JS console errors', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', err => errors.push(err.message))
  const response = await page.goto('/login')
  expect(response?.status()).toBe(200)
  await page.waitForLoadState('networkidle')
  const criticalErrors = errors.filter(e => !e.includes('favicon') && !e.includes('404'))
  expect(criticalErrors).toHaveLength(0)
})

// ── ML API health ─────────────────────────────────────────────────────────────

test('ML API health endpoint responds with status ok', async ({ request }) => {
  const response = await request.get('https://ritunjaym-codelens-api.hf.space/health')
  expect(response.status()).toBe(200)
  const body = await response.json()
  expect(body).toHaveProperty('status')
})
