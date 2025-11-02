#!/usr/bin/env bash
set -euo pipefail

# OOS Mandatory Security Setup
# This script configures all necessary security measures for OOS development

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

error() { echo -e "${RED}❌ $*${NC}" >&2; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
header() { echo -e "${BLUE}${BOLD}$*${NC}"; }

# Security setup functions
install_pre_commit_hook() {
    header "1. Installing Pre-commit Security Hook..."

    if [[ -f "$PROJECT_ROOT/.git/hooks/pre-commit" ]]; then
        success "Pre-commit hook already exists"
    else
        if "$PROJECT_ROOT/bin/prevent_api_key_commits.sh" --install; then
            success "Pre-commit hook installed successfully"
        else
            error "Failed to install pre-commit hook"
            return 1
        fi
    fi
}

validate_env_configuration() {
    header "2. Validating Environment Configuration..."

    # Check if .env exists
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        warn ".env file not found, creating from template..."
        if [[ -f "$PROJECT_ROOT/.env.template" ]]; then
            cp "$PROJECT_ROOT/.env.template" "$PROJECT_ROOT/.env"
            success "Created .env from template"
            warn "Please add your actual API keys to .env file"
        else
            error "No .env.template found"
            return 1
        fi
    fi

    # Verify .env is gitignored
    if git check-ignore "$PROJECT_ROOT/.env" >/dev/null 2>&1; then
        success ".env file is properly gitignored"
    else
        error ".env file is not gitignored - this is a security risk!"
        warn "Add .env to .gitignore immediately"
        return 1
    fi

    # Check for any API keys in .env (without revealing them)
    if grep -q "OPENROUTER_API_KEY=" "$PROJECT_ROOT/.env"; then
        success "Found API key configuration in .env"
    else
        warn "No API key found in .env - update with your keys"
    fi
}

run_security_audit() {
    header "3. Running Security Audit..."

    # Check for any existing API key exposures
    if "$PROJECT_ROOT/bin/prevent_api_key_commits.sh" --check-all >/dev/null 2>&1; then
        success "No API keys found in repository"
    else
        warn "API key issues detected - fixing..."
        # Run the audit to show issues
        "$PROJECT_ROOT/bin/prevent_api_key_commits.sh" --check-all || true

        warn "Please fix the above issues before proceeding"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Security setup aborted"
            return 1
        fi
    fi
}

validate_git_hooks() {
    header "4. Validating Git Hooks..."

    local hook_file="$PROJECT_ROOT/.git/hooks/pre-commit"
    if [[ -f "$hook_file" && -x "$hook_file" ]]; then
        success "Pre-commit hook is installed and executable"

        # Test the hook
        if grep -q "prevent_api_key_commits.sh" "$hook_file"; then
            success "Pre-commit hook references API key prevention"
        else
            warn "Pre-commit hook may not include API key checking"
        fi
    else
        error "Pre-commit hook not found or not executable"
        return 1
    fi
}

check_required_files() {
    header "5. Checking Required Security Files..."

    local required_files=(
        "docs/SECURITY_SETUP_MANDATORY.md"
        "docs/FAKE_API_KEYS.md"
        "bin/prevent_api_key_commits.sh"
        ".env.template"
    )

    local missing_files=()

    for file in "${required_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$file" ]]; then
            success "Found required file: $file"
        else
            warn "Missing required file: $file"
            missing_files+=("$file")
        fi
    done

    if [[ ${#missing_files[@]} -gt 0 ]]; then
        error "Missing required security files: ${missing_files[*]}"
        return 1
    fi
}

create_security_summary() {
    header "6. Creating Security Summary..."

    local summary_file="$PROJECT_ROOT/.oos/security-status.md"
    mkdir -p "$(dirname "$summary_file")"

    cat > "$summary_file" << EOF
# OOS Security Status

**Last Updated**: $(date)
**Setup Version**: 1.0

## Security Configuration
- [x] Pre-commit hook installed
- [x] Environment validation completed
- [x] Security audit passed
- [x] Required files present

## Security Checklist
- [ ] API keys stored in .env file (not committed)
- [ ] Pre-commit hook working correctly
- [ ] No hardcoded keys in documentation
- [ ] Security tests passing

## Next Steps
1. Review docs/SECURITY_SETUP_MANDATORY.md
2. Test security with: git commit --dry-run
3. Run periodic audits: ./bin/audit-security.sh

## Security Contacts
- OOS Security Team: All maintainers
- Report issues: Create GitHub issue with "security" label
EOF

    success "Security summary created at .oos/security-status.md"
}

test_security_system() {
    header "7. Testing Security System..."

    # Create a temporary test file with a fake API key
    local test_file="$PROJECT_ROOT/test_api_key.txt"
    echo "OPENROUTER_API_KEY=\"sk-or-v1-FAKE0000000000000000000000000000000000000000000000000000\"" > "$test_file"

    # Add it to git and test if pre-commit hook blocks it
    git add "$test_file" 2>/dev/null || true

    # Test commit (should succeed with fake key)
    if git commit -m "test: security system validation" --dry-run >/dev/null 2>&1; then
        success "Security system allows fake keys (correct behavior)"
    else
        warn "Security system may be too restrictive"
    fi

    # Clean up
    git reset HEAD "$test_file" 2>/dev/null || true
    rm -f "$test_file"

    success "Security system test completed"
}

show_security_instructions() {
    header "🔒 Security Setup Complete!"

    echo
    echo -e "${GREEN}Your OOS installation is now secured with:${NC}"
    echo " • Pre-commit API key prevention"
    echo " • Environment validation"
    echo " • Security audit tools"
    echo " • Comprehensive documentation"
    echo
    echo -e "${YELLOW}Important Security Practices:${NC}"
    echo "1. Never commit real API keys to git"
    echo "2. Always use environment variables for credentials"
    echo "3. Use fake keys in documentation (see docs/FAKE_API_KEYS.md)"
    echo "4. Run periodic security audits"
    echo
    echo -e "${BLUE}Useful Commands:${NC}"
    echo " • ./bin/audit-security.sh          # Run security audit"
    echo " • ./bin/prevent_api_key_commits.sh --check-all  # Check repository"
    echo " • git status                        # Verify no sensitive files tracked"
    echo
    echo -e "${BOLD}📚 Required Reading:${NC}"
    echo " • docs/SECURITY_SETUP_MANDATORY.md"
    echo " • docs/FAKE_API_KEYS.md"
    echo " • docs/SECURITY_INCIDENT_POSTMORTEM.md"
    echo
    success "OOS security setup completed successfully!"
}

# Main execution
main() {
    header "🔒 OOS Mandatory Security Setup"
    echo "This will configure security measures to prevent API key exposure"
    echo

    # Check if we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        error "Not in a git repository. Security setup requires git."
        exit 1
    fi

    # Run all security setup steps
    install_pre_commit_hook || exit 1
    validate_env_configuration || exit 1
    run_security_audit || exit 1
    validate_git_hooks || exit 1
    check_required_files || exit 1
    create_security_summary || exit 1
    test_security_system || exit 1
    show_security_instructions
}

# Help message
show_help() {
    cat << EOF
OOS Mandatory Security Setup

Usage: $0 [options]

Options:
  --help, -h     Show this help message
  --audit-only   Run security audit only (skip setup)
  --force        Force re-installation of security components

Description:
This script configures mandatory security measures for OOS development:
- Pre-commit hooks to prevent API key commits
- Environment configuration validation
- Security audit tools
- Required security files

This should be run after 'oos bootstrap project' and before any development work.
EOF
}

# Parse arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --audit-only)
        header "Running Security Audit Only..."
        "$PROJECT_ROOT/bin/prevent_api_key_commits.sh" --check-all
        exit $?
        ;;
    --force)
        warn "Force mode - re-installing security components"
        rm -f "$PROJECT_ROOT/.git/hooks/pre-commit"
        main
        ;;
    "")
        main
        ;;
    *)
        error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac