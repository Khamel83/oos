#!/usr/bin/env bash
set -euo pipefail
bin/safe_source_env.sh .env
[[ -f .env.active ]] || bin/select_or_key.sh .env .env.active
bin/safe_source_env.sh .env.active
exec gemini chat
