#!/usr/bin/env bash
set -euo pipefail

# Ensure .env is properly gitignored for security with Archon integration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

error() { echo -e "${RED}❌ $*${NC}" >&2; exit 1; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }

if [[ ! -f "$PROJECT_ROOT/.gitignore" ]]; then
    error ".gitignore file not found"
fi

if grep -q "^\.env$" "$PROJECT_ROOT/.gitignore"; then
    success ".env is properly gitignored"
else
    warn ".env not found in .gitignore - adding it..."
    echo ".env" >> "$PROJECT_ROOT/.gitignore"
    success "Added .env to .gitignore"
fi

# Check for other sensitive files
sensitive_patterns=(
    "*.key"
    "*secret*"
    "*credentials*"
    "archon_secrets.json"
)

for pattern in "${sensitive_patterns[@]}"; do
    if ! grep -q "^${pattern}$" "$PROJECT_ROOT/.gitignore"; then
        warn "Adding $pattern to .gitignore..."
        echo "$pattern" >> "$PROJECT_ROOT/.gitignore"
    fi
done

success "GitIgnore security validation complete"