"""
ML service singleton — lazy-loads models on first request.
Returns {"error": "model_not_loaded", "status": "unavailable"} with 503 if models not ready.
"""
from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Add project root to path so ml/ package is importable
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


class MLService:
    """Singleton that lazy-loads ML models."""

    def __init__(self):
        self._reranker: Any = None
        self._index: Any = None
        self._reranker_loaded = False
        self._index_loaded = False

    def _load_reranker(self) -> None:
        if self._reranker_loaded:
            return
        try:
            from ml.models.reranker import Reranker
            t0 = time.time()
            self._reranker = Reranker()
            logger.info(f"Reranker loaded in {time.time()-t0:.2f}s (zero_shot={self._reranker._zero_shot})")
        except Exception as e:
            logger.warning(f"Could not load reranker: {e}")
            self._reranker = None
        self._reranker_loaded = True

    def _load_index(self) -> None:
        if self._index_loaded:
            return
        try:
            from ml.models.index import PRIndex

            # Detect Vercel environment
            if os.environ.get("VERCEL"):
                index_path = Path("/tmp/hunk_index.faiss")
            else:
                index_path = _PROJECT_ROOT / "ml" / "models" / "faiss" / "hunk_index.faiss"

            if index_path.exists():
                t0 = time.time()
                self._index = PRIndex()
                self._index.load(str(index_path))
                logger.info(f"FAISS index loaded ({self._index.size} vectors) in {time.time()-t0:.2f}s")
            else:
                logger.info(f"No FAISS index found at {index_path}. Retrieval will be unavailable.")
                self._index = None
        except Exception as e:
            logger.warning(f"Could not load FAISS index: {e}")
            self._index = None
        self._index_loaded = True

    def rank_pr(self, pr_id: str, repo: str, files: list[dict]) -> dict:
        """Rank files in a PR by importance."""
        self._load_reranker()
        self._load_index()

        if not files:
            return {"pr_id": pr_id, "ranked_files": [], "processing_ms": 0}

        t0 = time.time()

        # Build texts for scoring
        texts = [
            f"<file>{f.get('filename','')}</file>"
            f"<diff>{(f.get('patch','') or '')[:512]}</diff>"
            for f in files
        ]

        # Reranker scores
        if self._reranker:
            reranker_scores = self._reranker.score(texts)
        else:
            reranker_scores = [0.5] * len(files)

        # Retrieval scores (if index available)
        retrieval_scores = [0.0] * len(files)
        if self._index:
            try:
                from ml.models.embedder import CodeEmbedder
                embedder = CodeEmbedder()
                for i, text in enumerate(texts):
                    emb = embedder.embed_single(text)
                    results = self._index.search(emb, k=3)
                    retrieval_scores[i] = float(results[0].score) if results else 0.0
            except Exception as e:
                logger.warning(f"Retrieval scoring failed: {e}")

        # Blend scores (60% reranker, 40% retrieval)
        ranked_files = []
        for i, f in enumerate(files):
            r_score = reranker_scores[i]
            ret_score = retrieval_scores[i]
            final = 0.6 * r_score + 0.4 * ret_score

            # Build explanation
            parts = []
            fname = f.get("filename", "")
            if any(kw in fname for kw in ["auth", "crypto", "token", "secret", "password"]):
                parts.append("security-sensitive path")
            if (f.get("additions", 0) + f.get("deletions", 0)) > 100:
                parts.append("large change")
            if any(fname.startswith(p) for p in ["src/", "lib/", "core/"]):
                parts.append("core source")
            explanation = (", ".join(parts) + " → high priority") if parts else "standard change"

            ranked_files.append({
                "filename": fname,
                "reranker_score": round(r_score, 4),
                "retrieval_score": round(ret_score, 4),
                "final_score": round(final, 4),
                "explanation": explanation,
            })

        # Sort and add rank
        ranked_files.sort(key=lambda x: x["final_score"], reverse=True)
        for rank, rf in enumerate(ranked_files, 1):
            rf["rank"] = rank

        processing_ms = int((time.time() - t0) * 1000)
        return {
            "pr_id": pr_id,
            "ranked_files": ranked_files,
            "processing_ms": processing_ms,
        }

    def cluster_pr(self, pr_id: str, files: list[dict]) -> dict:
        """Cluster PR files into semantic groups."""
        t0 = time.time()

        try:
            from ml.models.clusterer import SemanticClusterer
            from ml.models.embedder import CodeEmbedder
            import numpy as np

            if not files:
                return {"pr_id": pr_id, "groups": []}

            texts = [
                f"// {f.get('filename','')}\n{(f.get('patch','') or '')[:256]}"
                for f in files
            ]

            embedder = CodeEmbedder()
            embeddings = embedder.embed(texts)
            metadata = [{"filename": f.get("filename", "")} for f in files]

            clusterer = SemanticClusterer()
            clusters = clusterer.cluster(embeddings, metadata)

            groups = [
                {
                    "cluster_id": c.cluster_id,
                    "label": c.label,
                    "files": c.files,
                    "coherence": c.coherence,
                }
                for c in clusters
            ]

        except Exception as e:
            logger.warning(f"Clustering failed: {e}")
            groups = [
                {"cluster_id": i, "label": f.get("filename","").split("/")[-1],
                 "files": [f.get("filename","")], "coherence": 1.0}
                for i, f in enumerate(files)
            ]

        return {"pr_id": pr_id, "groups": groups}

    def retrieve(self, query_diff: str, k: int = 10) -> dict:
        """Retrieve similar historical hunks."""
        self._load_index()

        if not self._index:
            return {"results": [], "error": "index_not_loaded"}

        try:
            from ml.models.embedder import CodeEmbedder
            embedder = CodeEmbedder()
            query_emb = embedder.embed_single(query_diff)
            results = self._index.search(query_emb, k=k)
            return {
                "results": [r.model_dump() for r in results]
            }
        except Exception as e:
            logger.warning(f"Retrieval failed: {e}")
            return {"results": [], "error": str(e)}


# Global singleton
_ml_service: MLService | None = None


def get_ml_service() -> MLService:
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service
