"""
Generate ml/data/reranker_pairs.jsonl from pr_files.jsonl.

Each record: {"text": "<file>{filename}\n{patch}", "label": 1 or 0}
  - label=1 if additions > 20 OR security keyword in filename
  - label=0 otherwise

Usage: python -m ml.data.build_reranker_pairs
"""
from __future__ import annotations

import json
from pathlib import Path

PROCESSED_DIR = Path(__file__).parent / "processed"
INPUT_PATH = PROCESSED_DIR / "pr_files.jsonl"
OUTPUT_PATH = PROCESSED_DIR / "reranker_pairs.jsonl"

SECURITY_KEYWORDS = [
    "auth", "crypto", "secret", "token", "password",
    "credential", "security", "permission", "oauth", "jwt", "key",
]


def is_positive(filename: str, additions: int) -> int:
    fname_lower = filename.lower()
    if additions > 20:
        return 1
    if any(kw in fname_lower for kw in SECURITY_KEYWORDS):
        return 1
    return 0


def build_pairs(
    input_path: Path = INPUT_PATH,
    output_path: Path = OUTPUT_PATH,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = pos = neg = skipped = 0

    with open(input_path) as fin, open(output_path, "w") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)
            filename = record.get("filename", "")
            additions = record.get("additions", 0)
            patch = record.get("patch") or ""

            label = is_positive(filename, additions)
            text = f"<file>{filename}\n{patch}"

            fout.write(json.dumps({"text": text, "label": label}) + "\n")
            total += 1
            if label == 1:
                pos += 1
            else:
                neg += 1

    print(f"\n=== Reranker Pairs Stats ===")
    print(f"  Total pairs:    {total}")
    print(f"  Positive (1):   {pos}  ({pos/total*100:.1f}%)")
    print(f"  Negative (0):   {neg}  ({neg/total*100:.1f}%)")
    print(f"  Output:         {output_path}")


if __name__ == "__main__":
    build_pairs()
