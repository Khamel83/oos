#!/bin/bash

# OOS Pre-Commit Validation Composition
# Security scan + lint + tests + AI commit message preparation
# Ensures code quality and security before commits

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${CYAN}🔍 OOS Pre-Commit Validation${NC}"
echo -e "${CYAN}============================${NC}"
echo ""

# Track validation results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

# Function to run a validation step
run_validation() {
    local check_name="$1"
    local script_path="$2"
    local description="$3"
    local is_critical="${4:-true}"

    echo -e "${BLUE}🔍 $check_name${NC}"
    echo -e "   $description"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [[ -f "$script_path" ]]; then
        if "$script_path" "$@" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $check_name passed${NC}"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            echo ""
            return 0
        else
            if [[ "$is_critical" == "true" ]]; then
                echo -e "${RED}❌ $check_name failed (CRITICAL)${NC}"
                FAILED_CHECKS=$((FAILED_CHECKS + 1))
            else
                echo -e "${YELLOW}⚠️  $check_name warning (non-critical)${NC}"
                WARNINGS=$((WARNINGS + 1))
            fi
            echo ""
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  $check_name script not found: $script_path${NC}"
        WARNINGS=$((WARNINGS + 1))
        echo ""
        return 1
    fi
}

# Function to run validation with output
run_validation_with_output() {
    local check_name="$1"
    local script_path="$2"
    local description="$3"

    echo -e "${BLUE}🔍 $check_name${NC}"
    echo -e "   $description"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [[ -f "$script_path" ]]; then
        if "$script_path" "$@"; then
            echo -e "${GREEN}✅ $check_name passed${NC}"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            echo ""
            return 0
        else
            echo -e "${RED}❌ $check_name failed${NC}"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            echo ""
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  $check_name script not found: $script_path${NC}"
        WARNINGS=$((WARNINGS + 1))
        echo ""
        return 1
    fi
}

# Pre-commit validations

# 1. Git Status Check
echo -e "${BLUE}🔍 Git Status Check${NC}"
echo -e "   Ensuring there are changes to commit"
if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  No staged changes found. Stage your changes first with 'git add'${NC}"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ Staged changes detected${NC}"
    echo ""
fi

# 2. Security Scan - API Key Prevention
run_validation "API Key Security" "$PROJECT_ROOT/bin/prevent_api_key_commits.sh" "Scanning for accidentally committed API keys" true

# 3. Development Gate (Environment + Security)
run_validation "Development Gate" "$PROJECT_ROOT/bin/dev-gate.sh" "Running security and environment validation" false

# 4. OOS Validation Framework
run_validation_with_output "OOS Validation" "$PROJECT_ROOT/bin/validate-oos" "Running comprehensive OOS validation" false

# 5. Integration Tests
run_validation "Integration Tests" "$PROJECT_ROOT/bin/test_integration.sh" "Running integration test suite" false

# 6. User Scenario Tests (if available)
if [[ -f "$PROJECT_ROOT/bin/test-user-scenarios" ]]; then
    run_validation "User Scenarios" "$PROJECT_ROOT/bin/test-user-scenarios" "Testing user acceptance scenarios" false
fi

# 7. All Commands Test
run_validation "Command Tests" "$PROJECT_ROOT/bin/test-all-commands" "Testing all slash commands" false

# Summary and Decision
echo -e "${CYAN}📊 Pre-Commit Validation Summary${NC}"
echo -e "${CYAN}===============================${NC}"
echo -e "Total checks: $TOTAL_CHECKS"
echo -e "${GREEN}✅ Passed: $PASSED_CHECKS${NC}"

if [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
fi

if [[ $FAILED_CHECKS -gt 0 ]]; then
    echo -e "${RED}❌ Failed: $FAILED_CHECKS${NC}"
    echo ""
    echo -e "${RED}❌ Pre-commit validation failed!${NC}"
    echo -e "   Fix the critical issues above before committing."
    echo ""
    echo -e "${BLUE}💡 Helpful commands:${NC}"
    echo -e "  • ${CYAN}git status${NC} - Check current changes"
    echo -e "  • ${CYAN}git diff --cached${NC} - Review staged changes"
    echo -e "  • ${CYAN}/validate${NC} - Run full OOS validation"
    echo -e "  • ${CYAN}git commit${NC} - Try committing again after fixes"
    exit 1
else
    echo ""
    if [[ $WARNINGS -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  Pre-commit validation passed with warnings${NC}"
        echo -e "   Consider addressing the warnings above."
    else
        echo -e "${GREEN}🎉 All pre-commit validations passed!${NC}"
    fi
    echo ""
    echo -e "${GREEN}✅ Your code is ready to commit safely${NC}"
    echo ""
    echo -e "${BLUE}💡 Next steps:${NC}"
    echo -e "  • Use ${CYAN}/smart-commit${NC} to generate an AI commit message"
    echo -e "  • Or use ${CYAN}git commit${NC} with your own message"
    echo -e "  • Consider running ${CYAN}/complete-workflow${NC} for full systematic process"
fi

# Show staged changes summary
echo ""
echo -e "${BLUE}📝 Staged Changes Summary:${NC}"
git diff --cached --stat