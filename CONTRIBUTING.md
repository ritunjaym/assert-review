# Contributing to Assert Review

## Local Development

### Prerequisites
- Node.js 22+, npm 11+
- Python 3.12+
- Git

### Setup
```bash
git clone https://github.com/ritunjaym/assert-review
cd assert-review
cp .env.example .env
npm install
pip install fastapi uvicorn python-dotenv pydantic pydantic-settings httpx pytest pytest-asyncio httpx
```

### Running Tests
```bash
# Python tests
pytest /Users/ritunjay/Desktop/assert-review/ml/ /Users/ritunjay/Desktop/assert-review/apps/api/tests/ -v

# Frontend unit tests  
cd apps/web && npm run test

# E2E tests (requires running server)
cd apps/web && npm run test:e2e
```

### Coding Standards
- Python: `ruff check . --fix` + `mypy apps/api/`
- TypeScript: `eslint apps/web/` + TypeScript strict mode
- Commits: Conventional Commits (`feat`, `fix`, `test`, `docs`, `chore`, `perf`)
- Scopes: `ml`, `api`, `web`, `partykit`, `infra`, `docs`, `tests`, `ci`

### No Secrets Policy
Never commit credentials. All secrets via `.env` (gitignored).
Pre-check: `grep -r "ghp_\|sk-\|AKIA" --include="*.py" --include="*.ts" .`
