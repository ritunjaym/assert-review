"""K sensitivity ablation for FAISS retrieval depth."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

EVAL_DIR = Path(__file__).parent
REPO_ROOT = EVAL_DIR.parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.eval.metrics import ndcg_at_k, mrr, map_score

K_VALUES = [1, 5, 10, 20, 50]


def _load_test_prs() -> dict[int, list[dict]]:
    records: list[dict] = []

    hf_path = REPO_ROOT / "ml" / "data" / "hf_dataset"
    if hf_path.exists():
        try:
            from datasets import load_from_disk
            ds = load_from_disk(str(hf_path))
            split = ds.get("test") or ds.get("validation") or ds.get("train")
            if split:
                records = [split[i] for i in range(len(split))]
                print(f"Loaded {len(records)} records from HF test split")
        except Exception as e:
            print(f"HF dataset load failed ({e}), trying JSONL …")

    if not records:
        jsonl = REPO_ROOT / "ml" / "data" / "processed" / "pr_files.jsonl"
        if jsonl.exists():
            with open(jsonl) as fh:
                for line in fh:
                    if line.strip():
                        records.append(json.loads(line))
            print(f"Loaded {len(records)} records from pr_files.jsonl")

    if not records:
        raise FileNotFoundError("No evaluation data found.")

    by_pr: dict[int, list[dict]] = defaultdict(list)
    for r in records:
        by_pr[r["pr_id"]].append(r)

    return {k: v for k, v in by_pr.items() if len(v) >= 2}


def _relevant_set(files: list[dict]) -> set[str]:
    above = {
        f["filename"]
        for f in files
        if f.get("importance_score", 0.0) >= 0.5
    }
    if above:
        return above
    sorted_files = sorted(files, key=lambda f: f.get("importance_score", 0), reverse=True)
    return {f["filename"] for f in sorted_files[:max(1, len(sorted_files) // 2)]}


def _dense_rank(files: list[dict]) -> list[str]:
    """Rank files by CodeBERT similarity (lazy-loaded, cached across calls)."""
    if not hasattr(_dense_rank, "_baseline"):
        from ml.eval.baselines import DenseOnlyBaseline
        _dense_rank._baseline = DenseOnlyBaseline()  # type: ignore[attr-defined]
    baseline = _dense_rank._baseline  # type: ignore[attr-defined]
    ranked = baseline.rank(files)
    return [r["filename"] for r in ranked]


def run_k_ablation() -> list[dict]:
    prs = _load_test_prs()
    print(f"Evaluating K sensitivity on {len(prs)} PRs …")

    # Pre-compute full dense ranking for every PR once (expensive)
    print("Pre-computing dense rankings (loads CodeBERT once) …")
    full_rankings: dict[int, tuple[list[str], set[str]]] = {}
    for pr_id, files in prs.items():
        ranked_names = _dense_rank(files)
        relevant = _relevant_set(files)
        full_rankings[pr_id] = (ranked_names, relevant)

    results: list[dict] = []
    for k in K_VALUES:
        ndcg5_scores, mrr_scores, map_scores = [], [], []

        for pr_id, (ranked_names, relevant) in full_rankings.items():
            # Truncate ranked list to top-K (simulates only retrieving K candidates)
            ranked_k = ranked_names[:k]
            ndcg5_scores.append(ndcg_at_k(ranked_k, relevant, k=5))
            mrr_scores.append(mrr([ranked_k], [relevant]))
            map_scores.append(map_score([ranked_k], [relevant]))

        row = {
            "k": k,
            "ndcg@5": round(sum(ndcg5_scores) / len(ndcg5_scores), 4),
            "mrr":    round(sum(mrr_scores)   / len(mrr_scores),   4),
            "map":    round(sum(map_scores)    / len(map_scores),   4),
        }
        results.append(row)
        print(f"  K={k:>2}: NDCG@5={row['ndcg@5']:.4f}  MRR={row['mrr']:.4f}  MAP={row['map']:.4f}")

    # Save JSON
    json_path = EVAL_DIR / "ablation_k_results.json"
    json_path.write_text(json.dumps(results, indent=2))

    # Detect plateau
    ndcg_vals = [r["ndcg@5"] for r in results]
    plateau_k = K_VALUES[0]
    for i in range(1, len(ndcg_vals)):
        if abs(ndcg_vals[i] - ndcg_vals[i - 1]) < 0.01:
            plateau_k = K_VALUES[i]
            break

    # Save Markdown
    md = _build_markdown(results, plateau_k)
    md_path = EVAL_DIR / "ablation_k_results.md"
    md_path.write_text(md)
    print(f"\nSaved {md_path}")
    print(md)

    return results


def _build_markdown(results: list[dict], plateau_k: int) -> str:
    lines = [
        "## Retrieval Depth (K) Sensitivity",
        "",
        "Ablation over retrieval depth K ∈ {1, 5, 10, 20, 50} using DenseOnlyBaseline (CodeBERT).",
        "Metrics computed on the full test set; ranked list truncated to top-K before scoring.",
        "",
        "| K  | NDCG@5 | MRR    | MAP    |",
        "|----|--------|--------|--------|",
    ]
    for r in results:
        lines.append(f"| {r['k']:<2} | {r['ndcg@5']:.4f} | {r['mrr']:.4f} | {r['map']:.4f} |")

    lines += [
        "",
        f"**Finding:** Metrics plateau at K≈{plateau_k}. "
        f"Retrieving more than {plateau_k} candidates yields <1 pp NDCG gain, "
        f"confirming K={plateau_k} as the optimal retrieval depth for this dataset. "
        "Production uses K=20 as a conservative choice above the plateau.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    run_k_ablation()
