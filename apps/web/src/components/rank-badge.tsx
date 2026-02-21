"use client"

interface RankBadgeProps {
  file: {
    rank?: number
    finalScore?: number
    rerankerScore?: number
    retrievalScore?: number
    explanation?: string
  }
}

const TIER_CLASSES = [
  "bg-red-500/20 text-red-400 border-red-500/40",      // score >= 0.8
  "bg-orange-500/20 text-orange-400 border-orange-500/40", // 0.6-0.8
  "bg-yellow-500/20 text-yellow-400 border-yellow-500/40", // 0.4-0.6
  "bg-blue-500/20 text-blue-400 border-blue-500/40",   // 0.2-0.4
  "bg-muted text-muted-foreground border-border",       // < 0.2
]

function getTierClass(score: number): string {
  if (score >= 0.8) return TIER_CLASSES[0]
  if (score >= 0.6) return TIER_CLASSES[1]
  if (score >= 0.4) return TIER_CLASSES[2]
  if (score >= 0.2) return TIER_CLASSES[3]
  return TIER_CLASSES[4]
}

export function RankBadge({ file }: RankBadgeProps) {
  const score = file.finalScore ?? 0
  const tierClass = getTierClass(score)

  return (
    <div className="relative group/badge inline-block">
      <span
        className={`inline-flex items-center px-1.5 py-0.5 rounded border text-[10px] font-mono cursor-help ${tierClass}`}
        aria-label={`ML score: ${score.toFixed(2)}`}
      >
        {file.rank != null ? `#${file.rank}` : score.toFixed(2)}
      </span>
      
      {/* Tooltip */}
      <div className="absolute left-0 top-full mt-1 z-50 hidden group-hover/badge:block w-56 bg-popover border border-border rounded-lg shadow-lg p-3 text-xs">
        <div className="font-semibold mb-2">ML Score Breakdown</div>
        <table className="w-full" role="table">
          <tbody>
            <tr role="row">
              <td className="text-muted-foreground py-0.5">Reranker</td>
              <td className="text-right font-mono">{(file.rerankerScore ?? 0).toFixed(4)}</td>
            </tr>
            <tr role="row">
              <td className="text-muted-foreground py-0.5">Retrieval</td>
              <td className="text-right font-mono">{(file.retrievalScore ?? 0).toFixed(4)}</td>
            </tr>
            <tr role="row" className="border-t border-border">
              <td className="text-muted-foreground py-0.5 pt-1">Final</td>
              <td className="text-right font-mono font-semibold">{score.toFixed(4)}</td>
            </tr>
          </tbody>
        </table>
        {file.explanation && (
          <p className="mt-2 text-muted-foreground italic">{file.explanation}</p>
        )}
      </div>
    </div>
  )
}
