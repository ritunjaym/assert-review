export interface PRFile {
  filename: string;
  status: 'added' | 'removed' | 'modified' | 'renamed';
  additions: number;
  deletions: number;
  patch?: string;
}

export interface FileInput {
  filename: string;
  patch?: string;
  additions: number;
  deletions: number;
}

export interface RankedFile {
  filename: string;
  rank: number;
  reranker_score: number;
  retrieval_score: number;
  final_score: number;
  explanation: string;
}

export interface RankingResponse {
  pr_id: string;
  ranked_files: RankedFile[];
  processing_ms: number;
}

export interface ClusterOutput {
  cluster_id: number;
  label: string;
  files: string[];
  coherence: number;
}

export interface ClusterResponse {
  pr_id: string;
  groups: ClusterOutput[];
}

export interface RetrievalResult {
  score: number;
  filename: string;
  importance: number;
  hunk_preview: string;
}
