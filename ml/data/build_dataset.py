"""
Orchestrates: scrape → parse → label → save JSONL + HuggingFace dataset.
"""
import json
import os
from pathlib import Path

from .parser import parse_pr
from .labeler import compute_importance
from .schema import LabeledFile, LabeledHunk

PROCESSED_DIR = Path(__file__).parent / "processed"
HF_DIR = Path(__file__).parent / "hf_dataset"


def build_from_raw(raw_path: Path) -> tuple[list[LabeledFile], list[LabeledHunk]]:
    """Parse and label all PRs from raw JSONL."""
    labeled_files = []
    labeled_hunks = []
    
    with open(raw_path) as f:
        for line in f:
            if not line.strip():
                continue
            pr_json = json.loads(line)
            pr_record = parse_pr(pr_json)
            
            for file_rec in pr_record.files:
                scores = compute_importance(file_rec, pr_record)
                lf = LabeledFile(
                    pr_id=pr_record.pr_id,
                    repo=pr_record.repo,
                    pr_title=pr_record.title,
                    filename=file_rec.filename,
                    status=file_rec.status,
                    additions=file_rec.additions,
                    deletions=file_rec.deletions,
                    patch=file_rec.patch,
                    hunk_count=len(file_rec.hunks),
                    **scores,
                )
                labeled_files.append(lf)
                
                for i, hunk in enumerate(file_rec.hunks):
                    lh = LabeledHunk(
                        pr_id=pr_record.pr_id,
                        repo=pr_record.repo,
                        filename=file_rec.filename,
                        hunk_index=i,
                        old_start=hunk.old_start,
                        new_start=hunk.new_start,
                        added_lines=hunk.added_lines,
                        removed_lines=hunk.removed_lines,
                        raw=hunk.raw,
                        importance_score=scores["importance_score"],
                    )
                    labeled_hunks.append(lh)
    
    return labeled_files, labeled_hunks


def save_jsonl(records: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in records:
            f.write(r.model_dump_json() + "\n")
    print(f"Saved {len(records)} records to {path}")


def save_hf_dataset(labeled_files: list[LabeledFile]) -> None:
    """Save to HuggingFace datasets format."""
    try:
        from datasets import Dataset, DatasetDict
        
        data = [f.model_dump() for f in labeled_files]
        for item in data:
            if item.get("patch") is None:
                item["patch"] = ""
        
        dataset = Dataset.from_list(data)
        n = len(dataset)
        train_end = int(0.8 * n)
        val_end = int(0.9 * n)
        
        dd = DatasetDict({
            "train": dataset.select(range(train_end)),
            "validation": dataset.select(range(train_end, val_end)),
            "test": dataset.select(range(val_end, n)),
        })
        
        HF_DIR.mkdir(parents=True, exist_ok=True)
        dd.save_to_disk(str(HF_DIR))
        print(f"Saved HF dataset: train={len(dd['train'])}, val={len(dd['validation'])}, test={len(dd['test'])}")
    except ImportError:
        print("datasets library not installed, skipping HF format save")


def log_stats(labeled_files: list[LabeledFile], labeled_hunks: list[LabeledHunk]) -> None:
    """Log dataset statistics (W&B if available, else print)."""
    scores = [f.importance_score for f in labeled_files]
    
    stats = {
        "total_files": len(labeled_files),
        "total_hunks": len(labeled_hunks),
        "repos": len({f.repo for f in labeled_files}),
        "prs": len({f.pr_id for f in labeled_files}),
        "avg_importance": sum(scores) / len(scores) if scores else 0,
        "high_importance_pct": sum(1 for s in scores if s > 0.7) / len(scores) if scores else 0,
    }
    
    print("\n=== Dataset Statistics ===")
    for k, v in stats.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
    
    try:
        import wandb
        wandb_key = os.environ.get("WANDB_API_KEY", "")
        if wandb_key:
            wandb.init(project=os.environ.get("WANDB_PROJECT", "assert-review"), job_type="dataset")
            wandb.log(stats)
            wandb.finish()
    except Exception:
        pass


def main():
    raw_path = Path(__file__).parent / "raw" / "prs_raw.jsonl"
    
    if not raw_path.exists():
        print(f"Raw data not found at {raw_path}. Run scraper first.")
        return
    
    print("Building dataset from raw PRs...")
    labeled_files, labeled_hunks = build_from_raw(raw_path)
    
    save_jsonl(labeled_files, PROCESSED_DIR / "pr_files.jsonl")
    save_jsonl(labeled_hunks, PROCESSED_DIR / "pr_hunks.jsonl")
    save_hf_dataset(labeled_files)
    log_stats(labeled_files, labeled_hunks)


if __name__ == "__main__":
    main()
