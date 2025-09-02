#!/usr/bin/env bash
set -euo pipefail
set -a; source .env; set +a
[[ -f .env.active ]] || bin/select_or_key.sh .env .env.active
set -a; source .env.active; set +a
exec claude --mcp-debug
