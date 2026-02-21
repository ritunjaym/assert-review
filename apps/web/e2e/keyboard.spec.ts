import { test, expect } from "@playwright/test"

test.describe("Keyboard Navigation", () => {
  test.skip("Command palette opens with Cmd+K", async ({ page }) => {
    // Skipped: requires auth session
    // await page.keyboard.press("Meta+k")
    // await expect(page.locator('[role="dialog"]')).toBeVisible()
  })
})
