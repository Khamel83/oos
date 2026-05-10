# LLM Overview — oos
*Updated: 2026-05-10 07:35 UTC | Tier: standard | Auto-updated: daily cron*

## What This Is
**Your systematic thinking environment** - a brain extension system for consistent, structured development workflows.

## Current State
*Status: 🟢 active from local git history*

**Active work:**
- a5bf8c8 chore: bootstrap LLM-OVERVIEW files 2026-05-10
- 22b05b7 fix: replace humanizer gitlink with actual skill files, sync framework
- 3ffdc84 chore: update AGENTS.md to ONE_SHOT v13
- 4388a08 feat: add simple secrets management system and fix deprecation warnings
- 6023092 fix: add documentation placeholders to security allowlist
- 0e45abc fix: update documentation examples to use standardized fake API keys

**Known issues:**
- No known issue found in recent commit subjects or local TODO/BLOCKERS docs.

**Recent changes (7 days):**
- `a5bf8c8 chore: bootstrap LLM-OVERVIEW files 2026-05-10`

## Architecture
- Stack marker: Python package/CLI
- Stack marker: Node/JavaScript
- Stack marker: systemd service
- Stack marker: Makefile-driven operations
- Top-level entry: `AGENTS.md`
- Top-level entry: `AI_REFERENCE.md`
- Top-level entry: `api/`
- Top-level entry: `archive/`
- Top-level entry: `auth.py`
- Top-level entry: `BENCHMARK_DRIVEN_MODEL_SELECTION.md`
- Top-level entry: `benchmark_model_selection_report.json`
- Top-level entry: `benchmark_model_selector.py`

## Key Commands
- `python3 -m pytest  # run tests if configured`
- `python3 -m pip install -e .  # editable install`
- `git status --short`
- `git log --oneline -5`

## Dependencies
- **Runs on:** Not declared in local repo evidence.
- **Calls out to:** See repo docs and config files.
- **Called by:** Not declared in local repo evidence.
- **Env vars required:** No `.env.example` keys found.

## Critical Rules
- Preserve repo-local instructions in `AGENTS.md`, `CLAUDE.md`, or README when present.
- Do not infer behavior from the repository name alone; verify against local docs and source.

## Gotchas
- Generated from local evidence only: git history, top-level structure, README/CLAUDE/AGENTS/docs, and env examples.
