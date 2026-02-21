"""Tests for PRIndex — builds tiny in-memory FAISS index."""
import numpy as np
import pytest
import tempfile
import os

# Skip if faiss not installed
faiss = pytest.importorskip("faiss", reason="faiss-cpu not installed")

from ml.models.index import PRIndex, RetrievalResult


def make_unit_vectors(n: int, dim: int = 768, seed: int = 42) -> np.ndarray:
    rng = np.random.RandomState(seed)
    vecs = rng.randn(n, dim).astype(np.float32)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / norms


def make_metadata(n: int) -> list[dict]:
    return [
        {
            "filename": f"src/file_{i}.py",
            "importance_score": float(i) / n,
            "hunk_preview": f"def func_{i}(): pass",
            "pr_id": i,
            "repo": "test/repo",
        }
        for i in range(n)
    ]


def test_build_and_search():
    n = 20
    embeddings = make_unit_vectors(n)
    metadata = make_metadata(n)
    
    index = PRIndex(dim=768)
    index.build(embeddings, metadata)
    
    assert index.size == n
    
    # Query with exact first vector — should get score ≈ 1.0
    query = embeddings[0]
    results = index.search(query, k=5)
    
    assert len(results) == 5
    assert results[0].score > 0.9
    assert results[0].filename == "src/file_0.py"


def test_search_returns_sorted_descending():
    n = 20
    embeddings = make_unit_vectors(n)
    metadata = make_metadata(n)
    
    index = PRIndex(dim=768)
    index.build(embeddings, metadata)
    
    query = make_unit_vectors(1, seed=99)[0]
    results = index.search(query, k=10)
    
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_retrieval_result_fields():
    embeddings = make_unit_vectors(5)
    metadata = make_metadata(5)
    
    index = PRIndex(dim=768)
    index.build(embeddings, metadata)
    
    results = index.search(embeddings[2], k=3)
    assert all(isinstance(r, RetrievalResult) for r in results)
    assert all(hasattr(r, "score") for r in results)
    assert all(hasattr(r, "filename") for r in results)
    assert all(hasattr(r, "importance") for r in results)


def test_save_and_load():
    n = 15
    embeddings = make_unit_vectors(n)
    metadata = make_metadata(n)
    
    index = PRIndex(dim=768)
    index.build(embeddings, metadata)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.faiss")
        index.save(path)
        
        assert os.path.exists(path)
        assert os.path.exists(path + ".meta")
        
        index2 = PRIndex(dim=768)
        index2.load(path)
        
        assert index2.size == n
        results = index2.search(embeddings[0], k=1)
        assert results[0].score > 0.9


def test_empty_search_raises():
    index = PRIndex(dim=768)
    with pytest.raises(RuntimeError, match="not built"):
        index.search(np.zeros(768, dtype=np.float32), k=5)
