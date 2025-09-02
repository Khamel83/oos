#!/usr/bin/env bash
set -euo pipefail
ENV_FILE="${1:-.env}"; ACTIVE_FILE="${2:-.env.active}"
mapfile -t KEYS < <(grep -E '^OPENROUTER_KEYS=' "$ENV_FILE" | sed 's/^OPENROUTER_KEYS=//' | tr -d '"' | tr ',' '\n' | sed '/^\s*$/d')
[[ ${#KEYS[@]} -gt 0 ]] || { echo "No OPENROUTER_KEYS"; exit 1; }
for k in "${KEYS[@]}"; do
  code=$(curl -sS -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $k" https://openrouter.ai/api/v1/models || echo "000")
  if [[ "$code" == "200" ]]; then printf "OPENAI_API_KEY=%s\n" "$k" > "$ACTIVE_FILE"; exit 0; fi
done
echo "No working OpenRouter key"; exit 2
