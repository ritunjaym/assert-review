"""
Inference-only wrapper for the distilled student reranker model.
Falls back to zero-shot CodeBERT embedding cosine similarity if no checkpoint exists.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


CHECKPOINT_DIR = Path(__file__).parent / "reranker"


class Reranker:
    """
    Inference-only wrapper for the distilled CodeT5-small reranker.
    
    If the checkpoint doesn't exist, falls back to zero-shot scoring using
    the CodeEmbedder (cosine similarity as a proxy for importance).
    """
    
    def __init__(
        self,
        checkpoint_path: str | None = None,
        device: str = "cpu",
    ):
        self.checkpoint_path = checkpoint_path or str(CHECKPOINT_DIR)
        self.device = device
        self._model: Any = None
        self._tokenizer: Any = None
        self._loaded = False
        self._zero_shot = False
    
    def _try_load(self) -> None:
        """Attempt to load the fine-tuned checkpoint."""
        if self._loaded:
            return
        
        path = Path(self.checkpoint_path)
        if not path.exists() or not any(path.iterdir()):
            # No checkpoint — fall back to zero-shot
            self._zero_shot = True
            self._loaded = True
            return
        
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            
            self._tokenizer = AutoTokenizer.from_pretrained(str(path))
            self._model = AutoModelForSequenceClassification.from_pretrained(
                str(path), num_labels=1
            )
            self._model.eval()
            self._model.to(device=self.device)
            self._torch = torch
            self._zero_shot = False
        except Exception as e:
            # If loading fails, fall back to zero-shot
            print(f"Warning: Could not load reranker checkpoint ({e}). Using zero-shot fallback.")
            self._zero_shot = True
        
        self._loaded = True
    
    def score(self, texts: list[str]) -> list[float]:
        """
        Score each text with importance probability in [0, 1].
        Returns list same length as input.
        """
        self._try_load()
        
        if not texts:
            return []
        
        if self._zero_shot:
            return self._zero_shot_score(texts)
        
        return self._model_score(texts)
    
    def _model_score(self, texts: list[str]) -> list[float]:
        """Score using the fine-tuned model."""
        import torch
        
        scores = []
        batch_size = 16
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            encoded = self._tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            encoded = {k: v.to(self.device) for k, v in encoded.items()}
            
            with torch.no_grad():
                outputs = self._model(**encoded)
            
            # Apply sigmoid to get [0,1] scores
            logits = outputs.logits.squeeze(-1)
            probs = torch.sigmoid(logits).cpu().numpy().tolist()
            if isinstance(probs, float):
                probs = [probs]
            scores.extend(probs)
        
        return scores
    
    def _zero_shot_score(self, texts: list[str]) -> list[float]:
        """
        Zero-shot fallback: use keyword heuristics to estimate importance.
        This ensures the API works even without a trained checkpoint.
        """
        import re
        
        SECURITY_RE = re.compile(r'auth|crypto|secret|token|password|credential', re.IGNORECASE)
        SOURCE_RE = re.compile(r'<file>(src|lib|core|app)/', re.IGNORECASE)
        TEST_RE = re.compile(r'test|spec|__tests__', re.IGNORECASE)
        
        scores = []
        for text in texts:
            score = 0.4  # baseline
            
            if SECURITY_RE.search(text):
                score += 0.35
            if SOURCE_RE.search(text):
                score += 0.15
            if TEST_RE.search(text):
                score -= 0.15
            
            # Normalize by length as proxy for change size
            length = len(text)
            if length > 500:
                score += 0.05
            
            scores.append(max(0.0, min(1.0, score)))
        
        return scores
    
    def rank(self, items: list[dict], text_key: str = "diff") -> list[dict]:
        """
        Score all items by the text_key field.
        Returns items sorted descending by score with 'reranker_score' added.
        """
        if not items:
            return []
        
        texts = [str(item.get(text_key, "")) for item in items]
        scores = self.score(texts)
        
        ranked = []
        for item, score in zip(items, scores):
            ranked.append({**item, "reranker_score": score})
        
        return sorted(ranked, key=lambda x: x["reranker_score"], reverse=True)
