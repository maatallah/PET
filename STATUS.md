# PET — Project Status

## Phase Progress

| Phase | Progress | Tasks |
|-------|----------|-------|
| 0 — Foundation | 8/9 🔴 1 | Scaffold, conventions, database |
| 1 — Core MVP | 29/29 🟢 | API, engine, frontend |
| 2 — Enhanced | 5/8 🟡 | Real-time token estimator, export, A/B compare, full-text search, tag filtering |
| 3 — Advanced | 0/8 🔴 | Workflows, analytics, collaboration |

**Blocks:** Phase 0.8 (PostgreSQL) blocked until production deployment.

---

## Completed (Session 2026-05-20)

**Phase 2 Features Built:**
- `POST /tokenize` endpoint — live token count + cost estimation for any text
- `GET /prompts/{id}/export?format=markdown|json` — export prompts as .md or .json
- A/B comparison page at `/prompts/{id}/compare` — run same prompt with different providers/models side by side
- Dynamic provider dropdown — loads from `GET /providers` instead of hardcoded list
- Live token estimate display on prompt detail page (debounced 300ms)
- Export buttons (.md, .json, A/B Compare) on prompt detail page
- Full-text search: `GET /search?q=` across workspaces, projects, sessions, prompts with breadcrumb navigation
- Search bar in header (debounced 300ms, dropdown results)
- Tag filtering on sessions: `GET /sessions?tags=tag1,tag2` with Python-level intersection filter
- Frontend API client extended: `estimateTokens`, `exportPromptUrl`, `ExecuteResult` now includes all response fields

**OpenRouter Provider:**
- 4th LLM provider (OpenAI-compatible, uses `OPENROUTER_API_KEY`)
- 4 unit tests: name, execute success, custom params, import error handling

**Context Optimization:**
- Bloated docs moved to `Docs/` (gitignored)
- `.cursorignore` created — excludes deps, docs, cache, env, IDE files
- Improved `.gitignore` — added Docs/, OS, IDE, logs, build artifacts
- `STATUS.md` at root — updated each session to carry state across AI sessions
- Only `AGENTS.md`, `.gitignore`, `.cursorignore`, `STATUS.md` in root

**Git/Deployment:**
- Git init + initial commit (103 files, 8798 insertions)
- Pushed to `github.com/maatallah/PET.git`

---

## Key Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-20 | Docs moved to `Docs/` + gitignored | Reduces agent context bloat |
| 2026-05-20 | `.cursorignore` created | Prevents AI scanning deps/docs/cache |
| 2026-05-20 | `STATUS.md` updated each session | Single source of truth for agent state |
| 2026-05-20 | OpenRouter as 4th provider | OpenAI-compatible, minimal code |
| 2026-05-20 | `GET /providers` endpoint | Frontend loads dynamically instead of hardcoding |
| 2026-05-20 | Token estimator uses debounced POST | Avoids per-keystroke API calls, 300ms debounce |
| 2026-05-20 | A/B compare = new page, not inline | Cleaner UX for side-by-side comparison |
| 2026-05-20 | Full-text search via single `GET /search` endpoint | Searches all 4 entity types, returns breadcrumb paths |
| 2026-05-20 | Tag filtering at Python level, not SQL | SQLite JSON queries are complex; small dataset justifies Python filter |
| 2026-05-19 | UUID as strings `Uuid(as_uuid=False)` | Avoids uuid↔str coercion across layers |
| 2026-05-19 | CORS uses `CORS_ORIGINS=*` | pydantic-settings reads as str; expand in code |
| 2026-05-19 | API keys via pydantic-settings from `.env` | Consistent config, not `os.getenv` |
| 2026-05-19 | Auto-generated `owner_id` UUID | No auth; FK constraint satisfied |
| 2026-05-19 | `ignore` pattern in every `useEffect` | Prevents stale state after StrictMode |
| 2026-05-19 | pnpm `onlyBuiltDependencies` | pnpm 11 blocks build scripts by default |

---

## Open Questions (Need User Input)

| Question | Options | Notes |
|----------|---------|-------|
| Authentication? | None / email+password / OAuth | Affects MVP scope |
| File storage? | Local disk / S3-compatible | Local fine for MVP |
| Prompt patterns? | Which initially? | Persona, CoT, FewShot currently |

---

## Next Steps

1. Phase 2 remaining features: prompt optimizer (AI suggestions), full-text search, tag-based filtering, context window visualizer
2. Phase 3 features: prompt chaining, RAG context builder, analytics dashboard, team collaboration, injection scanner, API key vault
3. Set valid API keys in `backend/.env` for live execution
4. Push subsequent commits to GitHub
