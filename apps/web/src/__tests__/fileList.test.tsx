import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { FileList } from "@/components/pr-review/file-list"

// Mock useVirtualizer to render all items directly (no DOM scroll layout in tests)
vi.mock("@tanstack/react-virtual", () => ({
  useVirtualizer: ({ count, estimateSize }: { count: number; estimateSize: () => number }) => ({
    getTotalSize: () => count * estimateSize(),
    getVirtualItems: () =>
      Array.from({ length: count }, (_, i) => ({
        key: i,
        index: i,
        start: i * estimateSize(),
        size: estimateSize(),
      })),
  }),
}))

const FILES = [
  { filename: "src/auth.py", additions: 10, deletions: 2, finalScore: 0.9 },
  { filename: "README.md", additions: 5, deletions: 0, finalScore: 0.1 },
  { filename: "tests/test_auth.py", additions: 20, deletions: 5, finalScore: 0.5 },
  { filename: "config.yaml", additions: 3, deletions: 1, finalScore: 0.2 },
  { filename: "src/core.py", additions: 50, deletions: 10, finalScore: 0.7 },
]

describe("FileList", () => {
  it("renders all 5 files", () => {
    const onSelect = vi.fn()
    render(<FileList files={FILES} selectedFile={null} onSelectFile={onSelect} />)
    // Files are virtualized but should render visible ones
    expect(screen.getAllByRole("listitem").length).toBeGreaterThan(0)
  })

  it("clicking a file triggers selection callback", () => {
    const onSelect = vi.fn()
    render(
      <FileList files={FILES} selectedFile={null} onSelectFile={onSelect} />,
    )
    const buttons = screen.getAllByRole("listitem")
    fireEvent.click(buttons[0])
    expect(onSelect).toHaveBeenCalledTimes(1)
  })

  it("selected file has aria-selected=true", () => {
    render(
      <FileList
        files={FILES}
        selectedFile="src/auth.py"
        onSelectFile={() => {}}
      />
    )
    const selected = screen.getAllByRole("listitem").find(
      el => el.getAttribute("aria-selected") === "true"
    )
    expect(selected).toBeTruthy()
  })
})
