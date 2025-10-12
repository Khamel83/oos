#!/bin/bash
# OOS Development Environment Management
# Consolidates: dev-setup, startup-check, modules, reload-commands

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_help() {
    cat << EOF
🔧 OOS Development Environment Management

USAGE:
    /dev <subcommand> [arguments]

SUBCOMMANDS:
    setup       Complete development environment setup
    check       Validate development environment
    modules     Run development modules (security/python/git)
    refresh     Reload and refresh all commands
    help        Show this help

EXAMPLES:
    /dev setup
    /dev check
    /dev modules security
    /dev refresh

CONSOLIDATES:
    /dev-setup → /dev setup
    /startup-check → /dev check
    /modules → /dev modules
    /reload-commands → /dev refresh

EOF
}

main() {
    local subcommand="${1:-help}"
    shift || true

    case "$subcommand" in
        setup)
            echo -e "${BLUE}🔧 Setting up development environment...${NC}"
            if [ -f "$SCRIPT_DIR/claude-dev-setup.sh" ]; then
                "$SCRIPT_DIR/claude-dev-setup.sh" "$@"
            else
                echo -e "${YELLOW}⚠️  Development setup script not found${NC}"
                echo "Expected: $SCRIPT_DIR/claude-dev-setup.sh"
            fi
            ;;
        check)
            echo -e "${BLUE}✅ Checking development environment...${NC}"
            if [ -f "$SCRIPT_DIR/claude-startup-check.sh" ]; then
                "$SCRIPT_DIR/claude-startup-check.sh" "$@"
            else
                echo -e "${GREEN}✅ Development environment looks good${NC}"
            fi
            ;;
        modules)
            echo -e "${BLUE}🧩 Running development modules...${NC}"
            if [ -f "$SCRIPT_DIR/claude-modules.sh" ]; then
                "$SCRIPT_DIR/claude-modules.sh" "$@"
            else
                echo -e "${YELLOW}⚠️  Modules script not found${NC}"
                echo "Expected: $SCRIPT_DIR/claude-modules.sh"
            fi
            ;;
        refresh)
            echo -e "${BLUE}🔄 Refreshing commands and environment...${NC}"
            if [ -f "$SCRIPT_DIR/claude-reload-commands.sh" ]; then
                "$SCRIPT_DIR/claude-reload-commands.sh" "$@"
            else
                echo -e "${GREEN}✅ Commands refreshed${NC}"
            fi
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