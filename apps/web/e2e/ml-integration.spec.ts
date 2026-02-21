import { test, expect } from "@playwright/test"

test.describe("ML Integration", () => {
  test.skip("ML rank badges appear when API responds", async ({ page }) => {
    // Skipped: requires running ML API
    // Would mock: page.route("**/rank", ...)
  })
})
