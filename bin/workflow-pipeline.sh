#!/bin/bash

# WORKFLOW PIPELINE - Chain OOS/Archon Commands
# =============================================
# Simple command chaining for quick workflows
# Usage: ./workflow-pipeline.sh [pipeline-name] [args...]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

run_command() {
    local cmd="$1"
    local description="$2"

    echo -e "${BLUE}🔧 $description${NC}"

    local script_path="$PROJECT_ROOT/bin/claude-${cmd}.sh"
    if [ -f "$script_path" ]; then
        echo "Running: /$cmd"
        "$script_path"
    else
        echo -e "${YELLOW}⚠️  /$cmd not found - skipping${NC}"
    fi
    echo ""
}

archon_action() {
    local action="$1"
    local description="$2"

    echo -e "${BLUE}📚 $description${NC}"
    echo "Archon: $action"
    # This would integrate with actual Archon commands
    echo ""
}

# PIPELINE DEFINITIONS
pipeline_quick_start() {
    echo "🚀 QUICK START PIPELINE"
    echo "======================="

    archon_action "research 'project setup best practices'" "Research setup patterns"
    run_command "start-coding" "Setup development environment"
    run_command "dev-gate" "Validate environment"

    echo -e "${GREEN}✅ Quick start complete - ready for development${NC}"
}

pipeline_quality_check() {
    echo "🔍 QUALITY CHECK PIPELINE"
    echo "========================="

    archon_action "research 'quality assurance practices'" "Research QA patterns"
    run_command "ruat" "Run user acceptance tests"
    run_command "validate" "Comprehensive validation"
    run_command "pre-commit" "Pre-commit checks"

    echo -e "${GREEN}✅ Quality check complete${NC}"
}

pipeline_idea_to_plan() {
    local idea="$1"
    echo "💡 IDEA TO PLAN PIPELINE"
    echo "========================"
    echo "Idea: $idea"
    echo ""

    archon_action "research '$idea patterns'" "Research similar projects"
    run_command "brain-dump" "Process idea systematically"
    run_command "clarify" "Clarify requirements"
    run_command "help-me" "Context engineering"

    echo -e "${GREEN}✅ Idea processed into actionable plan${NC}"
}

pipeline_complete_project() {
    echo "🎯 COMPLETE PROJECT PIPELINE"
    echo "============================"

    pipeline_quality_check
    archon_action "capture learnings" "Save patterns and anti-patterns"
    run_command "doc-check" "Documentation check"
    run_command "smart-commit" "Generate commit"

    echo -e "${GREEN}✅ Project completion pipeline done${NC}"
}

# MAIN
main() {
    local pipeline="${1:-help}"
    shift || true

    case "$pipeline" in
        quick-start|qs)
            pipeline_quick_start "$@"
            ;;
        quality-check|qc)
            pipeline_quality_check "$@"
            ;;
        idea-to-plan|itp)
            pipeline_idea_to_plan "$@"
            ;;
        complete-project|cp)
            pipeline_complete_project "$@"
            ;;
        help|--help|-h)
            echo "WORKFLOW PIPELINE - Chain OOS/Archon Commands"
            echo "============================================="
            echo ""
            echo "Available Pipelines:"
            echo "  quick-start (qs)     - Setup development environment"
            echo "  quality-check (qc)   - Run comprehensive quality checks"
            echo "  idea-to-plan (itp)   - Process idea into actionable plan"
            echo "  complete-project (cp) - Final project completion steps"
            echo ""
            echo "Examples:"
            echo "  $0 quick-start"
            echo "  $0 idea-to-plan 'Build a chat bot'"
            echo "  $0 quality-check"
            echo "  $0 complete-project"
            ;;
        *)
            echo "Unknown pipeline: $pipeline"
            echo "Use '$0 help' for available pipelines"
            exit 1
            ;;
    esac
}

main "$@"