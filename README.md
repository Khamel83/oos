# OOS — Omar Operation System

Turn-key project bootstrap for local agent coding with **Claude Code**, **Gemini CLI**, and **Qwen**, wired to **Archon (MCP)** and secrets from **1Password**.  
Goal: `mkdir project && bootstrap.sh` → code immediately with the right MCPs, keys, and runners.

## Why
- One command per project; idempotent.
- Secrets never live in git; 1Password is the source of truth.
- Archon MCP autowired (local or remote).
- Works with Claude/Gemini/Qwen CLIs interchangeably.

## What it does
- Pulls `.env` from 1Password item `bootstrap-env` (vault `Private`, field `env`).
- Normalizes env (drops CRLF/BOM, comments) and derives a runtime `.env.active`.
- Registers MCPs (Archon, Context7) for this project.
- Creates runners:
  - `.agents/runners/run_claude.sh`
  - `.agents/runners/run_gemini.sh`
  - `.agents/runners/run_qwen.sh`
- Optionally creates a GitHub repo and pushes (with push-protection safe defaults).

## Prereqs
- **Archon MCP** running (default local: `http://localhost:8051/mcp`).  
  Check: `curl -4 -I http://localhost:8051/mcp` → `200/405`.
- **1Password CLI** (`op`) signed in for each shell:  
  `eval "$(op signin)"`
- CLIs installed on PATH: `claude`, `gemini`, `qwen`, `gh`, `git`.

## Quick start (this repo)
```bash
# 1) Sign in to 1Password
eval "$(op signin)"

# 2) Ensure your vault has the item:
#    Vault: Private, Item: bootstrap-env, Field name: env  (KEY=VALUE lines)
op item get "bootstrap-env" --vault "Private" --fields env > .env
sed -i 's/\r$//' .env

# 3) Verify Archon
curl -4 -I http://localhost:8051/mcp

# 4) Verify MCPs at project scope
claude mcp list   # expect: archon ✓, context7 ✓

# 5) Launch a runner
.agents/runners/run_claude.sh   # inside, type: /mcp
```

## New project (one-liner)
```bash
mkdir -p /home/ubuntu/dev/<Name>
eval "$(op signin)"
OP_VAULT="Private" OP_ITEM="bootstrap-env" OP_FIELD="env" \
ORG="Khamel83" VIS="public" \
/home/ubuntu/dev/oos/bootstrap.sh "<Name>" "/home/ubuntu/dev/<Name>"
```

## Environment model
- `bin/safe_source_env.sh` → normalizes `.env` → `.env.export`
- `bin/select_or_key.sh` → writes `.env.active` (chooses `OPENAI_API_KEY` from `OPENROUTER_KEYS`, `OPENROUTER_API_KEY`, or `OPENAI_API_KEY`)
- Runners source `.env` then `.env.active`.

**Do not commit** `.env`, `.env.active`, `.env.export`. `.gitignore` enforces this.

## Archon MCP
- Local default: `ARCHON_URL=http://localhost:8051/mcp`
- Remote option: `ARCHON_URL=https://archon.khamel.com:8051/mcp`
- Health: `curl -4 -I $ARCHON_URL` (must return quickly).

## Keys
- `OPENROUTER_KEYS` (comma-separated) supports rotation; first working key is used.
- Optional: `CONTEXT7_API_KEY`, `GITHUB_PAT` (for GitHub MCP/tools that need PAT).

## GitHub
- `bootstrap.sh` can create `github.com/<ORG>/<repo>` when `VIS` is `public`/`private`.
- Push protection is respected. If you ever leak a secret, purge with `git-filter-repo` (see `docs/TROUBLESHOOTING.md`).

## Troubleshooting

See `docs/TROUBLESHOOTING.md`.

## License

MIT (or your choice).