import { test, expect } from "@playwright/test"

test.describe("Commenting", () => {
  test.skip("Can add inline comment on diff line", async ({ page }) => {
    // Skipped: requires auth session
    // Would hover gutter, click "+", type comment, submit
  })
})
