#!/bin/bash
# OOS 1Password Operations and Authentication
# Consolidates: op-signin, op-status, op-setup, op-get, op-secret, op-session, op-session-automated

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
🔐 1Password Operations and Authentication

USAGE:
    /op <subcommand> [arguments]

SUBCOMMANDS:
    signin              Sign into 1Password CLI
    status              Check 1Password connection status
    setup               Setup 1Password integration
    get <item>          Get item from 1Password
    secret <item>       Get secret from 1Password
    session             Manage 1Password session
    help                Show this help

EXAMPLES:
    /op signin
    /op status
    /op setup
    /op get "bootstrap-env"
    /op secret "api-key"

CONSOLIDATES:
    /op-signin → /op signin
    /op-status → /op status
    /op-setup → /op setup
    /op-get → /op get
    /op-secret → /op secret
    /op-session → /op session
    /op-session-automated → /op session automated

EOF
}

op_signin() {
    echo -e "${BLUE}🔐 Signing into 1Password...${NC}"

    if command -v op >/dev/null 2>&1; then
        if op account list >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Already signed in to 1Password${NC}"
            op account list
        else
            echo "Please sign in to 1Password:"
            eval $(op signin)
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Successfully signed into 1Password${NC}"
            else
                echo -e "${RED}❌ Failed to sign into 1Password${NC}"
                return 1
            fi
        fi
    else
        echo -e "${RED}❌ 1Password CLI not found${NC}"
        echo "Install with: brew install 1password-cli"
        return 1
    fi
}

op_status() {
    echo -e "${CYAN}📊 1Password Status${NC}"
    echo "==================="
    echo

    if command -v op >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 1Password CLI installed${NC}"

        if op account list >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Signed in to 1Password${NC}"
            echo
            echo "Accounts:"
            op account list
        else
            echo -e "${YELLOW}⚠️  Not signed in to 1Password${NC}"
            echo "Run: /op signin"
        fi
    else
        echo -e "${RED}❌ 1Password CLI not installed${NC}"
        echo "Install with: brew install 1password-cli"
    fi
}

op_setup() {
    echo -e "${BLUE}🔧 Setting up 1Password integration...${NC}"

    # Check if 1Password CLI is installed
    if ! command -v op >/dev/null 2>&1; then
        echo -e "${RED}❌ 1Password CLI not found${NC}"
        echo "Installing 1Password CLI..."
        if command -v brew >/dev/null 2>&1; then
            brew install 1password-cli
        else
            echo "Please install 1Password CLI manually"
            return 1
        fi
    fi

    # Setup integration
    echo -e "${GREEN}✅ 1Password CLI ready${NC}"
    echo "Next: Run /op signin to authenticate"
}

op_get() {
    local item="$*"

    if [ -z "$item" ]; then
        echo -e "${RED}❌ Please specify an item to get${NC}"
        echo "Usage: /op get <item-name>"
        return 1
    fi

    echo -e "${BLUE}🔍 Getting item: $item${NC}"

    if command -v op >/dev/null 2>&1 && op account list >/dev/null 2>&1; then
        op item get "$item" --format json | jq -r '.fields[] | "\(.label): \(.value)"' 2>/dev/null || {
            echo "Item: $item"
            echo -e "${YELLOW}⚠️  Use 1Password app or CLI directly for sensitive data${NC}"
        }
    else
        echo -e "${RED}❌ Not signed in to 1Password${NC}"
        echo "Run: /op signin"
        return 1
    fi
}

op_secret() {
    local item="$*"

    if [ -z "$item" ]; then
        echo -e "${RED}❌ Please specify a secret to get${NC}"
        echo "Usage: /op secret <item-name>"
        return 1
    fi

    echo -e "${BLUE}🔒 Getting secret: $item${NC}"
    echo -e "${YELLOW}⚠️  Secrets not displayed for security${NC}"
    echo "Use 1Password app or CLI directly for sensitive data"
}

op_session() {
    local action="${1:-status}"

    case "$action" in
        status)
            echo -e "${CYAN}📊 1Password Session Status${NC}"
            if op account list >/dev/null 2>&1; then
                echo -e "${GREEN}✅ Active session${NC}"
                op account list
            else
                echo -e "${YELLOW}⚠️  No active session${NC}"
            fi
            ;;
        automated)
            echo -e "${BLUE}🤖 Setting up automated session...${NC}"
            echo -e "${YELLOW}⚠️  Automated session setup not implemented yet${NC}"
            ;;
        *)
            echo -e "${RED}❌ Unknown session action: $action${NC}"
            echo "Usage: /op session [status|automated]"
            ;;
    esac
}

main() {
    local subcommand="${1:-help}"
    shift || true

    case "$subcommand" in
        signin)
            op_signin "$@"
            ;;
        status)
            op_status "$@"
            ;;
        setup)
            op_setup "$@"
            ;;
        get)
            op_get "$@"
            ;;
        secret)
            op_secret "$@"
            ;;
        session)
            op_session "$@"
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