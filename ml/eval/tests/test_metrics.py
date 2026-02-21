"""
Tests for evaluation metrics with hand-crafted expected values.
"""
import math
import pytest
import numpy as np

from ml.eval.metrics import ranking_metrics, retrieval_metrics, clustering_metrics, _spearman, _kendall, _ndcg


def test_mse_exact():
    y_true = [1.0, 0.0, 0.5]
    y_pred = [1.0, 0.0, 0.5]
    metrics = ranking_metrics(y_true, y_pred)
    assert metrics["mse"] == pytest.approx(0.0, abs=1e-6)


def test_mse_known_value():
    # MSE of [1,0] vs [0,1] = mean([1,1]) = 1.0
    y_true = [1.0, 0.0]
    y_pred = [0.0, 1.0]
    metrics = ranking_metrics(y_true, y_pred)
    assert metrics["mse"] == pytest.approx(1.0, abs=1e-6)


def test_mae_exact():
    y_true = [1.0, 0.0, 0.5]
    y_pred = [1.0, 0.0, 0.5]
    metrics = ranking_metrics(y_true, y_pred)
    assert metrics["mae"] == pytest.approx(0.0, abs=1e-6)


def test_mae_known_value():
    # MAE of [1,0] vs [0,1] = mean([1,1]) = 1.0
    y_true = [1.0, 0.0]
    y_pred = [0.0, 1.0]
    metrics = ranking_metrics(y_true, y_pred)
    assert metrics["mae"] == pytest.approx(1.0, abs=1e-6)


def test_spearman_perfect_agreement():
    # Perfectly correlated ranks -> rho = 1.0
    y_true = [0.1, 0.3, 0.5, 0.7, 0.9]
    y_pred = [0.2, 0.4, 0.6, 0.8, 1.0]  # Same ranking
    metrics = ranking_metrics(y_true, y_pred)
    assert metrics["spearman_rho"] == pytest.approx(1.0, abs=1e-4)


def test_spearman_perfect_reversal():
    y_true = [0.1, 0.3, 0.5, 0.7, 0.9]
    y_pred = [0.9, 0.7, 0.5, 0.3, 0.1]  # Reversed
    metrics = ranking_metrics(y_true, y_pred)
    assert metrics["spearman_rho"] == pytest.approx(-1.0, abs=1e-4)


def test_kendall_perfect_agreement():
    y_true = [0.1, 0.5, 0.9]
    y_pred = [0.2, 0.6, 1.0]
    metrics = ranking_metrics(y_true, y_pred)
    assert metrics["kendall_tau"] == pytest.approx(1.0, abs=1e-4)


def test_ndcg_perfect():
    # When pred order matches true order, NDCG = 1.0
    y_true = [3.0, 2.0, 1.0, 0.0]
    y_pred = [3.0, 2.0, 1.0, 0.0]  # Same ranking
    metrics = ranking_metrics(y_true, y_pred)
    assert metrics["ndcg@5"] == pytest.approx(1.0, abs=1e-4)


def test_ndcg_worst():
    # When pred order is reversed, NDCG < 1
    y_true = [3.0, 2.0, 1.0, 0.0]
    y_pred = [0.0, 1.0, 2.0, 3.0]  # Reversed
    metrics = ranking_metrics(y_true, y_pred)
    assert metrics["ndcg@5"] < 1.0


def test_recall_at_k():
    # 2 queries, retrieved and relevant perfectly aligned
    retrieved = [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
    relevant = [[0, 1], [5, 6]]
    queries = [None, None]
    
    metrics = retrieval_metrics(queries, retrieved, relevant, k_values=[5])
    assert metrics["recall@5"] == pytest.approx(1.0, abs=1e-4)


def test_recall_at_k_partial():
    retrieved = [[0, 1, 2, 3, 4]]
    relevant = [[0, 5, 6]]  # only 0 is in top-5
    queries = [None]
    
    metrics = retrieval_metrics(queries, retrieved, relevant, k_values=[5])
    assert metrics["recall@5"] == pytest.approx(1/3, abs=1e-4)


def test_mrr_first_hit():
    retrieved = [[3, 0, 1], [2, 4, 5]]
    relevant = [[0], [4]]
    queries = [None, None]
    
    metrics = retrieval_metrics(queries, retrieved, relevant)
    # Query 1: hit at rank 2 -> 1/2; Query 2: hit at rank 2 -> 1/2; MRR = 0.5
    assert metrics["mrr"] == pytest.approx(0.5, abs=1e-4)


def test_ranking_metrics_empty():
    metrics = ranking_metrics([], [])
    assert metrics == {}


def test_clustering_metrics_insufficient_labels():
    embeddings = np.random.randn(5, 768).astype(np.float32)
    labels = [0, 0, 0, 0, 0]  # All same label -> can't compute silhouette
    metrics = clustering_metrics(embeddings, labels)
    assert "silhouette" in metrics
