# AGENTS — Project Conventions for AI Tools

## Project Overview
**PET (Prompt Engineering Tool)** — transforms user ideas into well-structured AI prompts. Backend API + web frontend with database persistence.

## Stack
- **Backend:** Python 3.14 + FastAPI + SQLAlchemy 2.0 + Alembic
- **Frontend:** Next.js (latest) + TypeScript + Tailwind CSS
- **Database:** SQLite (dev) -> PostgreSQL 18 (prod)
- **Package mgmt:** pip + requirements.txt (Python), pnpm (Node)
- **Shell:** PowerShell 7.5

## Code Conventions

### Python
- Format with **Ruff** (`ruff format .`)
- Lint with **Ruff** (`ruff check .`)
- Type-check with **mypy** (`mypy .`)
- Use `async def` for all route handlers
- Pydantic v2 for all request/response models
- SQLAlchemy 2.0 style (`select()` not `session.query()`)
- No docstrings/comments unless necessary for public APIs

### TypeScript/React
- Format with **Prettier** (`pnpm format`)
- TypeScript strict mode enabled
- React Server Components by default, client components only when needed
- Tailwind CSS for styling (no CSS modules or styled-components)
- No barrel exports (`index.ts`)

### Git
- Commit style: `type: concise description` (e.g. `feat: add prompt builder`, `fix: correct token counting`)
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
- No commits unless explicitly asked

## Testing
- **Python:** pytest with httpx (async) for API tests
- **TypeScript:** vitest + @testing-library/react
- Run all tests before considering a task complete

## Commands (will be updated as project grows)
```powershell
# Backend (in backend/)
python -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
ruff check . && ruff format . && mypy .

# Frontend (in frontend/)
pnpm install
pnpm dev
pnpm lint
pnpm typecheck
pnpm format
pnpm format:check

# Database (in backend/)
alembic upgrade head
alembic revision --autogenerate -m "message"

# Testing
pytest -v         # backend
pnpm test         # frontend (once vitest is set up)

# NOTE: pnpm 11 may block build scripts on first install.
# Run `pnpm approve-builds --all` to allow sharp + unrs-resolver builds.
```
