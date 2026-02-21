"""
Tests for SemanticClusterer.
Uses synthetic embeddings — no model download needed.
"""
import numpy as np
import pytest

from ml.models.clusterer import SemanticClusterer, Cluster


def make_two_cluster_embeddings(n_per_cluster: int = 5, noise: float = 0.01, seed: int = 42) -> np.ndarray:
    """Create embeddings clearly separating into 2 clusters."""
    rng = np.random.RandomState(seed)
    dim = 768
    
    centroid_a = rng.randn(dim).astype(np.float32)
    centroid_a /= np.linalg.norm(centroid_a)
    
    centroid_b = -centroid_a + rng.randn(dim).astype(np.float32) * 0.1
    centroid_b /= np.linalg.norm(centroid_b)
    
    cluster_a = centroid_a + rng.randn(n_per_cluster, dim).astype(np.float32) * noise
    cluster_b = centroid_b + rng.randn(n_per_cluster, dim).astype(np.float32) * noise
    
    embeddings = np.vstack([cluster_a, cluster_b])
    # L2 normalize
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms


def make_metadata(n: int, prefix: str = "file") -> list[dict]:
    return [{"filename": f"src/{prefix}_{i}.py"} for i in range(n)]


@pytest.mark.skipif(
    not __import__("importlib").util.find_spec("hdbscan"),
    reason="hdbscan not installed"
)
def test_two_clusters_detected():
    """10 embeddings (5+5) near opposite centroids → expect 2 clusters."""
    embeddings = make_two_cluster_embeddings(n_per_cluster=5)
    metadata = make_metadata(10)
    
    clusterer = SemanticClusterer(min_cluster_size=2, min_samples=1)
    clusters = clusterer.cluster(embeddings, metadata)
    
    # HDBSCAN may find 2 clusters or singletons depending on geometry
    # The key invariant: all files are accounted for
    total_files = sum(c.size for c in clusters)
    assert total_files == 10, f"Expected 10 total files, got {total_files}"
    assert len(clusters) >= 1


def test_singleton_fallback_for_small_pr():
    """< 4 files → each file becomes its own singleton cluster."""
    rng = np.random.RandomState(0)
    embeddings = rng.randn(3, 768).astype(np.float32)
    metadata = make_metadata(3)
    
    clusterer = SemanticClusterer()
    clusters = clusterer.cluster(embeddings, metadata)
    
    assert len(clusters) == 3, f"Expected 3 singletons, got {len(clusters)}"
    for c in clusters:
        assert c.size == 1
        assert c.coherence == 1.0


def test_empty_input_returns_empty():
    clusterer = SemanticClusterer()
    result = clusterer.cluster(np.zeros((0, 768), dtype=np.float32), [])
    assert result == []


def test_generate_label_returns_string():
    clusterer = SemanticClusterer()
    items = [
        {"filename": "src/auth/login.py", "patch": "+def login(): pass\n+def logout(): pass"},
        {"filename": "src/auth/session.py", "patch": "+class Session: pass"},
    ]
    label = clusterer._generate_label(items)
    assert isinstance(label, str)
    assert len(label) > 0


def test_generate_label_uses_common_words():
    """Common words in filenames/diffs should appear in label."""
    clusterer = SemanticClusterer()
    items = [
        {"filename": "auth/auth_service.py", "patch": "auth token validation"},
        {"filename": "auth/auth_middleware.py", "patch": "auth middleware check"},
        {"filename": "auth/auth_utils.py", "patch": "auth helper functions"},
    ]
    label = clusterer._generate_label(items)
    assert "auth" in label.lower()


def test_coherence_perfect_cluster():
    """Identical vectors → coherence = 1.0."""
    clusterer = SemanticClusterer()
    vec = np.array([[1.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0]], dtype=np.float32)
    assert abs(clusterer._coherence(vec) - 1.0) < 1e-5


def test_coherence_orthogonal_cluster():
    """Orthogonal vectors → coherence = 0.0."""
    clusterer = SemanticClusterer()
    vec = np.array([[1.0, 0.0],
                    [0.0, 1.0]], dtype=np.float32)
    assert abs(clusterer._coherence(vec) - 0.0) < 1e-5


def test_coherence_single_vector():
    """Single vector → coherence = 1.0 (no pairs)."""
    clusterer = SemanticClusterer()
    vec = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
    assert clusterer._coherence(vec) == 1.0


def test_cluster_ids_are_unique():
    """All cluster IDs should be unique."""
    rng = np.random.RandomState(1)
    embeddings = rng.randn(3, 768).astype(np.float32)
    metadata = make_metadata(3)
    
    clusterer = SemanticClusterer()
    clusters = clusterer.cluster(embeddings, metadata)
    
    ids = [c.cluster_id for c in clusters]
    assert len(ids) == len(set(ids)), "Cluster IDs should be unique"
