# OOS (Organized Operational Setup) - Complete Project Management System

**Advanced project bootstrap and management system** for local agent coding with **Claude Code**, **Gemini CLI**, and **Qwen**, integrated with **Archon (MCP)** and secure secrets from **1Password**.

🎯 **Goal:** `mkdir project && bootstrap_enhanced.sh` → comprehensive project setup with monitoring, security, testing, and management tools.

## 🚀 Core Benefits
- **One-command setup** per project; completely idempotent
- **Security-first approach** with comprehensive audit capabilities  
- **Zero-secret git commits** - 1Password is the single source of truth
- **Archon MCP integration** with proper project separation
- **Multi-agent support** - Works with Claude/Gemini/Qwen CLIs interchangeably
- **Production-ready tooling** with monitoring, testing, and optimization
- **Enterprise-grade security** with encryption, audit logging, and compliance

## 🛠️ What It Provides

### Core Bootstrap Features
- Pulls `.env` from 1Password item `bootstrap-env` (vault `Private`, field `env`)
- Normalizes environment (drops CRLF/BOM, comments) and derives runtime `.env.active`
- Auto-registers MCPs (Archon, Context7) with health monitoring
- Creates optimized runners for each AI CLI with proper environment isolation
- Optional GitHub repo creation with push-protection safe defaults
- **NEW:** Enhanced bootstrap with pre-flight checks and rollback capabilities

### Advanced Management Tools
- **Diagnostics System** - Interactive troubleshooting with self-healing
- **Health Monitoring** - Continuous system monitoring with alerting  
- **Security Auditing** - Comprehensive security scanning and compliance reporting
- **Performance Monitoring** - Profiling, benchmarking, and optimization
- **Testing Framework** - Unit, integration, security, and performance testing
- **Project Templates** - Rapid project creation with customizable templates
- **MCP Management** - Dynamic MCP server configuration and health monitoring
- **Key Rotation** - Automated API key management with smart failover
- **Web Dashboard** - Real-time monitoring and management interface

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