"use client"

import { useMemo } from "react"
import { detectLanguage } from "@/lib/language"

interface DiffLine {
  type: "add" | "remove" | "context" | "hunk-header"
  content: string
  oldLineNum?: number
  newLineNum?: number
}

interface DiffViewerProps {
  patch: string
  filename: string
  viewMode: "unified" | "split"
}

function parsePatch(patch: string): DiffLine[] {
  if (!patch) return []
  const lines: DiffLine[] = []
  let oldLine = 0
  let newLine = 0

  for (const line of patch.split("\n")) {
    if (line.startsWith("@@")) {
      // Parse hunk header
      const match = line.match(/@@ -(\d+)(?:,\d+)? \+(\d+)/)
      if (match) {
        oldLine = parseInt(match[1], 10)
        newLine = parseInt(match[2], 10)
      }
      lines.push({ type: "hunk-header", content: line })
    } else if (line.startsWith("+") && !line.startsWith("+++")) {
      lines.push({ type: "add", content: line.slice(1), newLineNum: newLine++ })
    } else if (line.startsWith("-") && !line.startsWith("---")) {
      lines.push({ type: "remove", content: line.slice(1), oldLineNum: oldLine++ })
    } else if (line.startsWith(" ")) {
      lines.push({ type: "context", content: line.slice(1), oldLineNum: oldLine++, newLineNum: newLine++ })
    }
  }
  return lines
}

function LineNumber({ n }: { n?: number }) {
  return (
    <td className="select-none w-12 pr-3 text-right text-xs text-muted-foreground/60 font-mono border-r border-border/40">
      {n ?? ""}
    </td>
  )
}

export function DiffViewer({ patch, filename, viewMode }: DiffViewerProps) {
  const lines = useMemo(() => parsePatch(patch), [patch])
  const language = detectLanguage(filename)

  if (!patch || lines.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground text-sm">
        No diff available for this file.
      </div>
    )
  }

  if (viewMode === "split") {
    const leftLines = lines.filter(l => l.type !== "add")
    const rightLines = lines.filter(l => l.type !== "remove")

    return (
      <div className="flex gap-0 overflow-x-auto font-mono text-xs">
        <div className="flex-1 min-w-0 border-r border-border">
          <table className="w-full border-collapse" role="table" aria-label="Removed lines">
            <tbody>
              {leftLines.map((line, i) => (
                <tr key={i} className={line.type === "remove" ? "bg-red-950/30" : line.type === "hunk-header" ? "bg-muted/50" : ""}>
                  <LineNumber n={line.oldLineNum} />
                  <td className="px-3 py-0.5 whitespace-pre overflow-hidden text-ellipsis max-w-0" style={{ width: "100%" }}>
                    <span className={line.type === "remove" ? "text-red-400" : "text-foreground"}>{line.content}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex-1 min-w-0">
          <table className="w-full border-collapse" role="table" aria-label="Added lines">
            <tbody>
              {rightLines.map((line, i) => (
                <tr key={i} className={line.type === "add" ? "bg-green-950/30" : line.type === "hunk-header" ? "bg-muted/50" : ""}>
                  <LineNumber n={line.newLineNum} />
                  <td className="px-3 py-0.5 whitespace-pre overflow-hidden text-ellipsis max-w-0" style={{ width: "100%" }}>
                    <span className={line.type === "add" ? "text-green-400" : "text-foreground"}>{line.content}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  // Unified view
  return (
    <div className="overflow-x-auto font-mono text-xs">
      <table className="w-full border-collapse" role="table" aria-label="Unified diff">
        <tbody>
          {lines.map((line, i) => {
            const rowClass =
              line.type === "add" ? "bg-green-950/30" :
              line.type === "remove" ? "bg-red-950/30" :
              line.type === "hunk-header" ? "bg-muted/50" : ""
            const textClass =
              line.type === "add" ? "text-green-400" :
              line.type === "remove" ? "text-red-400" :
              line.type === "hunk-header" ? "text-blue-400" : "text-foreground"
            const gutter =
              line.type === "add" ? "+" :
              line.type === "remove" ? "-" :
              line.type === "hunk-header" ? "@" : " "

            return (
              <tr key={i} className={rowClass} role="row">
                <LineNumber n={line.oldLineNum} />
                <LineNumber n={line.newLineNum} />
                <td className="w-4 text-center text-muted-foreground/60 select-none">{gutter}</td>
                <td className="px-3 py-0.5 whitespace-pre overflow-hidden text-ellipsis max-w-0" style={{ width: "100%" }} role="cell">
                  <span className={textClass}>{line.content}</span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
