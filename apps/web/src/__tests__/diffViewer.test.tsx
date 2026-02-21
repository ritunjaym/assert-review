import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { DiffViewer } from "@/components/pr-review/diff-viewer"

const SIMPLE_PATCH = `@@ -1,5 +1,6 @@
 line1
 line2
-old_line
+new_line
+extra_line
 line4
 line5`

describe("DiffViewer", () => {
  it("renders unified diff with correct line types", () => {
    render(<DiffViewer patch={SIMPLE_PATCH} filename="test.py" viewMode="unified" />)
    expect(screen.getByText("new_line")).toBeTruthy()
    expect(screen.getByText("old_line")).toBeTruthy()
  })

  it("renders split mode with two tables", () => {
    render(<DiffViewer patch={SIMPLE_PATCH} filename="test.ts" viewMode="split" />)
    const tables = screen.getAllByRole("table")
    expect(tables.length).toBe(2)
  })

  it("shows empty state when no patch", () => {
    render(<DiffViewer patch="" filename="test.py" viewMode="unified" />)
    expect(screen.getByText(/No diff available/)).toBeTruthy()
  })

  it("renders context lines", () => {
    render(<DiffViewer patch={SIMPLE_PATCH} filename="test.py" viewMode="unified" />)
    expect(screen.getByText("line1")).toBeTruthy()
  })
})
