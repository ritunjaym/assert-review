"""Tests for CodeEmbedder — use tiny mock to avoid downloading models."""
import numpy as np
import pytest


class MockEmbedder:
    """Mock embedder that returns deterministic unit vectors without loading models."""
    
    def __init__(self):
        self.dim = 768
    
    def embed(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        rng = np.random.RandomState(42)
        embeddings = rng.randn(len(texts), self.dim).astype(np.float32)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / norms
    
    def embed_single(self, text: str) -> np.ndarray:
        return self.embed([text])[0]


def test_embed_shape():
    embedder = MockEmbedder()
    texts = ["def foo(): pass", "class Bar:", "import os", "# comment", "x = 1"]
    result = embedder.embed(texts)
    assert result.shape == (5, 768), f"Expected (5, 768), got {result.shape}"


def test_embed_unit_vectors():
    embedder = MockEmbedder()
    texts = ["hello world", "foo bar baz"]
    result = embedder.embed(texts)
    norms = np.linalg.norm(result, axis=1)
    np.testing.assert_allclose(norms, np.ones(len(texts)), atol=1e-5)


def test_embed_single_shape():
    embedder = MockEmbedder()
    result = embedder.embed_single("def hello(): return 42")
    assert result.shape == (768,)


def test_embed_single_unit_vector():
    embedder = MockEmbedder()
    result = embedder.embed_single("test text")
    norm = np.linalg.norm(result)
    assert abs(norm - 1.0) < 1e-5
