"""
Tests for Reranker inference wrapper.
Uses mock model (random weights) or zero-shot fallback.
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock


def make_mock_model_score(texts):
    """Return random [0,1] scores for tests."""
    rng = np.random.RandomState(len(texts))
    return list(rng.random(len(texts)).astype(float))


def test_score_returns_correct_length():
    from ml.models.reranker import Reranker
    reranker = Reranker()
    # Force zero-shot (no checkpoint)
    reranker._loaded = True
    reranker._zero_shot = True
    
    texts = ["diff text 1", "diff text 2", "diff text 3"]
    scores = reranker.score(texts)
    assert len(scores) == len(texts)


def test_score_values_in_unit_interval():
    from ml.models.reranker import Reranker
    reranker = Reranker()
    reranker._loaded = True
    reranker._zero_shot = True
    
    texts = [
        "src/auth/login.py +++ def validate_token",
        "README.md docs update",
        "test_utils.py test case",
    ]
    scores = reranker.score(texts)
    for s in scores:
        assert isinstance(s, float), f"Score should be float, got {type(s)}"
        assert 0.0 <= s <= 1.0, f"Score {s} out of [0,1]"


def test_score_empty_list():
    from ml.models.reranker import Reranker
    reranker = Reranker()
    reranker._loaded = True
    reranker._zero_shot = True
    
    assert reranker.score([]) == []


def test_rank_returns_descending_order():
    from ml.models.reranker import Reranker
    reranker = Reranker()
    reranker._loaded = True
    reranker._zero_shot = True
    
    items = [
        {"filename": "a.py", "diff": "README update docs"},
        {"filename": "b.py", "diff": "<file>src/auth/token.py auth crypto secret"},
        {"filename": "c.py", "diff": "test_spec.py unit tests"},
    ]
    ranked = reranker.rank(items, text_key="diff")
    
    scores = [r["reranker_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True), "Items should be sorted descending"


def test_rank_preserves_all_items():
    from ml.models.reranker import Reranker
    reranker = Reranker()
    reranker._loaded = True
    reranker._zero_shot = True
    
    items = [{"filename": f"file{i}.py", "diff": f"code {i}"} for i in range(7)]
    ranked = reranker.rank(items)
    assert len(ranked) == len(items), "All items should be preserved"


def test_rank_adds_reranker_score_field():
    from ml.models.reranker import Reranker
    reranker = Reranker()
    reranker._loaded = True
    reranker._zero_shot = True
    
    items = [{"filename": "auth.py", "diff": "auth token secret"}]
    ranked = reranker.rank(items)
    assert "reranker_score" in ranked[0], "reranker_score field should be added"


def test_rank_empty_list():
    from ml.models.reranker import Reranker
    reranker = Reranker()
    reranker._loaded = True
    reranker._zero_shot = True
    
    assert reranker.rank([]) == []


def test_zero_shot_security_higher_than_readme():
    """Security-related files should score higher than docs in zero-shot mode."""
    from ml.models.reranker import Reranker
    reranker = Reranker()
    reranker._loaded = True
    reranker._zero_shot = True
    
    security_texts = ["<file>src/auth/jwt.py auth token password"]
    readme_texts = ["<file>README.md documentation update"]
    
    security_scores = reranker.score(security_texts)
    readme_scores = reranker.score(readme_texts)
    
    assert security_scores[0] > readme_scores[0], \
        f"Security ({security_scores[0]}) should outscore readme ({readme_scores[0]})"
