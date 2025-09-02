#!/usr/bin/env bash
set -euo pipefail
# Reads OPENROUTER_KEYS (comma-separated). Writes .env.active with OPENAI_API_KEY.
IN="${1:-.env}"
OUT="${2:-.env.active}"

# Normalize and source IN
sed -e 's/\r$//' "$IN" | awk 'NF && $1 !~ /^#/' > .env.export
set -a; . ./.env.export; set +a

: "${OPENAI_API_BASE_URL:=https://openrouter.ai/api/v1}"
if [[ -n "${OPENROUTER_KEYS:-}" ]]; then
  IFS=',' read -ra KEYS <<< "$OPENROUTER_KEYS"
  SEL="${KEYS[0]}"
elif [[ -n "${OPENROUTER_API_KEY:-}" ]]; then
  SEL="${OPENROUTER_API_KEY}"
else
  SEL="${OPENAI_API_KEY:-}"
fi

{
  echo "OPENAI_API_BASE_URL=${OPENAI_API_BASE_URL}"
  [[ -n "${SEL}" ]] && echo "OPENAI_API_KEY=${SEL}"
} > "${OUT}"
