"""
Tests for baseline rankers.
"""
import pytest
from ml.eval.baselines import RandomBaseline, FileSizeBaseline, PathHeuristicBaseline


SAMPLE_FILES = [
    {"filename": "src/auth/login.py", "additions": 50, "deletions": 10, "patch": ""},
    {"filename": "README.md", "additions": 5, "deletions": 2, "patch": ""},
    {"filename": "tests/test_auth.py", "additions": 30, "deletions": 5, "patch": ""},
    {"filename": "config/settings.yaml", "additions": 3, "deletions": 1, "patch": ""},
    {"filename": "src/core/engine.py", "additions": 100, "deletions": 50, "patch": ""},
]


def test_random_baseline_returns_all_items():
    baseline = RandomBaseline()
    ranked = baseline.rank(SAMPLE_FILES)
    assert len(ranked) == len(SAMPLE_FILES)


def test_random_baseline_scores_in_unit_interval():
    baseline = RandomBaseline()
    ranked = baseline.rank(SAMPLE_FILES)
    for item in ranked:
        assert 0.0 <= item["baseline_score"] <= 1.0


def test_filesize_baseline_returns_all_items():
    baseline = FileSizeBaseline()
    ranked = baseline.rank(SAMPLE_FILES)
    assert len(ranked) == len(SAMPLE_FILES)


def test_filesize_baseline_sorted_descending():
    baseline = FileSizeBaseline()
    ranked = baseline.rank(SAMPLE_FILES)
    scores = [r["baseline_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_filesize_baseline_large_change_scores_higher():
    files = [
        {"filename": "a.py", "additions": 200, "deletions": 100},
        {"filename": "b.py", "additions": 1, "deletions": 0},
    ]
    baseline = FileSizeBaseline()
    ranked = baseline.rank(files)
    assert ranked[0]["filename"] == "a.py"


def test_path_heuristic_baseline_returns_all():
    baseline = PathHeuristicBaseline()
    ranked = baseline.rank(SAMPLE_FILES)
    assert len(ranked) == len(SAMPLE_FILES)


def test_path_heuristic_scores_in_unit_interval():
    baseline = PathHeuristicBaseline()
    ranked = baseline.rank(SAMPLE_FILES)
    for item in ranked:
        assert 0.0 <= item["baseline_score"] <= 1.0


def test_path_heuristic_sorted_descending():
    baseline = PathHeuristicBaseline()
    ranked = baseline.rank(SAMPLE_FILES)
    scores = [r["baseline_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_path_heuristic_auth_higher_than_docs():
    files = [
        {"filename": "src/auth/login.py", "additions": 10, "deletions": 2},
        {"filename": "README.md", "additions": 10, "deletions": 2},
    ]
    baseline = PathHeuristicBaseline()
    ranked = baseline.rank(files)
    assert ranked[0]["filename"] == "src/auth/login.py"


def test_random_baseline_deterministic_with_seed():
    b1 = RandomBaseline(seed=42)
    b2 = RandomBaseline(seed=42)
    r1 = b1.rank(SAMPLE_FILES)
    r2 = b2.rank(SAMPLE_FILES)
    assert [r["filename"] for r in r1] == [r["filename"] for r in r2]
