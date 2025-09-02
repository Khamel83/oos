#!/usr/bin/env bash
set -euo pipefail
ENV_FILE="${1:-.env}"

# Normalize and strip BOM
tmp="$(mktemp)"
LC_ALL=C tr -d '\r' < "$ENV_FILE" > "$tmp"
sed -i '1s/^\xEF\xBB\xBF//' "$tmp"

# Build a clean export file (only KEY=VALUE, ignore comments/blank)
awk '
  /^[[:space:]]*#/ { next }         # comments
  /^[[:space:]]*$/ { next }         # blanks
  /^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*=/{ print; next }  # valid assign
  { next }                          # drop anything else
' "$tmp" > .env.export
rm -f "$tmp"

# Export only proper KEY=VALUE lines without executing junk
set -a
while IFS= read -r line; do
  # Preserve value as-is
  eval "export ${line}"
done < .env.export
set +a
