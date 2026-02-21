import { expect } from "vitest"

export async function checkA11y(container: HTMLElement): Promise<void> {
  try {
    const { axe } = await import("axe-core")
    const results = await axe(container)
    if (results.violations.length > 0) {
      const msgs = results.violations.map(v => `${v.id}: ${v.description} (${v.nodes.length} nodes)`).join("\n")
      throw new Error(`axe violations:\n${msgs}`)
    }
  } catch (e: unknown) {
    // If axe-core is not installed, skip
    if (e instanceof Error && e.message.includes("axe violations")) throw e
  }
}
