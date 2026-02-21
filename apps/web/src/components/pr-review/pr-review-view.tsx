"use client"

import { useState, useMemo, useCallback } from "react"
import { FileList, FileListItem } from "./file-list"
import { DiffViewer } from "./diff-viewer"
import { ClusterPanel } from "@/components/cluster-panel"
import { RankBadge } from "@/components/rank-badge"
import { MLUnavailableBanner } from "@/components/ml-unavailable-banner"

interface RankedFileData {
  filename: string
  rank: number
  reranker_score: number
  retrieval_score: number
  final_score: number
  explanation: string
}

interface ClusterData {
  cluster_id: number
  label: string
  files: string[]
  coherence: number
}

interface PRFile {
  filename: string
  additions: number
  deletions: number
  patch?: string
}

interface PRReviewViewProps {
  files: PRFile[]
  rankingData: { ranked_files: RankedFileData[] } | null
  clusterData: { groups: ClusterData[] } | null
  prTitle: string
}

export function PRReviewView({ files, rankingData, clusterData, prTitle }: PRReviewViewProps) {
  const [selectedFile, setSelectedFile] = useState<string | null>(files[0]?.filename ?? null)
  const [viewMode, setViewMode] = useState<"unified" | "split">("unified")
  const [reviewOrder, setReviewOrder] = useState(false)
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null)

  const mlUnavailable = !rankingData && !clusterData

  // Merge ranking data into files
  const enrichedFiles = useMemo<FileListItem[]>(() => {
    const rankMap = new Map(
      rankingData?.ranked_files.map(r => [r.filename, r]) ?? []
    )
    const clusterMap = new Map<string, { id: number; label: string }>()
    clusterData?.groups.forEach(g => {
      g.files.forEach(f => clusterMap.set(f, { id: g.cluster_id, label: g.label }))
    })

    const enriched = files.map(f => ({
      ...f,
      rank: rankMap.get(f.filename)?.rank,
      finalScore: rankMap.get(f.filename)?.final_score,
      rerankerScore: rankMap.get(f.filename)?.reranker_score,
      retrievalScore: rankMap.get(f.filename)?.retrieval_score,
      explanation: rankMap.get(f.filename)?.explanation,
      clusterId: clusterMap.get(f.filename)?.id,
      clusterLabel: clusterMap.get(f.filename)?.label,
    }))

    if (reviewOrder && rankingData) {
      return [...enriched].sort((a, b) => (a.rank ?? 999) - (b.rank ?? 999))
    }
    return enriched
  }, [files, rankingData, clusterData, reviewOrder])

  const selectedFileData = useMemo(
    () => files.find(f => f.filename === selectedFile),
    [files, selectedFile]
  )

  const selectedFileRank = useMemo(
    () => enrichedFiles.find(f => f.filename === selectedFile),
    [enrichedFiles, selectedFile]
  )

  return (
    <div className="flex h-[calc(100vh-57px)] overflow-hidden">
      {/* Left panel: file list + cluster panel */}
      <div className="w-72 border-r border-border flex flex-col shrink-0">
        {/* Toolbar */}
        <div className="px-3 py-2 border-b border-border flex items-center gap-2">
          <button
            className={`text-xs px-2 py-1 rounded transition-colors ${reviewOrder ? "bg-primary text-primary-foreground" : "hover:bg-muted"}`}
            onClick={() => setReviewOrder(v => !v)}
            aria-pressed={reviewOrder}
          >
            Review Order
          </button>
          <button
            className={`text-xs px-2 py-1 rounded transition-colors ${viewMode === "split" ? "bg-primary text-primary-foreground" : "hover:bg-muted"}`}
            onClick={() => setViewMode(v => v === "unified" ? "split" : "unified")}
          >
            {viewMode === "unified" ? "Split" : "Unified"}
          </button>
        </div>

        {/* Cluster panel */}
        {clusterData && (
          <div className="border-b border-border">
            <ClusterPanel
              clusters={clusterData.groups}
              selectedClusterId={selectedCluster}
              onSelectCluster={setSelectedCluster}
            />
          </div>
        )}

        {/* File list */}
        <div className="flex-1 overflow-hidden">
          <FileList
            files={enrichedFiles}
            selectedFile={selectedFile}
            onSelectFile={setSelectedFile}
            filterClusterId={selectedCluster}
          />
        </div>
      </div>

      {/* Right panel: diff viewer */}
      <div className="flex-1 overflow-y-auto">
        {mlUnavailable && (
          <div className="px-6 pt-4">
            <MLUnavailableBanner />
          </div>
        )}

        {selectedFileData ? (
          <div className="p-4">
            {/* File header */}
            <div className="flex items-center gap-3 mb-4 pb-3 border-b border-border">
              {selectedFileRank?.finalScore != null && (
                <RankBadge file={{
                  rank: selectedFileRank.rank,
                  finalScore: selectedFileRank.finalScore,
                  rerankerScore: selectedFileRank.rerankerScore,
                  retrievalScore: selectedFileRank.retrievalScore,
                  explanation: selectedFileRank.explanation,
                }} />
              )}
              <span className="font-mono text-sm font-medium">{selectedFileData.filename}</span>
              <span className="ml-auto flex items-center gap-2 text-xs">
                <span className="text-green-500">+{selectedFileData.additions}</span>
                <span className="text-red-500">-{selectedFileData.deletions}</span>
              </span>
            </div>

            <DiffViewer
              patch={selectedFileData.patch ?? ""}
              filename={selectedFileData.filename}
              viewMode={viewMode}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
            Select a file to view its diff
          </div>
        )}
      </div>
    </div>
  )
}
