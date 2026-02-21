"""
High-level PR grouping pipeline: embed → cluster → return GroupingResult.
"""
from __future__ import annotations

from .clusterer import SemanticClusterer, GroupingResult
from .embedder import CodeEmbedder


class PRGrouper:
    """Groups PR files into semantic clusters using embeddings + HDBSCAN."""
    
    def __init__(
        self,
        model_name: str = "microsoft/codebert-base",
        device: str = "cpu",
        min_cluster_size: int = 2,
        min_samples: int = 1,
    ):
        self.embedder = CodeEmbedder(model_name=model_name, device=device)
        self.clusterer = SemanticClusterer(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
        )
    
    def group_pr(self, pr_files: list[dict]) -> GroupingResult:
        """
        Embed all files and cluster them semantically.
        
        Each dict in pr_files should have: filename, patch (optional), 
        additions (optional), deletions (optional).
        """
        if not pr_files:
            return GroupingResult(
                clusters=[],
                file_cluster_map={},
                n_clusters=0,
                noise_count=0,
            )
        
        # Build text representation for each file
        texts = [
            f"// {f.get('filename', '')}\n{(f.get('patch', '') or '')[:512]}"
            for f in pr_files
        ]
        
        # Embed
        embeddings = self.embedder.embed(texts)
        
        # Cluster
        metadata = [{"filename": f.get("filename", ""), **f} for f in pr_files]
        clusters = self.clusterer.cluster(embeddings, metadata)
        
        # Build file → cluster_id map
        file_cluster_map: dict[str, int] = {}
        noise_count = 0
        for cluster in clusters:
            for fname in cluster.files:
                file_cluster_map[fname] = cluster.cluster_id
            if cluster.size == 1:
                noise_count += 1
        
        return GroupingResult(
            clusters=clusters,
            file_cluster_map=file_cluster_map,
            n_clusters=len(clusters),
            noise_count=noise_count,
        )
