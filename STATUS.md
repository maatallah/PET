# PET — Project Status

## Phase Progress

| Phase | Progress | Tasks |
|-------|----------|-------|
| 0 — Foundation | 8/9 🔴 1 | Scaffold, conventions, database |
| 1 — Core MVP | 29/29 🟢 | API, engine, frontend |
| 2 — Enhanced | 0/8 🔴 | Optimizer, compare, multi-model, export |
| 3 — Advanced | 0/8 🔴 | Workflows, analytics, collaboration |

**Blocks:** Phase 0.8 (PostgreSQL) blocked until production deployment.

---

## Completed (Last Session: 2026-05-20)

- Moved all documentation `.md` files to `Docs/` (gitignored dev reference)
- Updated root `.gitignore` — added `Docs/`, `.vscode/`, `.idea/`, `*.log`, `.DS_Store`, `Thumbs.db`, `dist/`, `build/`, `*.egg-info/`
- Created `.cursorignore` — excludes Docs/, deps, cache, env, IDE, OS files, logs, db files
- Created `STATUS.md` — living document updated at end of each AI session
- Kept only `AGENTS.md` + `.gitignore` + `.cursorignore` + source dirs in root

---

## Key Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-20 | Documentation moved to `Docs/` and gitignored | Bloated dev docs not needed in source tree; reduces agent context |
| 2026-05-20 | `.cursorignore` created | Prevent AI agent from scanning dependencies, docs, cache |
| 2026-05-20 | `STATUS.md` at root, updated each session | Avoids reinventing decisions; single source of truth for agent state |
| 2026-05-20 | OpenRouter added as 4th LLM provider | OpenAI-compatible, uses `OPENROUTER_API_KEY`, default model `openai/gpt-4o-mini` |
| 2026-05-19 | UUID stored as strings `Uuid(as_uuid=False)` | Avoids uuid↔str coercion across SQLAlchemy, Pydantic, URL params |
| 2026-05-19 | CORS uses `CORS_ORIGINS=*` with code split to `["*"]` | pydantic-settings reads as str; expand in code |
| 2026-05-19 | API keys via pydantic-settings from `.env` | Consistent config, not `os.getenv` |
| 2026-05-19 | Auto-generated `owner_id` UUID placeholder | No auth system exists yet; FK constraint satisfied |
| 2026-05-19 | `ignore` cleanup pattern in every `useEffect` | Prevents stale state after StrictMode unmount/remount |
| 2026-05-19 | pnpm `onlyBuiltDependencies` + `approve-builds` | pnpm 11 blocks build scripts by default |

---

## Open Questions (Need User Input)

| Question | Options | Notes |
|----------|---------|-------|
| Authentication? | None / email+password / OAuth | Affects MVP scope |
| File storage? | Local disk / S3-compatible | Local fine for MVP |
| Prompt patterns? | Which initially? | Persona, CoT, FewShot currently |

---

## Next Steps

1. Test end-to-end flow: Workspace -> Project -> Session -> Prompt -> Run with provider
2. Verify workspace detail / project detail pages in browser (possible stale dev server 404)
3. Phase 2 features: A/B comparison, token estimator, multi-model, export
4. Initialize git repo and push to `git@github.com:maatallah/PET.git`
