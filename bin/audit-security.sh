#!/usr/bin/env bash
set -euo pipefail

# OOS Security Audit Script
# Comprehensive security audit for OOS development environment

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

# Audit results
AUDIT_PASSED=true
ISSUES_FOUND=()

# Audit functions
audit_api_key_exposure() {
    header "1. Checking for API Key Exposure..."

    if "$PROJECT_ROOT/bin/prevent_api_key_commits.sh" --check-all >/dev/null 2>&1; then
        success "No API keys detected in repository"
    else
        error "API key exposure detected!"
        warn "Run the following for details:"
        warn "  ./bin/prevent_api_key_commits.sh --check-all"
        ISSUES_FOUND+=("API key exposure in repository")
        AUDIT_PASSED=false
    fi
}

audit_gitignore_configuration() {
    header "2. Validating .gitignore Configuration..."

    local required_patterns=(
        ".env"
        "*.key"
        "*credentials*"
        "test_*_access.py"
        "working_ai_credentials.json"
    )

    local missing_patterns=()

    for pattern in "${required_patterns[@]}"; do
        if ! grep -q "^${pattern}$" "$PROJECT_ROOT/.gitignore" 2>/dev/null; then
            missing_patterns+=("$pattern")
        fi
    done

    if [[ ${#missing_patterns[@]} -eq 0 ]]; then
        success "All required .gitignore patterns present"
    else
        error "Missing .gitignore patterns: ${missing_patterns[*]}"
        ISSUES_FOUND+=("Incomplete .gitignore configuration")
        AUDIT_PASSED=false
    fi

    # Check if .env is tracked
    if git ls-files | grep -q "^\.env$"; then
        error ".env file is tracked by git - SECURITY RISK!"
        ISSUES_FOUND+=(".env file tracked by git")
        AUDIT_PASSED=false
    else
        success ".env file is not tracked by git"
    fi
}

audit_pre_commit_hook() {
    header "3. Validating Pre-commit Security Hook..."

    local hook_file="$PROJECT_ROOT/.git/hooks/pre-commit"

    if [[ -f "$hook_file" ]]; then
        if [[ -x "$hook_file" ]]; then
            success "Pre-commit hook is installed and executable"

            if grep -q "prevent_api_key_commits.sh" "$hook_file"; then
                success "Pre-commit hook includes API key prevention"
            else
                warn "Pre-commit hook may not include API key checking"
                ISSUES_FOUND+=("Pre-commit hook missing API key prevention")
            fi
        else
            error "Pre-commit hook is not executable"
            ISSUES_FOUND+=("Pre-commit hook not executable")
            AUDIT_PASSED=false
        fi
    else
        error "Pre-commit hook not installed"
        ISSUES_FOUND+=("Pre-commit hook not installed")
        AUDIT_PASSED=false
    fi
}

audit_environment_configuration() {
    header "4. Validating Environment Configuration..."

    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        success ".env file exists"

        # Check for common environment variables
        local env_vars=("OPENROUTER_API_KEY" "PERPLEXITY_API_KEY" "ARCHON_URL")
        local found_vars=()

        for var in "${env_vars[@]}"; do
            if grep -q "^${var}=" "$PROJECT_ROOT/.env"; then
                found_vars+=("$var")
            fi
        done

        if [[ ${#found_vars[@]} -gt 0 ]]; then
            success "Found environment variables: ${found_vars[*]}"
        else
            warn "No common environment variables found in .env"
        fi

        # Check for empty values
        local empty_vars=()
        for var in "${found_vars[@]}"; do
            if grep -q "^${var}=\"\"" "$PROJECT_ROOT/.env"; then
                empty_vars+=("$var")
            fi
        done

        if [[ ${#empty_vars[@]} -gt 0 ]]; then
            warn "Empty environment variables: ${empty_vars[*]}"
            ISSUES_FOUND+=("Empty environment variables in .env")
        fi
    else
        warn ".env file not found"
        ISSUES_FOUND+=("Missing .env file")
        AUDIT_PASSED=false
    fi
}

audit_documentation_security() {
    header "5. Auditing Documentation Security..."

    local doc_files=$(find "$PROJECT_ROOT/docs" "$PROJECT_ROOT/GUIDES" -name "*.md" 2>/dev/null || true)
    local issues_found=false

    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            # Check for real API key patterns in documentation
            if grep -q "sk-or-v1-[A-Za-z0-9]{48}" "$file" 2>/dev/null; then
                warn "Potential real API key in documentation: $file"
                ISSUES_FOUND+=("Real API key pattern in $file")
                issues_found=true
                AUDIT_PASSED=false
            fi

            # Check for hardcoded assignment patterns
            if grep -q "api_key.*=.*\"sk-" "$file" 2>/dev/null; then
                warn "Potential hardcoded API key in documentation: $file"
                ISSUES_FOUND+=("Hardcoded API key in $file")
                issues_found=true
                AUDIT_PASSED=false
            fi
        fi
    done <<< "$doc_files"

    if ! $issues_found; then
        success "No security issues found in documentation"
    fi
}

audit_security_files() {
    header "6. Validating Security Files..."

    local required_files=(
        "docs/SECURITY_SETUP_MANDATORY.md"
        "docs/FAKE_API_KEYS.md"
        "bin/prevent_api_key_commits.sh"
        "bin/setup-security.sh"
        ".env.template"
    )

    local missing_files=()

    for file in "${required_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$file" ]]; then
            success "Security file exists: $file"
        else
            missing_files+=("$file")
            ISSUES_FOUND+=("Missing security file: $file")
            AUDIT_PASSED=false
        fi
    done

    if [[ ${#missing_files[@]} -eq 0 ]]; then
        success "All required security files present"
    fi
}

audit_test_files() {
    header "7. Auditing Test Files for Security..."

    local test_files=$(find "$PROJECT_ROOT/tests" -name "*.py" 2>/dev/null || true)
    local issues_found=false

    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            # Check for hardcoded API keys in test files
            if grep -q "sk-or-v1-[A-Za-z0-9]{48}" "$file" 2>/dev/null; then
                warn "Potential real API key in test file: $file"
                ISSUES_FOUND+=("Real API key in test file: $file")
                issues_found=true
                AUDIT_PASSED=false
            fi
        fi
    done <<< "$test_files"

    if ! $issues_found; then
        success "No security issues found in test files"
    fi
}

generate_audit_report() {
    header "🔍 Security Audit Report"
    echo

    if $AUDIT_PASSED; then
        success "✅ SECURITY AUDIT PASSED"
        echo
        echo -e "${GREEN}All security checks passed successfully!${NC}"
        echo
        echo -e "${BLUE}Security Status:${NC}"
        echo " • No API key exposure detected"
        echo " • Pre-commit hooks properly configured"
        echo " • Environment configuration validated"
        echo " • Documentation follows security standards"
        echo " • All required security files present"
        echo
        info "Repository is secure for development work"
    else
        error "❌ SECURITY AUDIT FAILED"
        echo
        error "Security issues found that must be addressed:"
        for issue in "${ISSUES_FOUND[@]}"; do
            echo " • $issue"
        done
        echo
        echo -e "${YELLOW}Recommended Actions:${NC}"
        echo "1. Run: ./bin/setup-security.sh --force"
        echo "2. Address each issue listed above"
        echo "3. Re-run this audit: ./bin/audit-security.sh"
        echo "4. Do not commit changes until audit passes"
        echo
        warn "Repository is NOT secure for development work"
    fi

    echo
    echo -e "${BLUE}Audit completed at: $(date)${NC}"
    echo
}

# Main execution
main() {
    header "🔍 OOS Security Audit"
    echo "Comprehensive security audit for OOS development environment"
    echo

    # Check if we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        error "Not in a git repository. Security audit requires git."
        exit 1
    fi

    # Run all audit checks
    audit_api_key_exposure
    audit_gitignore_configuration
    audit_pre_commit_hook
    audit_environment_configuration
    audit_documentation_security
    audit_security_files
    audit_test_files

    # Generate report
    generate_audit_report

    # Exit with appropriate code
    if $AUDIT_PASSED; then
        exit 0
    else
        exit 1
    fi
}

# Help message
show_help() {
    cat << EOF
OOS Security Audit

Usage: $0 [options]

Options:
  --help, -h     Show this help message
  --quiet        Suppress verbose output
  --report-file  Save report to file (default: .oos/security-audit-report.txt)

Description:
This script performs a comprehensive security audit of your OOS development
environment, checking for:
- API key exposure in repository
- .gitignore configuration
- Pre-commit hook installation
- Environment configuration
- Documentation security
- Required security files

Run this periodically to ensure your development environment remains secure.
EOF
}

# Parse arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --quiet)
        # Redirect all output to /dev/null except final result
        main >/dev/null 2>&1
        if $AUDIT_PASSED; then
            echo "PASSED"
            exit 0
        else
            echo "FAILED"
            exit 1
        fi
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