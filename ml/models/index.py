"""
FAISS index for dense retrieval over code hunks.
Uses IndexFlatIP (inner product = cosine sim on L2-normalized vectors).
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import NamedTuple

import numpy as np
from pydantic import BaseModel


class RetrievalResult(BaseModel):
    score: float
    filename: str
    importance: float
    hunk_preview: str
    pr_id: int = 0
    repo: str = ""


class PRIndex:
    """FAISS index wrapping embeddings + metadata for retrieval."""
    
    def __init__(self, dim: int = 768):
        self.dim = dim
        self._index = None
        self._metadata: list[dict] = []
    
    def _get_faiss(self):
        try:
            import faiss
            return faiss
        except ImportError as e:
            raise ImportError("faiss-cpu required: pip install faiss-cpu") from e
    
    def build(self, embeddings: np.ndarray, metadata: list[dict]) -> None:
        """Build FAISS index from embeddings + metadata list."""
        faiss = self._get_faiss()
        assert embeddings.shape[0] == len(metadata), "embeddings and metadata must match length"
        assert embeddings.shape[1] == self.dim, f"expected dim {self.dim}, got {embeddings.shape[1]}"
        
        emb = np.ascontiguousarray(embeddings.astype(np.float32))
        self._index = faiss.IndexFlatIP(self.dim)
        self._index.add(emb)
        self._metadata = list(metadata)
    
    def search(self, query: np.ndarray, k: int = 10) -> list[RetrievalResult]:
        """Search for top-k nearest neighbors."""
        if self._index is None:
            raise RuntimeError("Index not built. Call build() or load() first.")
        
        q = np.ascontiguousarray(query.reshape(1, -1).astype(np.float32))
        k = min(k, self._index.ntotal)
        if k == 0:
            return []
        
        scores, indices = self._index.search(q, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            meta = self._metadata[idx]
            results.append(RetrievalResult(
                score=float(score),
                filename=meta.get("filename", ""),
                importance=meta.get("importance_score", 0.0),
                hunk_preview=meta.get("hunk_preview", "")[:200],
                pr_id=meta.get("pr_id", 0),
                repo=meta.get("repo", ""),
            ))
        
        return sorted(results, key=lambda r: r.score, reverse=True)
    
    def save(self, path: str) -> None:
        """Save FAISS index + metadata to disk."""
        faiss = self._get_faiss()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(path))
        with open(str(path) + ".meta", "wb") as f:
            pickle.dump(self._metadata, f)
    
    def load(self, path: str) -> None:
        """Load FAISS index + metadata from disk."""
        faiss = self._get_faiss()
        self._index = faiss.read_index(str(path))
        with open(str(path) + ".meta", "rb") as f:
            self._metadata = pickle.load(f)
    
    @property
    def size(self) -> int:
        return self._index.ntotal if self._index else 0
