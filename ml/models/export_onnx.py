"""
ONNX export and INT8 quantization of the distilled student reranker.
Usage: python -m ml.models.export_onnx
"""
from __future__ import annotations

from pathlib import Path

import structlog

log = structlog.get_logger()

CHECKPOINT_DIR = Path(__file__).parent / "reranker"
ONNX_DIR = Path(__file__).parent / "reranker_onnx"


def export_reranker_to_onnx(
    checkpoint_path: str | None = None,
    output_path: str | None = None,
) -> None:
    """Export the distilled student reranker to ONNX format (opset 14).

    Load order: local checkpoint → ``ritunjaym/prism-reranker`` on HF Hub →
    ``microsoft/codebert-base`` (final fallback).  Verifies that the maximum
    absolute difference between PyTorch and ONNX outputs is < 1e-3.

    Args:
        checkpoint_path: Path to a local model directory.  Defaults to
            ``ml/models/reranker``.
        output_path: Destination ``.onnx`` file path.  Defaults to
            ``ml/models/reranker_onnx/model.onnx``.
    """
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    cp = Path(checkpoint_path or CHECKPOINT_DIR)
    out = Path(output_path or ONNX_DIR / "model.onnx")
    out.parent.mkdir(parents=True, exist_ok=True)

    # Load order: local checkpoint → HF Hub → codebert-base
    if cp.exists() and any(cp.iterdir()):
        model_name = str(cp)
        log.info(f"Loading local checkpoint from {cp}")
    else:
        try:
            model_name = "ritunjaym/prism-reranker"
            log.info(f"No local checkpoint found. Trying HF Hub: {model_name}")
            # Quick check: try loading tokenizer to detect format issues
            AutoTokenizer.from_pretrained(model_name, cache_dir="/tmp/hf-cache")
        except Exception as e:
            log.warning(f"HF Hub load failed ({e}). Falling back to microsoft/codebert-base")
            model_name = "microsoft/codebert-base"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="/tmp/hf-cache")
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=1, cache_dir="/tmp/hf-cache"
        )
    except Exception as e:
        log.warning(f"Failed to load {model_name} ({e}). Falling back to microsoft/codebert-base")
        model_name = "microsoft/codebert-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="/tmp/hf-cache")
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=1, cache_dir="/tmp/hf-cache"
        )

    model.eval()

    # Dummy input
    dummy = tokenizer(
        "def example(): pass",
        padding="max_length", max_length=128, truncation=True,
        return_tensors="pt",
    )

    with torch.no_grad():
        torch.onnx.export(
            model,
            tuple(dummy.values()),
            str(out),
            opset_version=14,
            input_names=["input_ids", "attention_mask", "token_type_ids"],
            output_names=["logits"],
            dynamic_axes={
                "input_ids": {0: "batch", 1: "sequence"},
                "attention_mask": {0: "batch", 1: "sequence"},
                "token_type_ids": {0: "batch", 1: "sequence"},
                "logits": {0: "batch"},
            },
        )
    log.info(f"ONNX model exported to {out}")

    # Verify
    import onnxruntime as ort
    sess = ort.InferenceSession(str(out))
    ort_out = sess.run(None, {k: v.numpy() for k, v in dummy.items()})
    torch_out = model(**dummy).logits.detach().numpy()
    import numpy as np
    diff = abs(ort_out[0] - torch_out).max()
    log.info(f"Max output diff PyTorch vs ONNX: {diff:.6f} ({'OK' if diff < 1e-3 else 'WARNING'})")

    log.info("exported ONNX model", path=str(out), size_mb=round(out.stat().st_size/1e6, 1), max_diff=round(float(diff), 6), status="ok" if diff < 1e-3 else "WARNING")


def quantize_onnx_model(
    onnx_path: str | None = None,
    output_path: str | None = None,
) -> None:
    """Dynamically quantize an ONNX model to INT8 using onnxruntime.

    Applies ``onnxruntime.quantization.quantize_dynamic`` with
    ``weight_type=QInt8``.  Prints the compression ratio and verifies that the
    quantized model can perform a forward pass.

    Args:
        onnx_path: Source FP32 ``.onnx`` file.  Defaults to
            ``ml/models/reranker_onnx/model.onnx``.
        output_path: Destination INT8 ``.onnx`` file.  Defaults to
            ``ml/models/reranker_onnx/model_int8.onnx``.

    Raises:
        FileNotFoundError: If ``onnx_path`` does not exist.
    """
    from onnxruntime.quantization import quantize_dynamic, QuantType

    src = Path(onnx_path or ONNX_DIR / "model.onnx")
    dst = Path(output_path or ONNX_DIR / "model_int8.onnx")

    if not src.exists():
        raise FileNotFoundError(f"ONNX model not found at {src}. Run export first.")

    quantize_dynamic(str(src), str(dst), weight_type=QuantType.QInt8)

    size_fp32 = src.stat().st_size / 1e6
    size_int8 = dst.stat().st_size / 1e6
    compression = (1 - size_int8 / size_fp32) * 100
    log.info("quantized ONNX to INT8", fp32_mb=round(size_fp32, 1), int8_mb=round(size_int8, 1), compression_pct=round(compression, 0))

    # Verify quantized model runs
    import onnxruntime as ort
    import numpy as np
    sess = ort.InferenceSession(str(dst))
    dummy = {
        "input_ids": np.ones((1, 128), dtype=np.int64),
        "attention_mask": np.ones((1, 128), dtype=np.int64),
        "token_type_ids": np.zeros((1, 128), dtype=np.int64),
    }
    out = sess.run(None, dummy)
    log.info("INT8 inference verification ok", output_shape=str(out[0].shape))


if __name__ == "__main__":
    export_reranker_to_onnx()
    try:
        quantize_onnx_model()
    except FileNotFoundError as e:
        log.warning("skipping quantization", error=str(e))
