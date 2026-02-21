import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { PRCard, PRCardData } from "@/components/pr-card"
import { MLUnavailableBanner } from "@/components/ml-unavailable-banner"
import { ClusterPanel } from "@/components/cluster-panel"
import { KeyboardShortcutsModal } from "@/components/keyboard-shortcuts-modal"
import { CommandPalette } from "@/components/command-palette"

const mockPR: PRCardData = {
  number: 1, title: "Fix bug", repo: "myrepo", owner: "myuser",
  author: "alice", authorAvatar: "https://github.com/alice.png",
  createdAt: new Date().toISOString(), fileCount: 3,
  additions: 10, deletions: 5, isDraft: false,
}

describe("Accessibility", () => {
  it("PRCard has no missing alt texts", () => {
    render(<PRCard pr={mockPR} />)
    const imgs = document.querySelectorAll("img")
    imgs.forEach(img => {
      expect(img.getAttribute("alt")).toBeTruthy()
    })
  })

  it("MLUnavailableBanner has role=alert", () => {
    render(<MLUnavailableBanner />)
    expect(screen.getByRole("alert")).toBeTruthy()
  })

  it("ClusterPanel buttons have accessible content", () => {
    const clusters = [{ cluster_id: 0, label: "auth", files: ["src/auth.py"], coherence: 0.9 }]
    render(<ClusterPanel clusters={clusters} selectedClusterId={null} onSelectCluster={() => {}} />)
    const buttons = screen.getAllByRole("button")
    buttons.forEach(btn => {
      // Button should have text content or aria-label
      expect(btn.textContent?.trim().length || btn.getAttribute("aria-label")).toBeTruthy()
    })
  })

  it("KeyboardShortcutsModal has dialog role", () => {
    render(<KeyboardShortcutsModal open={true} onClose={() => {}} />)
    expect(screen.getByRole("dialog")).toBeTruthy()
  })

  it("CommandPalette has dialog role", () => {
    render(<CommandPalette open={true} onClose={() => {}} items={[]} />)
    expect(screen.getByRole("dialog")).toBeTruthy()
  })
})
