#!/usr/bin/env bash
set -euo pipefail
ENV_FILE="${1:-.env}"
sed -e 's/\r$//' "$ENV_FILE" | awk 'NF && $1 !~ /^#/' > .env.export
set -a
. ./.env.export
set +a
