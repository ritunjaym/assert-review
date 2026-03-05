"""
Pareto chart: model accuracy (AUC) vs inference latency (p50 ms).

Loads ``ml/eval/benchmark_results.json`` produced by ``ml.eval.benchmark``.
Falls back to representative sample data when the file does not exist.

Usage::

    python -m ml.eval.pareto_chart

Output: ``docs/pareto.png``
"""
from __future__ import annotations

import json
from pathlib import Path

EVAL_DIR = Path(__file__).parent
REPO_ROOT = EVAL_DIR.parent.parent
RESULTS_PATH = EVAL_DIR / "benchmark_results.json"
OUTPUT_PATH = REPO_ROOT / "docs" / "pareto.png"

# Representative sample data (used when benchmark_results.json is absent)
_SAMPLE_DATA = [
    {"config": "PyTorch FP32", "auc": 0.87, "latency_p50_ms": 420},
    {"config": "LoRA",         "auc": 0.89, "latency_p50_ms": 450},
    {"config": "ONNX FP32",   "auc": 0.86, "latency_p50_ms": 140},
    {"config": "ONNX INT8",   "auc": 0.84, "latency_p50_ms": 110},
]


def load_benchmark_data() -> list[dict]:
    """Load benchmark results, falling back to sample data if file is absent.

    Reads ``ml/eval/benchmark_results.json`` written by ``ml.eval.benchmark``.
    For each model config, the batch_size=1 entry is used for latency so that
    single-request latency is shown (typical production scenario).

    Returns:
        List of dicts, each with keys:

        - ``config`` (str): Model variant name (e.g. ``"ONNX INT8"``).
        - ``auc`` (float): Validation AUC in [0, 1].
        - ``latency_p50_ms`` (float): Median inference latency in milliseconds.
    """
    if not RESULTS_PATH.exists():
        print(f"Warning: {RESULTS_PATH} not found — using sample data.")
        return _SAMPLE_DATA

    with open(RESULTS_PATH) as fh:
        raw: list[dict] = json.load(fh)

    # Prefer batch_size=1 entry per config for single-request latency
    by_config: dict[str, dict] = {}
    for entry in raw:
        cfg = entry.get("config", "unknown")
        if cfg not in by_config or entry.get("batch_size", 99) == 1:
            by_config[cfg] = {
                "config": cfg,
                "auc": float(entry.get("auc", 0.0)),
                "latency_p50_ms": float(entry.get("p50_ms", 0.0)),
            }

    return list(by_config.values()) if by_config else _SAMPLE_DATA


def plot_pareto(data: list[dict], output_path: Path) -> None:
    """Render and save a scatter plot of AUC vs p50 latency.

    Each model variant is plotted as a labelled point. Lower latency and
    higher AUC is better; the Pareto frontier is in the top-left region.

    Args:
        data: List of model-variant dicts (see :func:`load_benchmark_data`).
        output_path: Filesystem path for the output PNG file.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    _COLORS = ["#4C72B0", "#55A868", "#C44E52", "#8172B2"]
    _LABELS = {
        "pytorch_fp32": "PyTorch FP32",
        "pytorch_lora": "LoRA",
        "onnx_fp32":    "ONNX FP32",
        "onnx_int8":    "ONNX INT8",
    }

    fig, ax = plt.subplots(figsize=(8, 5))

    for i, entry in enumerate(data):
        label = _LABELS.get(entry["config"], entry["config"])
        ax.scatter(
            entry["latency_p50_ms"],
            entry["auc"],
            s=130,
            color=_COLORS[i % len(_COLORS)],
            zorder=3,
        )
        ax.annotate(
            label,
            xy=(entry["latency_p50_ms"], entry["auc"]),
            xytext=(8, 4),
            textcoords="offset points",
            fontsize=9,
        )

    ax.set_xlabel("Latency p50 (ms)", fontsize=11)
    ax.set_ylabel("AUC", fontsize=11)
    ax.set_title(
        "Accuracy vs Latency — CodeLens Reranker Variants",
        fontsize=12, fontweight="bold",
    )
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlim(left=0)
    ax.set_ylim(0.75, 1.0)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Pareto chart saved to {output_path}")


def main() -> None:
    """Entry point: load benchmark data and generate the Pareto chart."""
    data = load_benchmark_data()
    plot_pareto(data, OUTPUT_PATH)


if __name__ == "__main__":
    main()
