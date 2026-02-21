"""
ONNX export and INT8 quantization of the distilled student reranker.
Usage: python -m ml.models.export_onnx
"""
from __future__ import annotations

from pathlib import Path
import logging

logger = logging.getLogger(__name__)

CHECKPOINT_DIR = Path(__file__).parent / "reranker"
ONNX_DIR = Path(__file__).parent / "onnx"


def export_reranker_to_onnx(
    checkpoint_path: str | None = None,
    output_path: str | None = None,
) -> None:
    """Export distilled student reranker to ONNX format."""
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    cp = Path(checkpoint_path or CHECKPOINT_DIR)
    out = Path(output_path or ONNX_DIR / "reranker.onnx")
    out.parent.mkdir(parents=True, exist_ok=True)

    if not cp.exists():
        logger.info(f"No checkpoint found at {cp}. Exporting CodeBERT base instead.")
        model_name = "microsoft/codebert-base"
    else:
        model_name = str(cp)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1)
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
    logger.info(f"ONNX model exported to {out}")

    # Verify
    import onnxruntime as ort
    sess = ort.InferenceSession(str(out))
    ort_out = sess.run(None, {k: v.numpy() for k, v in dummy.items()})
    torch_out = model(**dummy).logits.detach().numpy()
    import numpy as np
    diff = abs(ort_out[0] - torch_out).max()
    logger.info(f"Max output diff PyTorch vs ONNX: {diff:.6f} ({'OK' if diff < 1e-3 else 'WARNING'})")

    print(f"Exported to {out} ({out.stat().st_size/1e6:.1f} MB)")


def quantize_onnx_model(
    onnx_path: str | None = None,
    output_path: str | None = None,
) -> None:
    """INT8 quantize an ONNX model using onnxruntime."""
    from onnxruntime.quantization import quantize_dynamic, QuantType

    src = Path(onnx_path or ONNX_DIR / "reranker.onnx")
    dst = Path(output_path or ONNX_DIR / "reranker_int8.onnx")

    if not src.exists():
        raise FileNotFoundError(f"ONNX model not found at {src}. Run export first.")

    quantize_dynamic(str(src), str(dst), weight_type=QuantType.QInt8)
    
    size_fp32 = src.stat().st_size / 1e6
    size_int8 = dst.stat().st_size / 1e6
    compression = (1 - size_int8 / size_fp32) * 100
    print(f"Quantized: {size_fp32:.1f} MB → {size_int8:.1f} MB ({compression:.0f}% reduction)")


if __name__ == "__main__":
    export_reranker_to_onnx()
    try:
        quantize_onnx_model()
    except FileNotFoundError as e:
        print(f"Skipping quantization: {e}")
