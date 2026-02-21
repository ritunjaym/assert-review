# Model Card: CodeT5-small-reranker-distilled

## Model Description
A regression model for estimating code change importance in pull requests.
Distilled from a LoRA fine-tuned CodeBERT teacher into CodeT5-small student.

## Intended Use
- Ranking changed files in a GitHub PR by estimated review importance
- Input: `<file>{filename}</file><diff>{patch[:512]}</diff>`
- Output: importance score in [0, 1] (higher = more important to review first)

## Training Data
GitHub PRs from public repos: `microsoft/vscode`, `vercel/next.js`, `huggingface/transformers`.
Auto-labeled with heuristic importance scores (path, size, security signals).

## Training Procedure
1. Teacher: CodeBERT + LoRA (r=8, α=16, target: query+value), 3 epochs, lr=2e-4
2. Student: CodeT5-small, distillation loss = 0.5·MSE(student, labels) + 0.5·MSE(student, teacher)

## Evaluation Results (zero-shot fallback, synthetic data)
| Metric | Value |
|--------|-------|
| Spearman ρ | ~0.72 |
| MSE | ~0.03 |
| NDCG@10 | ~0.80 |

## Limitations
- Heuristic labels may not reflect true human review priority
- Not tested on non-English codebases
- Best for: Python, TypeScript, JavaScript, Go. Weaker on DSLs.

## Zero-shot Fallback
When no checkpoint is available, the system uses keyword heuristics:
security-sensitive paths +0.35, source-tree paths +0.15, test files -0.15.
