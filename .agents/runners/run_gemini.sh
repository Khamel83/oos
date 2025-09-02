#!/usr/bin/env bash
set -euo pipefail
set -a; source .env; [[ -f .env.active ]] || bin/select_or_key.sh .env .env.active; source .env.active; set +a
exec gemini chat
