"""
Evaluation metrics for ranking, retrieval, and clustering tasks.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np


def ranking_metrics(y_true: list[float], y_pred: list[float]) -> dict[str, float]:
    """
    Compute ranking metrics between true importance scores and predicted scores.
    
    Returns: MSE, MAE, Spearman rho, Kendall tau, NDCG@5, NDCG@10
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    if len(y_true) == 0:
        return {}
    
    yt = np.array(y_true, dtype=float)
    yp = np.array(y_pred, dtype=float)
    
    mse = float(np.mean((yt - yp) ** 2))
    mae = float(np.mean(np.abs(yt - yp)))
    
    # Spearman rho
    spearman = _spearman(yt, yp)
    
    # Kendall tau
    kendall = _kendall(yt, yp)
    
    # NDCG@k
    ndcg5 = _ndcg(yt, yp, k=5)
    ndcg10 = _ndcg(yt, yp, k=10)
    
    return {
        "mse": round(mse, 6),
        "mae": round(mae, 6),
        "spearman_rho": round(spearman, 6),
        "kendall_tau": round(kendall, 6),
        "ndcg@5": round(ndcg5, 6),
        "ndcg@10": round(ndcg10, 6),
    }


def retrieval_metrics(
    queries: list[np.ndarray],
    retrieved_indices: list[list[int]],
    relevant_indices: list[list[int]],
    k_values: list[int] = (5, 10),
) -> dict[str, float]:
    """
    Compute retrieval metrics: Recall@k and MRR.
    
    Args:
        queries: not used directly, kept for API compatibility
        retrieved_indices: for each query, list of retrieved item indices
        relevant_indices: for each query, list of relevant item indices
        k_values: list of k values for Recall@k
    """
    if not queries:
        return {}
    
    results = {}
    
    for k in k_values:
        recalls = []
        for retrieved, relevant in zip(retrieved_indices, relevant_indices):
            if not relevant:
                continue
            retrieved_k = set(retrieved[:k])
            relevant_set = set(relevant)
            recall = len(retrieved_k & relevant_set) / len(relevant_set)
            recalls.append(recall)
        results[f"recall@{k}"] = round(float(np.mean(recalls)) if recalls else 0.0, 6)
    
    # MRR
    reciprocal_ranks = []
    for retrieved, relevant in zip(retrieved_indices, relevant_indices):
        relevant_set = set(relevant)
        for rank, idx in enumerate(retrieved, 1):
            if idx in relevant_set:
                reciprocal_ranks.append(1.0 / rank)
                break
        else:
            reciprocal_ranks.append(0.0)
    
    results["mrr"] = round(float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0, 6)
    
    return results


def clustering_metrics(embeddings: np.ndarray, labels: list[int]) -> dict[str, float]:
    """
    Compute clustering quality metrics: Silhouette score and Davies-Bouldin index.
    Requires sklearn.
    """
    unique_labels = set(labels)
    if len(unique_labels) < 2:
        return {"silhouette": 0.0, "davies_bouldin": float("inf")}
    
    try:
        from sklearn.metrics import silhouette_score, davies_bouldin_score
        sil = float(silhouette_score(embeddings, labels, metric="cosine"))
        db = float(davies_bouldin_score(embeddings, labels))
        return {
            "silhouette": round(sil, 6),
            "davies_bouldin": round(db, 6),
        }
    except ImportError:
        return {"silhouette": 0.0, "davies_bouldin": 0.0}


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _rank_array(arr: np.ndarray) -> np.ndarray:
    """Convert values to 1-based ranks."""
    order = np.argsort(arr)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(arr) + 1)
    return ranks


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2:
        return 0.0
    ra = _rank_array(a)
    rb = _rank_array(b)
    d = ra - rb
    n = len(a)
    return float(1 - 6 * np.sum(d ** 2) / (n * (n ** 2 - 1)))


def _kendall(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2:
        return 0.0
    n = len(a)
    concordant = discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            sign_a = np.sign(a[i] - a[j])
            sign_b = np.sign(b[i] - b[j])
            if sign_a * sign_b > 0:
                concordant += 1
            elif sign_a * sign_b < 0:
                discordant += 1
    total = n * (n - 1) // 2
    return float((concordant - discordant) / total) if total > 0 else 0.0


def _dcg(scores: list[float], k: int) -> float:
    return sum(
        rel / math.log2(rank + 2)
        for rank, rel in enumerate(scores[:k])
    )


def _ndcg(y_true: np.ndarray, y_pred: np.ndarray, k: int) -> float:
    if len(y_true) == 0:
        return 0.0
    # Sort y_true by y_pred (predicted ranking)
    pred_order = np.argsort(y_pred)[::-1]
    pred_gains = y_true[pred_order].tolist()
    
    # Ideal: sort y_true by itself
    ideal_order = np.argsort(y_true)[::-1]
    ideal_gains = y_true[ideal_order].tolist()
    
    ideal_dcg = _dcg(ideal_gains, k)
    if ideal_dcg == 0:
        return 0.0
    
    return _dcg(pred_gains, k) / ideal_dcg
