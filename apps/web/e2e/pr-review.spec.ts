import { test, expect } from "@playwright/test"

test.describe("PR Review", () => {
  test.skip("Navigate to PR view and verify file list renders", async ({ page }) => {
    // Skipped: requires real GitHub OAuth session
    // In CI: use mock auth + mock GitHub API
    await page.goto("/pr/microsoft/vscode/200000")
    await expect(page.locator('[role="list"]')).toBeVisible()
  })
})
