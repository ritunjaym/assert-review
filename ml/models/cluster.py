"""
Embedding-based semantic clustering for CodeLens.

Embeds each file's patch text using CodeBERT, then runs HDBSCAN to form
semantic clusters. Each cluster is auto-labeled by the dominant pattern of
its member files.

Usage (standalone)::

    from ml.models.cluster import cluster_files
    groups = cluster_files(filenames, patches, embedder=None)
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

import numpy as np

# ── Auto-labeling heuristics ─────────────────────────────────────────────────

_TEST_RE = re.compile(r"test|spec", re.IGNORECASE)
_DEP_RE = re.compile(
    r"package\.json|requirements|setup\.py|pyproject\.toml|go\.(mod|sum)|Cargo\.toml|Pipfile",
    re.IGNORECASE,
)
_DOC_RE = re.compile(r"\.md$|docs?/|readme|changelog|\.rst$|\.txt$", re.IGNORECASE)


def _label_cluster(filenames: list[str], patches: list[str]) -> str:
    """Auto-label a cluster from its filenames and patch content.

    Priority order:

    1. **Test changes** — majority match ``test`` / ``spec`` patterns.
    2. **Dependency update** — majority match package manifest patterns.
    3. **Documentation** — majority match doc/markdown patterns.
    4. **Cleanup / Refactor** — majority files have more deletions than additions.
    5. **Directory name** — majority share the same top-level directory.
    6. **Core changes** — default fallback.

    Args:
        filenames: File paths in the cluster.
        patches: Unified-diff patch text for each file (parallel to ``filenames``).

    Returns:
        A short human-readable label string.
    """
    n = len(filenames)
    if n == 0:
        return "Core changes"

    majority = n // 2 + 1

    if sum(1 for f in filenames if _TEST_RE.search(f)) >= majority:
        return "Test changes"
    if sum(1 for f in filenames if _DEP_RE.search(f)) >= majority:
        return "Dependency update"
    if sum(1 for f in filenames if _DOC_RE.search(f)) >= majority:
        return "Documentation"

    cleanup = sum(
        1 for p in patches
        if p and p.count("\n-") > p.count("\n+")
    )
    if cleanup >= majority:
        return "Cleanup / Refactor"

    dirs = [f.split("/")[0] for f in filenames if "/" in f]
    if dirs:
        top, cnt = Counter(dirs).most_common(1)[0]
        if cnt >= majority:
            return top

    return "Core changes"


def cluster_files(
    filenames: list[str],
    patches: list[str],
    embedder: Any | None,
    min_cluster_size: int = 2,
) -> list[dict]:
    """Cluster files by semantic similarity using CodeBERT embeddings + HDBSCAN.

    Falls back to directory-based grouping when the embedder is unavailable or
    HDBSCAN is not installed.

    Args:
        filenames: File paths to cluster.
        patches: Unified-diff patch text for each file (parallel to ``filenames``).
        embedder: A ``(tokenizer, model)`` tuple from CodeBERT, or ``None`` for
            directory-based fallback.
        min_cluster_size: Minimum points per HDBSCAN cluster (default 2).

    Returns:
        List of group dicts with keys:

        - ``cluster_id`` (int): 0-based cluster index.
        - ``label`` (str): Auto-generated human-readable label.
        - ``files`` (list[str]): File paths in this cluster.
        - ``coherence`` (float): Mean pairwise cosine similarity in [0, 1].

    Example:
        >>> groups = cluster_files(["src/a.py", "tests/test_a.py"], ["", ""], None)
        >>> len(groups) >= 1
        True
    """
    n = len(filenames)
    if n == 0:
        return []

    # ── Embed each file ───────────────────────────────────────────────────────
    embeddings: np.ndarray | None = None
    if embedder is not None and n >= 2:
        try:
            import torch

            tokenizer, model = embedder
            texts = [
                f"<file>{fname}</file><diff>{(patch or '')[:512]}</diff>"
                for fname, patch in zip(filenames, patches)
            ]
            inputs = tokenizer(
                texts, padding=True, truncation=True, max_length=128, return_tensors="pt"
            )
            with torch.no_grad():
                out = model(**inputs)
            emb = out.last_hidden_state.mean(dim=1)  # (N, 768)
            norms = emb.norm(dim=1, keepdim=True) + 1e-8
            embeddings = (emb / norms).numpy().astype(np.float32)
        except Exception:
            embeddings = None

    # ── HDBSCAN clustering ────────────────────────────────────────────────────
    labels: list[int] | None = None
    if embeddings is not None:
        try:
            import hdbscan

            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=min_cluster_size,
                metric="euclidean",
                cluster_selection_method="eom",
            )
            labels = clusterer.fit_predict(embeddings).tolist()
        except Exception:
            labels = None

    # ── Directory-based fallback ──────────────────────────────────────────────
    if labels is None:
        dir_map: dict[str, list[int]] = defaultdict(list)
        for i, fname in enumerate(filenames):
            parts = fname.split("/")
            key = parts[0] if len(parts) > 1 else "root"
            dir_map[key].append(i)
        labels = [0] * n
        for cluster_id, idxs in enumerate(dir_map.values()):
            for idx in idxs:
                labels[idx] = cluster_id

    # ── Assemble output groups ────────────────────────────────────────────────
    cluster_to_idxs: dict[int, list[int]] = defaultdict(list)
    for i, lbl in enumerate(labels):
        cluster_to_idxs[lbl].append(i)

    groups: list[dict] = []
    output_id = 0

    # Non-noise clusters first, then noise (-1) points as singletons
    sorted_ids = sorted(k for k in cluster_to_idxs if k >= 0)
    if -1 in cluster_to_idxs:
        sorted_ids.append(-1)

    for lbl in sorted_ids:
        idxs = cluster_to_idxs[lbl]

        if lbl == -1:
            for idx in idxs:
                groups.append({
                    "cluster_id": output_id,
                    "label": filenames[idx].split("/")[-1],
                    "files": [filenames[idx]],
                    "coherence": 1.0,
                })
                output_id += 1
            continue

        c_filenames = [filenames[i] for i in idxs]
        c_patches = [patches[i] for i in idxs]
        label = _label_cluster(c_filenames, c_patches)

        if embeddings is not None and len(idxs) > 1:
            e = embeddings[idxs]
            sim = e @ e.T  # cosine sims (embeddings already L2-normed)
            mask = np.ones(sim.shape, dtype=bool)
            np.fill_diagonal(mask, False)
            coherence = float(np.clip(np.mean(sim[mask]), 0.0, 1.0))
        else:
            coherence = 1.0 if len(idxs) == 1 else round(0.7 + 0.3 * min(len(idxs) / 5, 1.0), 2)

        groups.append({
            "cluster_id": output_id,
            "label": label,
            "files": c_filenames,
            "coherence": round(coherence, 2),
        })
        output_id += 1

    return groups
