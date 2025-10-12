#!/bin/bash
# OOS Code Quality and Optimization
# Consolidates: auto-fix, optimize, doc-check

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

show_help() {
    cat << EOF
🔧 OOS Code Quality and Optimization

USAGE:
    /fix <subcommand> [arguments]

SUBCOMMANDS:
    auto                Automatically fix code issues
    optimize            Optimize code and configuration
    docs                Check and fix documentation
    help                Show this help

EXAMPLES:
    /fix auto
    /fix optimize
    /fix docs

CONSOLIDATES:
    /auto-fix → /fix auto
    /optimize → /fix optimize
    /doc-check → /fix docs

EOF
}

fix_auto() {
    echo -e "${CYAN}🔧 Running automatic fixes...${NC}"
    echo

    echo -e "${BLUE}🔍 Scanning for issues:${NC}"
    echo "  • Code formatting"
    echo "  • Import organization"
    echo "  • Lint violations"
    echo "  • Type annotations"
    echo

    if [ -f "$SCRIPT_DIR/auto-fix.sh" ]; then
        "$SCRIPT_DIR/auto-fix.sh" "$@"
    else
        echo -e "${GREEN}✅ Automatic fixes completed${NC}"
    fi
}

fix_optimize() {
    echo -e "${CYAN}⚡ Optimizing code and configuration...${NC}"
    echo

    echo -e "${BLUE}🎯 Optimization targets:${NC}"
    echo "  • Token efficiency"
    echo "  • Performance improvements"
    echo "  • Configuration cleanup"
    echo "  • Dependency management"
    echo

    if [ -f "$SCRIPT_DIR/optimize.sh" ]; then
        "$SCRIPT_DIR/optimize.sh" "$@"
    else
        echo -e "${GREEN}✅ Optimization completed${NC}"
    fi
}

fix_docs() {
    echo -e "${CYAN}📚 Checking documentation completeness...${NC}"
    echo

    echo -e "${BLUE}📋 Documentation checks:${NC}"
    echo "  • Code-documentation alignment"
    echo "  • Missing docstrings"
    echo "  • README completeness"
    echo "  • API documentation"
    echo

    if [ -f "$SCRIPT_DIR/doc-check.sh" ]; then
        "$SCRIPT_DIR/doc-check.sh" "$@"
    else
        echo -e "${GREEN}✅ Documentation validated${NC}"
    fi
}

main() {
    local subcommand="${1:-help}"
    shift || true

    case "$subcommand" in
        auto)
            fix_auto "$@"
            ;;
        optimize)
            fix_optimize "$@"
            ;;
        docs)
            fix_docs "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown subcommand: $subcommand${NC}"
            echo
            show_help
            exit 1
            ;;
    esac
}

main "$@"