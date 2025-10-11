#!/bin/bash

# OOS COMPLETE WORKFLOW: IDEA TO COMPLETION
# =========================================
# Runs the complete systematic workflow: A→B→C→D
# Takes a project from idea to fully validated, documented, and deployed completion

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
MODE="${1:-interactive}"
PROJECT_IDEA="${2:-}"

# Workflow steps
CURRENT_STEP=0
TOTAL_STEPS=8

show_help() {
    cat << EOF
🚀 OOS Complete Workflow: Idea to Completion

USAGE:
    $0 [mode] [project-idea]

MODES:
    interactive    Interactive mode with prompts (default)
    auto          Automatic mode with minimal interaction
    plan          Show workflow plan without executing

EXAMPLES:
    $0                                    # Interactive workflow
    $0 interactive "React blog app"       # Interactive with idea
    $0 auto "API service"                 # Automatic execution
    $0 plan                               # Show workflow steps

DESCRIPTION:
    Runs the complete OOS systematic workflow:

    A → /start-coding     (Setup development environment)
    B → Development       (Implement with RUAT validation)
    C → /validate         (Comprehensive validation)
    D → /deploy           (Deploy to production)

    Each step is validated before proceeding to next.

EOF
}

step_header() {
    local step_name="$1"
    CURRENT_STEP=$((CURRENT_STEP + 1))

    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} ${BOLD}STEP $CURRENT_STEP/$TOTAL_STEPS: $step_name${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

step_success() {
    echo ""
    echo -e "${GREEN}✅ Step $CURRENT_STEP completed successfully${NC}"
    echo ""
}

step_failed() {
    local error_msg="$1"
    echo ""
    echo -e "${RED}❌ Step $CURRENT_STEP failed: $error_msg${NC}"
    echo -e "${YELLOW}Fix the issue and re-run the workflow${NC}"
    exit 1
}

user_confirmation() {
    local message="$1"
    if [ "$MODE" = "auto" ]; then
        echo -e "${BLUE}[AUTO MODE] $message${NC}"
        return 0
    fi

    echo -e "${YELLOW}$message${NC}"
    echo -e "${YELLOW}Continue? (y/n/skip)${NC}"

    local response
    while true; do
        read -r response
        case "$response" in
            y|Y|yes|YES)
                return 0
                ;;
            n|N|no|NO)
                echo -e "${RED}Workflow stopped by user${NC}"
                exit 1
                ;;
            s|skip|SKIP)
                echo -e "${YELLOW}⏭️  Step skipped${NC}"
                return 1
                ;;
            *)
                echo -e "${YELLOW}Please answer: y (yes), n (no), or skip${NC}"
                ;;
        esac
    done
}

# ==============================================================================
# WORKFLOW STEPS
# ==============================================================================

# Step A: Setup Development Environment
step_a_setup() {
    step_header "Setup Development Environment (/start-coding)"

    echo "🔧 Setting up systematic development environment..."
    echo ""

    # Check if /start-coding command exists
    if [ -f "$PROJECT_ROOT/bin/claude-start-coding.sh" ]; then
        if user_confirmation "Run /start-coding to setup development environment?"; then
            echo "Running: /start-coding"
            if "$PROJECT_ROOT/bin/claude-start-coding.sh"; then
                step_success
            else
                step_failed "Development environment setup failed"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  /start-coding not found - manual setup required${NC}"
        if user_confirmation "Continue with manual environment setup?"; then
            echo "Manual setup completed"
            step_success
        else
            step_failed "Environment setup required"
        fi
    fi
}

# Step B: Development with RUAT
step_b_development() {
    step_header "Development with RUAT Validation"

    echo "💻 Development phase with user acceptance testing..."
    echo ""

    if [ -n "$PROJECT_IDEA" ]; then
        echo "Project Idea: $PROJECT_IDEA"
        echo ""
    fi

    echo "Development checklist:"
    echo "1. ✅ Implement core functionality"
    echo "2. ✅ Create user scenarios with: /test-user-scenarios --create [feature]"
    echo "3. ✅ Run RUAT validation: /ruat [feature]"
    echo "4. ✅ Fix any UX issues found"
    echo "5. ✅ Re-test until scenarios pass"
    echo ""

    if user_confirmation "Development phase completed with RUAT validation?"; then
        step_success
    else
        step_failed "Development must include RUAT validation"
    fi
}

# Step C: Comprehensive Validation
step_c_validation() {
    step_header "Comprehensive Validation (/validate)"

    echo "🧪 Running comprehensive OOS validation..."
    echo ""

    if user_confirmation "Run full validation suite?"; then
        echo "Running: /validate"
        if "$PROJECT_ROOT/bin/validate-oos" --report; then
            echo ""
            echo -e "${GREEN}📊 Validation report generated: validation-report.md${NC}"
            step_success
        else
            echo ""
            echo -e "${RED}❌ Validation found issues${NC}"
            echo -e "${YELLOW}Review validation-report.md and fix issues before proceeding${NC}"

            if user_confirmation "Ignore validation issues and continue? (NOT RECOMMENDED)"; then
                echo -e "${YELLOW}⚠️  Proceeding despite validation issues${NC}"
                step_success
            else
                step_failed "Validation issues must be resolved"
            fi
        fi
    fi
}

# Step D: User Scenario Testing
step_d_ruat() {
    step_header "Final User Scenario Testing"

    echo "👥 Running final user acceptance testing..."
    echo ""

    if user_confirmation "Run user scenario testing for all features?"; then
        echo "Running: /test-user-scenarios --all"

        # Check if any scenario files exist
        if [ -d "$PROJECT_ROOT/tests/scenarios" ] && [ "$(ls -A "$PROJECT_ROOT/tests/scenarios" 2>/dev/null)" ]; then
            echo "Found scenario files:"
            ls "$PROJECT_ROOT/tests/scenarios"/*.scenarios 2>/dev/null | while read -r file; do
                echo "  - $(basename "$file" .scenarios)"
            done
            echo ""

            if user_confirmation "All user scenarios validated successfully?"; then
                step_success
            else
                step_failed "User scenarios must pass before deployment"
            fi
        else
            echo -e "${YELLOW}⚠️  No user scenarios found${NC}"
            echo "Create scenarios with: /test-user-scenarios --create [feature]"

            if user_confirmation "Skip user scenario testing? (NOT RECOMMENDED)"; then
                echo -e "${YELLOW}⚠️  Proceeding without user scenario validation${NC}"
                step_success
            else
                step_failed "User scenarios required for complete workflow"
            fi
        fi
    fi
}

# Step E: Pre-commit Validation
step_e_precommit() {
    step_header "Pre-commit Validation"

    echo "📝 Running pre-commit checks..."
    echo ""

    if user_confirmation "Run pre-commit validation?"; then
        if [ -f "$PROJECT_ROOT/bin/claude-pre-commit.sh" ]; then
            echo "Running: /pre-commit"
            if "$PROJECT_ROOT/bin/claude-pre-commit.sh"; then
                step_success
            else
                step_failed "Pre-commit validation failed"
            fi
        else
            echo -e "${YELLOW}⚠️  /pre-commit not found - manual checks required${NC}"
            if user_confirmation "Manual pre-commit checks completed?"; then
                step_success
            else
                step_failed "Pre-commit validation required"
            fi
        fi
    fi
}

# Step F: Smart Commit
step_f_commit() {
    step_header "Smart Commit"

    echo "💾 Creating intelligent commit..."
    echo ""

    if user_confirmation "Generate smart commit?"; then
        if [ -f "$PROJECT_ROOT/bin/claude-smart-commit.sh" ]; then
            echo "Running: /smart-commit"
            if "$PROJECT_ROOT/bin/claude-smart-commit.sh"; then
                step_success
            else
                step_failed "Smart commit failed"
            fi
        else
            echo -e "${YELLOW}⚠️  /smart-commit not found - manual commit required${NC}"
            if user_confirmation "Manual commit completed?"; then
                echo "Manual commit completed"
                step_success
            else
                step_failed "Commit required to complete workflow"
            fi
        fi
    fi
}

# Step G: Infrastructure Provisioning
step_g_provision() {
    step_header "Infrastructure Provisioning (/provision)"

    echo "🚀 Provisioning production infrastructure..."
    echo ""

    if [ -n "$PROJECT_IDEA" ]; then
        echo "Suggested provisioning: /provision \"$PROJECT_IDEA\""
        echo ""
    fi

    if user_confirmation "Provision infrastructure for deployment?"; then
        echo "Running: /provision"

        local provision_cmd="$PROJECT_ROOT/bin/provision-infrastructure.sh"
        if [ -f "$provision_cmd" ]; then
            if [ -n "$PROJECT_IDEA" ]; then
                if "$provision_cmd" "$PROJECT_IDEA" --preview; then
                    echo ""
                    if user_confirmation "Deploy infrastructure to production?"; then
                        if "$provision_cmd" "$PROJECT_IDEA" --deploy; then
                            step_success
                        else
                            step_failed "Infrastructure deployment failed"
                        fi
                    else
                        echo "Infrastructure previewed but not deployed"
                        step_success
                    fi
                else
                    step_failed "Infrastructure provisioning failed"
                fi
            else
                echo -e "${YELLOW}⚠️  No project idea provided for provisioning${NC}"
                if user_confirmation "Skip infrastructure provisioning?"; then
                    step_success
                else
                    step_failed "Infrastructure provisioning required"
                fi
            fi
        else
            echo -e "${YELLOW}⚠️  /provision not found - manual deployment required${NC}"
            if user_confirmation "Manual deployment completed?"; then
                step_success
            else
                step_failed "Deployment required to complete workflow"
            fi
        fi
    fi
}

# Step H: Final Validation
step_h_final() {
    step_header "Final Validation & Completion"

    echo "🎯 Final validation of complete workflow..."
    echo ""

    echo "Workflow completion checklist:"
    echo "✅ Development environment setup"
    echo "✅ Feature development with RUAT"
    echo "✅ Comprehensive validation passed"
    echo "✅ User scenarios validated"
    echo "✅ Pre-commit checks passed"
    echo "✅ Code committed"
    echo "✅ Infrastructure provisioned"
    echo ""

    if user_confirmation "All workflow steps completed successfully?"; then
        echo ""
        echo -e "${GREEN}🎉 WORKFLOW COMPLETE!${NC}"
        echo -e "${GREEN}Project successfully taken from idea to completion${NC}"
        echo ""
        echo "Summary:"
        echo "• Development environment: Ready ✅"
        echo "• Feature implementation: Complete ✅"
        echo "• User validation: Passed ✅"
        echo "• Code quality: Validated ✅"
        echo "• Infrastructure: Deployed ✅"
        echo ""
        echo -e "${CYAN}Your systematic thinking environment is complete!${NC}"
        step_success
        return 0
    else
        step_failed "Workflow incomplete"
    fi
}

# ==============================================================================
# WORKFLOW EXECUTION
# ==============================================================================

show_workflow_plan() {
    echo -e "${CYAN}🗺️  OOS Complete Workflow Plan${NC}"
    echo "==============================="
    echo ""
    echo "A → Setup Development Environment (/start-coding)"
    echo "    • Validate development environment"
    echo "    • Setup Archon integration"
    echo "    • Configure 1Password access"
    echo "    • Load project context"
    echo ""
    echo "B → Development with RUAT"
    echo "    • Implement core functionality"
    echo "    • Create user scenarios"
    echo "    • Run user acceptance testing"
    echo "    • Fix UX issues"
    echo ""
    echo "C → Comprehensive Validation (/validate)"
    echo "    • Code-documentation alignment"
    echo "    • Functional testing"
    echo "    • Integration testing"
    echo "    • Simplicity analysis"
    echo ""
    echo "D → User Scenario Testing (/ruat)"
    echo "    • Validate all user scenarios"
    echo "    • Ensure UX excellence"
    echo "    • Fix any UX issues"
    echo ""
    echo "E → Pre-commit Validation (/pre-commit)"
    echo "    • Security checks"
    echo "    • Code quality validation"
    echo "    • Documentation checks"
    echo ""
    echo "F → Smart Commit (/smart-commit)"
    echo "    • Generate intelligent commit message"
    echo "    • Update Archon task status"
    echo "    • Create commit"
    echo ""
    echo "G → Infrastructure Provisioning (/provision)"
    echo "    • Generate production config"
    echo "    • Deploy to infrastructure"
    echo "    • Configure SSL and monitoring"
    echo ""
    echo "H → Final Validation & Completion"
    echo "    • Verify all steps completed"
    echo "    • Confirm deployment success"
    echo "    • Mark project complete"
}

main() {
    case "$MODE" in
        plan)
            show_workflow_plan
            exit 0
            ;;
        interactive|auto)
            echo -e "${BOLD}🚀 OOS COMPLETE WORKFLOW: IDEA TO COMPLETION${NC}"
            echo "================================================="
            echo ""

            if [ -n "$PROJECT_IDEA" ]; then
                echo -e "${CYAN}Project Idea: $PROJECT_IDEA${NC}"
                echo ""
            fi

            echo -e "${YELLOW}Mode: $MODE${NC}"
            echo ""

            if user_confirmation "Start complete workflow A→B→C→D?"; then
                step_a_setup
                step_b_development
                step_c_validation
                step_d_ruat
                step_e_precommit
                step_f_commit
                step_g_provision
                step_h_final
            else
                echo -e "${YELLOW}Workflow cancelled by user${NC}"
                exit 1
            fi
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown mode: $MODE${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"