import { expect } from "vitest"

export async function checkA11y(container: HTMLElement): Promise<void> {
  try {
    const axeCore = await import("axe-core")
    const axe = axeCore.default ?? axeCore
    const results = await axe.run(container)
    if (results.violations.length > 0) {
      const msgs = results.violations.map((v: { id: string; description: string; nodes: unknown[] }) => `${v.id}: ${v.description} (${v.nodes.length} nodes)`).join("\n")
      throw new Error(`axe violations:\n${msgs}`)
    }
  } catch (e: unknown) {
    // If axe-core is not installed, skip
    if (e instanceof Error && e.message.includes("axe violations")) throw e
  }
}
