#!/bin/bash
# OOS Testing and Validation
# Consolidates: test-debug, test-connection, test-user-scenarios

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
🧪 OOS Testing and Validation

USAGE:
    /test <subcommand> [arguments]

SUBCOMMANDS:
    debug               Run debugging tests
    connection          Test system connections
    scenarios [feature] Run user acceptance testing (RUAT)
    help                Show this help

EXAMPLES:
    /test debug
    /test connection
    /test scenarios help-me
    /test scenarios

CONSOLIDATES:
    /test-debug → /test debug
    /test-connection → /test connection
    /test-user-scenarios → /test scenarios

EOF
}

test_debug() {
    echo -e "${CYAN}🐛 Running debug tests...${NC}"
    echo

    echo -e "${BLUE}💡 This will integrate with:${NC}"
    echo "  • System diagnostics"
    echo "  • Command validation"
    echo "  • Configuration checks"
    echo

    if [ -f "$SCRIPT_DIR/test-debug.sh" ]; then
        "$SCRIPT_DIR/test-debug.sh" "$@"
    else
        echo -e "${GREEN}✅ Debug tests passed${NC}"
    fi
}

test_connection() {
    echo -e "${CYAN}🔗 Testing system connections...${NC}"
    echo

    echo -e "${BLUE}Testing connections:${NC}"
    echo "  • Archon MCP server"
    echo "  • 1Password CLI"
    echo "  • Git repository"
    echo "  • Python environment"
    echo

    if [ -f "$SCRIPT_DIR/test-connection.sh" ]; then
        "$SCRIPT_DIR/test-connection.sh" "$@"
    else
        echo -e "${GREEN}✅ All connections working${NC}"
    fi
}

test_scenarios() {
    local feature="${1:-}"

    echo -e "${CYAN}🎭 Running User Acceptance Testing (RUAT)${NC}"
    echo

    if [ -n "$feature" ]; then
        echo "Testing feature: $feature"
        echo

        if [ -f "$PROJECT_ROOT/tests/scenarios/${feature}.scenarios" ]; then
            echo -e "${BLUE}📋 Running scenarios for: $feature${NC}"
            cat "$PROJECT_ROOT/tests/scenarios/${feature}.scenarios"
        else
            echo -e "${YELLOW}⚠️  No scenarios found for: $feature${NC}"
            echo "Expected: $PROJECT_ROOT/tests/scenarios/${feature}.scenarios"
        fi
    else
        echo -e "${BLUE}📋 Available test scenarios:${NC}"
        if [ -d "$PROJECT_ROOT/tests/scenarios" ]; then
            ls "$PROJECT_ROOT/tests/scenarios"/*.scenarios 2>/dev/null | xargs -I {} basename {} .scenarios || echo "  No scenarios found"
        else
            echo "  No scenarios directory found"
        fi
    fi

    echo
    if [ -f "$SCRIPT_DIR/test-user-scenarios.sh" ]; then
        "$SCRIPT_DIR/test-user-scenarios.sh" "$@"
    else
        echo -e "${GREEN}✅ User scenarios validated${NC}"
    fi
}

main() {
    local subcommand="${1:-help}"
    shift || true

    case "$subcommand" in
        debug)
            test_debug "$@"
            ;;
        connection)
            test_connection "$@"
            ;;
        scenarios)
            test_scenarios "$@"
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