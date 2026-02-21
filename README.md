# Assert Review

> AI-powered code review interface — ML ↔ Product portfolio project for Assert Labs.

## Overview

Assert Review demonstrates deep ML ↔ Product synergy by surfacing ML-computed importance rankings, semantic change groups, and real-time reviewer presence directly in the code review workflow.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| Real-time | PartyKit (WebSockets) |
| ML API | FastAPI, Python 3.12 |
| Embeddings | CodeBERT (microsoft/codebert-base) |
| Reranker | CodeT5-small (distilled, ONNX) |
| Clustering | HDBSCAN |
| Vector Store | FAISS |
| Training | W&B, Google Colab |
| Deploy | Vercel (frontend + API), PartyKit cloud |

## Getting Started

### Prerequisites

- Node.js 22+
- Python 3.12+
- Git

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/assert-review
cd assert-review
cp .env.example .env
# Fill in .env values

# Install JS deps
npm install

# Install Python deps
pip install -e ".[api,dev]"

# Run API
cd apps/api && uvicorn main:app --reload

# Run frontend (in another terminal)
cd apps/web && npm run dev
```

## Project Structure

```
assert-review/
├── apps/web/          # Next.js 14 frontend
├── apps/api/          # FastAPI ML backend
├── packages/shared-types/  # Shared TypeScript types
├── ml/                # ML pipeline (data, models, eval, notebooks)
├── infra/partykit/    # Real-time collaboration server
└── docs/              # Architecture diagrams, OpenAPI spec
```

## Development Status

This project is being built phase-by-phase. See git tags for milestones.
