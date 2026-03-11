"""
Build FAISS index from HuggingFace dataset.
Usage: python -m ml.models.build_index
"""
import json
import os
import time
from pathlib import Path

import numpy as np
import structlog

from .embedder import CodeEmbedder
from .index import PRIndex

log = structlog.get_logger()

FAISS_DIR = Path(__file__).parent / "faiss"
HF_DATASET_DIR = Path(__file__).parent.parent / "data" / "hf_dataset"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"


def format_hunk_text(record: dict) -> str:
    """Format a hunk record as text for embedding."""
    filename = record.get("filename", "")
    raw = record.get("raw", "") or record.get("patch", "")
    return f"// {filename}\n{raw[:1024]}"


def load_records() -> list[dict]:
    """Load records from HF dataset or fallback to JSONL."""
    # Try HF dataset first
    if HF_DATASET_DIR.exists():
        try:
            from datasets import load_from_disk
            ds = load_from_disk(str(HF_DATASET_DIR))
            train = ds["train"]
            records = [train[i] for i in range(len(train))]
            log.info("loaded records from HF dataset", n=len(records), split="train")
            return records
        except Exception as e:
            log.warning("could not load HF dataset, falling back to JSONL", error=str(e))
    
    # Fallback to JSONL
    hunks_path = PROCESSED_DIR / "pr_hunks.jsonl"
    if hunks_path.exists():
        records = []
        with open(hunks_path) as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        log.info("loaded hunk records from JSONL", n=len(records))
        return records
    
    files_path = PROCESSED_DIR / "pr_files.jsonl"
    if files_path.exists():
        records = []
        with open(files_path) as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        log.info("loaded file records from JSONL", n=len(records))
        return records
    
    raise FileNotFoundError(
        f"No dataset found. Run `python -m ml.data.build_dataset` first.\n"
        f"Looked in: {HF_DATASET_DIR}, {hunks_path}"
    )


def build_index(
    max_records: int | None = None,
    batch_size: int = 32,
    index_path: str | None = None,
) -> PRIndex:
    """Build FAISS index from dataset records."""
    records = load_records()
    if max_records:
        records = records[:max_records]
    
    log.info("building FAISS index", n_records=len(records))
    
    embedder = CodeEmbedder()
    texts = [format_hunk_text(r) for r in records]
    
    log.info("embedding records", n=len(texts))
    t0 = time.time()
    embeddings = embedder.embed(texts, batch_size=batch_size)
    embed_time = time.time() - t0
    log.info("embedding complete", n=len(texts), elapsed_s=round(embed_time, 1), records_per_s=round(len(texts)/embed_time, 1))
    
    metadata = []
    for r in records:
        raw = r.get("raw", "") or r.get("patch", "") or ""
        metadata.append({
            "filename": r.get("filename", ""),
            "importance_score": r.get("importance_score", 0.0),
            "hunk_preview": raw[:200],
            "pr_id": r.get("pr_id", 0),
            "repo": r.get("repo", ""),
        })
    
    index = PRIndex(dim=768)
    index.build(embeddings, metadata)
    
    save_path = index_path or str(FAISS_DIR / "hunk_index.faiss")
    index.save(save_path)
    
    index_size_mb = Path(save_path).stat().st_size / 1e6 if Path(save_path).exists() else 0
    log.info("saved FAISS index", path=save_path, size_mb=round(index_size_mb, 1), n_vectors=index.size)
    
    # Log to W&B if available
    try:
        import wandb
        if os.environ.get("WANDB_API_KEY"):
            wandb.init(project=os.environ.get("WANDB_PROJECT", "assert-review"), job_type="build_index")
            wandb.log({
                "embed_time_s": embed_time,
                "n_vectors": index.size,
                "index_size_mb": index_size_mb,
                "embedding_dim": 768,
            })
            wandb.finish()
    except Exception:
        pass
    
    return index


if __name__ == "__main__":
    build_index()
