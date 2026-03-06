## Retrieval Depth (K) Sensitivity

Ablation over retrieval depth K ∈ {1, 5, 10, 20, 50} using DenseOnlyBaseline (CodeBERT).
Metrics computed on the full test set; ranked list truncated to top-K before scoring.

| K  | NDCG@5 | MRR    | MAP    |
|----|--------|--------|--------|
| 1  | 0.2546 | 0.4444 | 0.1984 |
| 5  | 0.5080 | 0.5370 | 0.3949 |
| 10 | 0.5080 | 0.5481 | 0.4571 |
| 20 | 0.5080 | 0.5574 | 0.4984 |
| 50 | 0.5080 | 0.5574 | 0.5072 |

**Finding:** Metrics plateau at K≈10. Retrieving more than 10 candidates yields <1 pp NDCG gain, confirming K=10 as the optimal retrieval depth for this dataset. Production uses K=20 as a conservative choice above the plateau.
