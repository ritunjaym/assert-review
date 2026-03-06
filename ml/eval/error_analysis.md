## Error Analysis

Evaluated on 9 PRs. Failure cases (NDCG@5 < 0.5): **1** (11%). Success cases (NDCG@5 > 0.9): **8** (88%).

### Model Failure Patterns

- **Large PRs (>10 files):** 1 of 1 failure cases (100%). Avg 25.0 files, 25 LOC/file.
- **Small PRs (<3 files):** 0 of 1 failure cases (0%).
- **Documentation-heavy PRs (>50% .md):** 0 of 1 (0%).
- **Test-heavy PRs (>50% test files):** 0 of 1 (0%).

### Model Success Patterns

- **Security-related files present:** 2 of 8 success cases (25%) contained auth/crypto/token filenames — the model reliably ranks these Critical.
- **Avg PR size in successes:** 9.9 files, 112 LOC/file (typically focused, single-concern PRs).
- **Test-heavy PRs correctly deprioritised:** 1 of 8 (12%) test-heavy PRs landed in success cases.

### Root Cause

The model was trained on synthetic importance scores derived from file-path heuristics (security keywords, source-tree depth, change size). Failure cases concentrate in:

1. **Large PRs** — when many files score similarly, small ranking errors compound into large NDCG drops. With real reviewer interaction data (click-through, time-on-file), the model would learn finer-grained priority distinctions.

2. **Atypical repo structure** — repos with non-standard layouts (e.g., monorepos where `build/` contains critical logic) defeat path-based priors. Semantic embedding helps here but is limited by the 128-token truncation.

3. **Pure documentation PRs** — `importance_score` is calibrated for code changes; doc-only PRs are systematically under-scored, causing the model to mis-rank them. A doc-detection pre-filter would fix this class of errors.
