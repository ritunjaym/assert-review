from pydantic import BaseModel
from typing import Optional


class FileInput(BaseModel):
    filename: str
    patch: Optional[str] = None
    additions: int = 0
    deletions: int = 0


class RankedFile(BaseModel):
    filename: str
    rank: int
    reranker_score: float
    retrieval_score: float
    final_score: float
    explanation: str


class RankRequest(BaseModel):
    pr_id: str
    repo: str
    files: list[FileInput]


class RankResponse(BaseModel):
    pr_id: str
    ranked_files: list[RankedFile]
    processing_ms: int


class ClusterOutput(BaseModel):
    cluster_id: int
    label: str
    files: list[str]
    coherence: float


class ClusterRequest(BaseModel):
    pr_id: str
    files: list[FileInput]


class ClusterResponse(BaseModel):
    pr_id: str
    groups: list[ClusterOutput]


class RetrieveRequest(BaseModel):
    query_diff: str
    k: int = 10


class RetrieveResponse(BaseModel):
    results: list[dict]
