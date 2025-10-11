#!/bin/bash

# OOS Startup Health Check
# Ensures slash commands are fresh and working, runs automatically to ensure OOS is ready

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OOS_ROOT="$PROJECT_ROOT"

cd "$PROJECT_ROOT"

echo -e "${CYAN}🚀 OOS Startup Health Check${NC}"
echo -e "${CYAN}==========================${NC}"

# Check if we need to refresh commands
if [[ ! -f ".claude/commands_version.json" ]] || \
   [[ "$(git -C "$OOS_ROOT" rev-parse --short HEAD 2>/dev/null)" != "$(jq -r '.oos_version // "unknown"' .claude/commands_version.json 2>/dev/null)" ]]; then

    echo -e "${BLUE}📥 Detected OOS update or new installation${NC}"
    echo -e "${BLUE}🔄 Refreshing slash commands...${NC}"

    if ./bin/oos-refresh-commands.sh; then
        echo -e "${GREEN}✅ Commands refreshed successfully${NC}"

        # Show key commands that are ready
        echo ""
        echo -e "${CYAN}🎯 Ready to use:${NC}"
        for cmd in complete-workflow validate ruat provision screenshot oos-refresh; do
            if [[ -f ".claude/commands/$cmd.md" ]]; then
                echo -e "  ${GREEN}•${NC} /$cmd"
            fi
        done

    else
        echo -e "${RED}❌ Command refresh failed${NC}"
        echo -e "${YELLOW}🔧 Try manual refresh: /oos-refresh${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ OOS commands are up to date${NC}"

    # Quick validation
    if ./bin/oos-refresh-commands.sh --test-only >/dev/null 2>&1; then
        echo -e "${GREEN}✅ All commands validated${NC}"
    else
        echo -e "${YELLOW}⚠️  Commands need validation - run /oos-refresh${NC}"
    fi
fi

echo ""
echo -e "${BLUE}💡 Run /oos-refresh to manually update commands${NC}"
echo -e "${BLUE}📋 Status: .claude/commands_version.json${NC}"
echo -e "${BLUE}🧪 Tests: .claude/commands_test.log${NC}"

# Additional helpful information for startup
echo ""
echo -e "${CYAN}🔧 OOS Status Summary:${NC}"
echo -e "   Project: $PROJECT_ROOT"
if [[ -f ".claude/commands_version.json" ]]; then
    local version=$(jq -r '.oos_version // "unknown"' .claude/commands_version.json 2>/dev/null)
    local updated=$(jq -r '.updated_at // "unknown"' .claude/commands_version.json 2>/dev/null)
    echo -e "   Commands Version: $version"
    echo -e "   Last Updated: $updated"
else
    echo -e "   Commands Version: ${YELLOW}Not initialized${NC}"
fi

# Show current git status
if git rev-parse --git-dir > /dev/null 2>&1; then
    local current_commit=$(git rev-parse --short HEAD 2>/dev/null)
    echo -e "   Current OOS: $current_commit"
else
    echo -e "   Current OOS: ${YELLOW}Not a git repository${NC}"
fi

echo ""
echo -e "${GREEN}🎉 OOS Startup Health Check Complete!${NC}"