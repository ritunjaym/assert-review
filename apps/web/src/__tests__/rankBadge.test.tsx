import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { RankBadge } from "@/components/rank-badge"

describe("RankBadge", () => {
  it("renders rank number when provided", () => {
    render(<RankBadge file={{ rank: 1, finalScore: 0.9 }} />)
    expect(screen.getByText("#1")).toBeTruthy()
  })

  it("renders score when no rank", () => {
    render(<RankBadge file={{ finalScore: 0.75 }} />)
    expect(screen.getByText("0.75")).toBeTruthy()
  })

  it("has aria-label with score", () => {
    render(<RankBadge file={{ finalScore: 0.85, rank: 2 }} />)
    const el = screen.getByLabelText(/ML score/)
    expect(el).toBeTruthy()
  })

  it("shows tooltip with score breakdown", () => {
    render(<RankBadge file={{ rank: 1, finalScore: 0.9, rerankerScore: 0.85, retrievalScore: 0.95 }} />)
    // Tooltip is in DOM but hidden via CSS
    expect(screen.getByText("ML Score Breakdown")).toBeTruthy()
  })
})
