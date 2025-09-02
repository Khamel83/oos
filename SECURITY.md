# Security posture

## Secrets management
- **Source of truth**: 1Password vault (`Private` → `bootstrap-env` → `env` field)
- **Local files**: `.env*` files are git-ignored and ephemeral
- **No hardcoding**: Secrets never committed to repositories
- **Rotation**: `OPENROUTER_KEYS` supports comma-separated key rotation

## Git protection
- `.gitignore` blocks `.env`, `.env.*`, `.env.export`
- GitHub push protection acts as guardrail
- If secrets leak: purge history with `git-filter-repo` and rotate keys
- Bootstrap creates repos with safe defaults (no `.env` mirrored)

## Network security
- **MCP endpoints**: Prefer `localhost:8051`; if remote, use HTTPS + IP allowlists
- **API keys**: OpenRouter proxies to multiple providers; rotate regularly
- **Transport**: All MCP/API calls over HTTPS where possible

## Process isolation
- **Runners**: Load env in isolated process scope
- **No logging**: Secrets not printed to stdout/logs
- **Environment**: Variables exported only to necessary child processes

## Audit trail
- 1Password tracks secret access/modifications
- `dev.md` logs operational decisions
- Git history shows configuration changes (excluding secrets)

## Threat model
**Protected against:**
- Accidental secret commits (git hooks, `.gitignore`)
- Key compromise (rotation, multiple providers)
- MCP endpoint exposure (localhost default)

**Assumptions:**
- 1Password vault security
- Local machine security
- Network transport security for remote MCPs

## Recovery procedures
1. **Leaked API key**: Rotate in 1Password → re-sync projects
2. **Compromised repo**: `git-filter-repo` → force push → rotate affected keys
3. **Lost 1Password access**: Regenerate all keys from providers directly