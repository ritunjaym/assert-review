"""
Baseline rankers for comparison with the ML reranker.
All implement .rank(pr_files: list[dict]) -> list[dict].
"""
from __future__ import annotations

import math
import random
import re


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


PATH_SCORE_RE = re.compile(r'^(src|lib|core|pkg|cmd|internal|app)/', re.IGNORECASE)
SECURITY_RE = re.compile(r'auth|crypto|secret|token|password', re.IGNORECASE)
DOC_RE = re.compile(r'\.(md|txt|rst)$|^docs?/', re.IGNORECASE)


class RandomBaseline:
    """Scores files uniformly at random. Useful as a floor."""
    
    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)
    
    def rank(self, pr_files: list[dict]) -> list[dict]:
        scored = [
            {**f, "baseline_score": self._rng.random()}
            for f in pr_files
        ]
        return sorted(scored, key=lambda x: x["baseline_score"], reverse=True)


class FileSizeBaseline:
    """
    Scores files by sigmoid of (additions + deletions).
    Larger changes → higher score.
    """
    
    def rank(self, pr_files: list[dict]) -> list[dict]:
        scored = []
        for f in pr_files:
            change_size = f.get("additions", 0) + f.get("deletions", 0)
            score = _sigmoid(change_size / 50.0 - 2.0)  # centered around 100 lines
            scored.append({**f, "baseline_score": score})
        return sorted(scored, key=lambda x: x["baseline_score"], reverse=True)


class PathHeuristicBaseline:
    """
    Scores files using only the path-based heuristic from the labeler.
    Mirrors labeler._path_score() logic.
    """
    
    def rank(self, pr_files: list[dict]) -> list[dict]:
        scored = []
        for f in pr_files:
            filename = f.get("filename", "")
            score = self._path_score(filename)
            scored.append({**f, "baseline_score": score})
        return sorted(scored, key=lambda x: x["baseline_score"], reverse=True)
    
    def _path_score(self, filename: str) -> float:
        if DOC_RE.search(filename):
            return 0.1
        if SECURITY_RE.search(filename):
            return 0.95
        if PATH_SCORE_RE.match(filename):
            return 0.85
        ext = "." + filename.rsplit(".", 1)[-1] if "." in filename else ""
        config_exts = {".json", ".yaml", ".yml", ".toml", ".lock", ".ini", ".cfg"}
        if ext in config_exts:
            return 0.3
        return 0.5
