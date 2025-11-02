#!/usr/bin/env bash
set -euo pipefail

# OOS Zero-Trust Secrets Validation
# Works in harmony with Archon secrets management

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

error() { echo -e "${RED}❌ $*${NC}" >&2; exit 1; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
info() { echo -e "${BLUE}ℹ️  $*${NC}"; }

# Industry-standard patterns from GitGuardian/Gitleaks
PATTERNS=(
    # OpenRouter API keys
    "sk-or-v1-[a-f0-9]{48}"
    # Generic API keys with context
    "(?i)(api[_-]?key|apikey|secret|token)[\s=:]['\"]+([a-z0-9]{20,})['\"]"
    # High entropy base64
    "[A-Za-z0-9+/]{40,}={0,2}"
    # Bearer tokens
    "Bearer[\s]+[a-zA-Z0-9\-._~+/]+"
    # AWS keys
    "AKIA[0-9A-Z]{16}"
    # GitHub tokens
    "ghp_[a-zA-Z0-9]{36}"
)

# Explicitly allowed patterns (must be exact match)
ALLOWED_PATTERNS=(
    "sk-or-v1-FAKE[0-9]{40}"
    "sk-or-v1-EXAMPLE[0-9]{40}"
    "sk-or-v1-DEMO[0-9]{40}"
    "your_api_key_here"
    "your_.*_key_here"
    "example_.*_key"
    "1234567890"  # Current placeholder
    "sk-or-v1-[real_key_here]"  # Documentation placeholder
)

validate_no_secrets() {
    local found_issues=false

    info "Scanning for secrets using industry-standard patterns..."

    # Get all staged files
    local files=()
    while IFS= read -r -d '' file; do
        files+=("$file")
    done < <(git diff --cached --name-only -z 2>/dev/null || true)

    # Also check untracked files
    while IFS= read -r -d '' file; do
        files+=("$file")
    done < <(git ls-files --others --exclude-standard -z 2>/dev/null || true)

    if [[ ${#files[@]} -eq 0 ]]; then
        success "No files to scan"
        return 0
    fi

    info "Checking ${#files[@]} files for secrets..."

    for file in "${files[@]}"; do
        if [[ ! -f "$file" ]]; then
            continue
        fi

        # Skip binary files and certain directories
        if [[ "$file" =~ \.(png|jpg|jpeg|gif|pdf|zip|tar|gz)$ ]] || \
           [[ "$file" =~ (venv|\.git|node_modules|\.pytest_cache) ]]; then
            continue
        fi

        # Check each pattern
        for pattern in "${PATTERNS[@]}"; do
            if grep -E "$pattern" "$file" >/dev/null 2>&1; then
                # Check if it's an allowed pattern
                local is_allowed=false
                for allowed in "${ALLOWED_PATTERNS[@]}"; do
                    if grep -E "$allowed" "$file" >/dev/null 2>&1; then
                        is_allowed=true
                        break
                    fi
                done

                if ! $is_allowed; then
                    error "Potential secret found in $file"
                    warn "Pattern: $pattern"
                    warn "Line(s):"
                    grep -n -E "$pattern" "$file" 2>/dev/null | head -3
                    echo
                    found_issues=true
                fi
            fi
        done
    done

    if $found_issues; then
        error "Secrets detected! Use Archon for secrets management."
        warn "Remove secrets from files and store them in Archon vault."
        warn "Reference: https://archon.khamel.com/vault"
        exit 1
    else
        success "No secrets detected in files"
        info "✨ All secrets should be stored in Archon vault"
        return 0
    fi
}

check_archon_integration() {
    info "Validating Archon secrets integration..."

    # Check if Archon configuration exists
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        if grep -q "ARCHON_VAULT_PASSWORD" "$PROJECT_ROOT/.env"; then
            success "Archon integration configured"
        else
            warn "Consider using Archon for secrets management"
            info "Visit: https://archon.khamel.com/vault"
        fi
    fi
}

main() {
    echo "🔒 OOS Zero-Trust Secrets Validation"
    echo "Working in harmony with Archon secrets management"
    echo

    validate_no_secrets
    check_archon_integration

    echo
    success "Security validation passed"
    info "Remember: Store all secrets in Archon vault"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi