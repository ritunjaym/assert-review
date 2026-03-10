import { test, expect } from '@playwright/test'

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
