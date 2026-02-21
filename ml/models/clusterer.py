"""
Semantic clustering of PR files using HDBSCAN.
Handles small PRs (< 4 files) with singleton fallback.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

import numpy as np
from pydantic import BaseModel


class Cluster(BaseModel):
    cluster_id: int
    label: str
    file_indices: list[int]
    files: list[str]
    coherence: float
    size: int


class GroupingResult(BaseModel):
    clusters: list[Cluster]
    file_cluster_map: dict[str, int]
    n_clusters: int
    noise_count: int


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "can", "this", "that", "these",
    "those", "it", "its", "as", "if", "not", "no", "nor", "so", "yet",
    "both", "either", "neither", "each", "few", "more", "most", "other",
    "some", "such", "than", "too", "very",
}


class SemanticClusterer:
    """Cluster file embeddings using HDBSCAN."""
    
    def __init__(self, min_cluster_size: int = 2, min_samples: int = 1):
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
    
    def cluster(self, embeddings: np.ndarray, metadata: list[dict]) -> list[Cluster]:
        """
        Cluster embeddings into semantic groups.
        
        Falls back to singletons if < 4 items.
        Noise points (HDBSCAN label -1) become their own singleton clusters.
        Returns clusters sorted by size descending.
        """
        n = len(embeddings)
        
        if n == 0:
            return []
        
        if n < 4:
            return self._make_singletons(metadata)
        
        try:
            import hdbscan
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=self.min_cluster_size,
                min_samples=self.min_samples,
                metric="euclidean",
            )
            labels = clusterer.fit_predict(embeddings)
        except ImportError:
            # hdbscan not installed — all singletons
            return self._make_singletons(metadata)
        
        # Group by label
        label_to_indices: dict[int, list[int]] = {}
        noise_count = 0
        
        for idx, label in enumerate(labels):
            if label == -1:
                noise_count += 1
                # Noise points become singletons with unique negative IDs
                singleton_id = -(idx + 1000)
                label_to_indices[singleton_id] = [idx]
            else:
                label_to_indices.setdefault(label, []).append(idx)
        
        clusters = []
        for cluster_id, indices in label_to_indices.items():
            cluster_embeddings = embeddings[indices]
            files = [metadata[i].get("filename", f"file_{i}") for i in indices]
            label = self._generate_label([metadata[i] for i in indices])
            coherence = self._coherence(cluster_embeddings)
            
            clusters.append(Cluster(
                cluster_id=max(0, cluster_id),  # remap negatives to 0 for noise singletons
                label=label,
                file_indices=indices,
                files=files,
                coherence=round(coherence, 4),
                size=len(indices),
            ))
        
        # Re-assign unique IDs and sort by size
        clusters.sort(key=lambda c: c.size, reverse=True)
        for i, c in enumerate(clusters):
            c.cluster_id = i
        
        return clusters
    
    def _make_singletons(self, metadata: list[dict]) -> list[Cluster]:
        """Create one cluster per file (fallback for small PRs)."""
        return [
            Cluster(
                cluster_id=i,
                label=meta.get("filename", f"file_{i}").split("/")[-1],
                file_indices=[i],
                files=[meta.get("filename", f"file_{i}")],
                coherence=1.0,
                size=1,
            )
            for i, meta in enumerate(metadata)
        ]
    
    def _generate_label(self, items: list[dict]) -> str:
        """
        Generate a label for a cluster from filenames + diff content.
        Returns top-2 bigrams or top-3 unigrams from the content.
        """
        text_parts = []
        for item in items:
            filename = item.get("filename", "")
            # Extract words from path components
            text_parts.extend(re.split(r'[/._\-\s]+', filename))
            
            # Add first 200 chars of diff
            diff = item.get("patch", "") or item.get("raw", "") or item.get("diff", "")
            text_parts.extend(re.split(r'\W+', diff[:200]))
        
        words = [
            w.lower() for w in text_parts
            if len(w) >= 3 and w.lower() not in STOPWORDS and w.isalpha()
        ]
        
        # Try bigrams first
        bigrams = []
        for i in range(len(words) - 1):
            bigrams.append(f"{words[i]} {words[i+1]}")
        
        if bigrams:
            top_bigrams = Counter(bigrams).most_common(2)
            if top_bigrams and top_bigrams[0][1] > 1:
                return ", ".join(bg for bg, _ in top_bigrams)
        
        # Fall back to top unigrams
        if words:
            top_words = Counter(words).most_common(3)
            return " ".join(w for w, _ in top_words)
        
        # Last resort: use first filename
        if items:
            return items[0].get("filename", "unknown").split("/")[-1]
        return "unknown"
    
    def _coherence(self, embeddings: np.ndarray) -> float:
        """Mean pairwise cosine similarity within a cluster."""
        n = len(embeddings)
        if n <= 1:
            return 1.0
        
        # Ensure L2 normalized
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms < 1e-9, 1.0, norms)
        normalized = embeddings / norms
        
        # Compute all pairwise similarities
        sim_matrix = normalized @ normalized.T
        
        # Mean of upper triangle (excluding diagonal)
        upper_tri = sim_matrix[np.triu_indices(n, k=1)]
        return float(np.mean(upper_tri))
