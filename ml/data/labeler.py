import math
import re
from .schema import FileRecord, PRRecord


# Patterns
SECURITY_PATTERNS = re.compile(r'auth|crypto|secret|token|password|credential|jwt|oauth|session|key', re.IGNORECASE)
TEST_PATTERNS = re.compile(r'test|spec|__tests__|\.test\.|\.spec\.', re.IGNORECASE)
CONFIG_EXTENSIONS = {'.json', '.yaml', '.yml', '.toml', '.lock', '.ini', '.cfg', '.env'}
SOURCE_PATTERNS = re.compile(r'^(src|lib|core|pkg|cmd|internal|app)/|/?(main|index)\.(ts|tsx|js|jsx|py|go|rs)$')
DOC_PATTERNS = re.compile(r'\.(md|txt|rst|adoc)$|^(docs?|documentation|CHANGELOG|LICENSE|README)', re.IGNORECASE)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _path_score(filename: str) -> float:
    """Score based on file path — higher for core source, lower for docs/config."""
    if DOC_PATTERNS.search(filename):
        return 0.1
    if SOURCE_PATTERNS.search(filename):
        return 0.9
    ext = '.' + filename.rsplit('.', 1)[-1] if '.' in filename else ''
    if ext in CONFIG_EXTENSIONS:
        return 0.3
    return 0.5


def _size_score(file: FileRecord, pr: PRRecord) -> float:
    """Sigmoid of change size normalized to PR total."""
    total = pr.total_additions + pr.total_deletions
    if total == 0:
        return 0.5
    file_changes = file.additions + file.deletions
    ratio = file_changes / total
    # Center sigmoid so ratio=0.3 → ~0.5
    return _sigmoid(10 * (ratio - 0.15))


def _security_score(filename: str, patch: str | None) -> float:
    """1.0 if file path or patch contains security-sensitive terms."""
    text = filename + (patch[:500] if patch else "")
    return 1.0 if SECURITY_PATTERNS.search(text) else 0.0


def compute_importance(file: FileRecord, pr: PRRecord) -> dict:
    """Compute importance score and sub-scores for a file."""
    path = _path_score(file.filename)
    size = _size_score(file, pr)
    security = _security_score(file.filename, file.patch)
    
    raw = 0.3 * path + 0.3 * size + 0.4 * security
    
    # Penalties
    penalty = 1.0
    if TEST_PATTERNS.search(file.filename):
        penalty *= 0.7
    
    ext = '.' + file.filename.rsplit('.', 1)[-1] if '.' in file.filename else ''
    if ext in CONFIG_EXTENSIONS:
        # Exception: large package.json changes are important
        if not (file.filename.endswith('package.json') and (file.additions + file.deletions) > 50):
            penalty *= 0.5
    
    score = max(0.0, min(1.0, raw * penalty))
    
    return {
        "importance_score": round(score, 4),
        "path_score": round(path, 4),
        "size_score": round(size, 4),
        "security_score": round(security, 4),
    }
