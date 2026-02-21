import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { ClusterPanel } from "@/components/cluster-panel"

const CLUSTERS = [
  { cluster_id: 0, label: "auth middleware", files: ["src/auth.py", "src/middleware.py"], coherence: 0.92 },
  { cluster_id: 1, label: "test coverage", files: ["tests/test_auth.py"], coherence: 1.0 },
]

describe("ClusterPanel", () => {
  it("renders cluster labels", () => {
    render(<ClusterPanel clusters={CLUSTERS} selectedClusterId={null} onSelectCluster={() => {}} />)
    expect(screen.getByText("auth middleware")).toBeTruthy()
    expect(screen.getByText("test coverage")).toBeTruthy()
  })

  it("renders 'All files' option", () => {
    render(<ClusterPanel clusters={CLUSTERS} selectedClusterId={null} onSelectCluster={() => {}} />)
    expect(screen.getByText("All files")).toBeTruthy()
  })

  it("clicking cluster triggers callback with cluster id", () => {
    const onSelect = vi.fn()
    render(<ClusterPanel clusters={CLUSTERS} selectedClusterId={null} onSelectCluster={onSelect} />)
    fireEvent.click(screen.getByText("auth middleware"))
    expect(onSelect).toHaveBeenCalledWith(0)
  })

  it("clicking 'All files' clears filter", () => {
    const onSelect = vi.fn()
    render(<ClusterPanel clusters={CLUSTERS} selectedClusterId={0} onSelectCluster={onSelect} />)
    fireEvent.click(screen.getByText("All files"))
    expect(onSelect).toHaveBeenCalledWith(null)
  })

  it("shows empty state when no clusters", () => {
    render(<ClusterPanel clusters={[]} selectedClusterId={null} onSelectCluster={() => {}} />)
    expect(screen.getByText(/unavailable/i)).toBeTruthy()
  })

  it("shows file count in each cluster", () => {
    render(<ClusterPanel clusters={CLUSTERS} selectedClusterId={null} onSelectCluster={() => {}} />)
    expect(screen.getByText(/2 files/)).toBeTruthy()
    expect(screen.getByText(/1 files/)).toBeTruthy()
  })
})
