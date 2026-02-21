"""
CodeBERT-based code embedder with mean pooling + L2 normalization.
Falls back gracefully if transformers/torch not installed.
"""
from __future__ import annotations

import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class CodeEmbedder:
    """Embed code snippets using CodeBERT (microsoft/codebert-base).
    
    Mean-pools last hidden state and L2-normalizes the output.
    Returns numpy arrays of shape (N, 768).
    """
    
    def __init__(self, model_name: str = "microsoft/codebert-base", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._model = None
        self._tokenizer = None
    
    def _load(self) -> None:
        """Lazy-load model and tokenizer."""
        if self._model is not None:
            return
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModel.from_pretrained(self.model_name)
            self._model.eval()
            self._model.to(self.device)
            self._torch = torch
        except ImportError as e:
            raise ImportError(f"torch/transformers required for embedding: {e}") from e
    
    def _mean_pool(self, hidden_state: "torch.Tensor", attention_mask: "torch.Tensor") -> "torch.Tensor":
        """Mean pool last hidden state, masked by attention."""
        mask = attention_mask.unsqueeze(-1).float()
        summed = (hidden_state * mask).sum(dim=1)
        count = mask.sum(dim=1).clamp(min=1e-9)
        return summed / count
    
    def embed(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """Embed a list of texts. Returns shape (N, 768), L2-normalized rows."""
        self._load()
        torch = self._torch
        all_embeddings = []
        
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
            
            pooled = self._mean_pool(outputs.last_hidden_state, encoded["attention_mask"])
            
            # L2 normalize
            norms = pooled.norm(dim=-1, keepdim=True).clamp(min=1e-9)
            normalized = (pooled / norms).cpu().numpy()
            all_embeddings.append(normalized)
        
        return np.vstack(all_embeddings).astype(np.float32)
    
    def embed_single(self, text: str) -> np.ndarray:
        """Embed a single text. Returns shape (768,)."""
        return self.embed([text])[0]
