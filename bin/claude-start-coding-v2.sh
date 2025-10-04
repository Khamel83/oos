#!/usr/bin/env bash
set -euo pipefail

# Claude Code "Start Coding" Command V2 - Compositor Architecture
# Calls focused, smaller slash commands that can be updated independently

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Helper function to run other slash commands
run_slash_command() {
    local cmd_name="$1"
    shift || true

    echo -e "${BLUE}▶️  Running /$cmd_name${NC}"
    if bash "$PROJECT_ROOT/bin/claude-run-command.sh" "$cmd_name" "$@"; then
        echo -e "${GREEN}✅ /$cmd_name completed${NC}"
        return 0
    else
        echo -e "${RED}❌ /$cmd_name failed${NC}"
        return 1
    fi
}

echo -e "${BOLD}${CYAN}🚀 Starting Development Session (Compositor v2)${NC}"
echo "=============================================="

# Step 1: Update OOS (always first)
echo -e "\n${BLUE}Step 1: Update OOS subfolder operating system${NC}"
if ! run_slash_command "update-oos"; then
    echo -e "${YELLOW}⚠️  OOS update failed, continuing with current version${NC}"
fi

# Step 2: Validate development environment
echo -e "\n${BLUE}Step 2: Validate development environment${NC}"
if ! run_slash_command "dev-gate"; then
    echo -e "${RED}❌ Development environment validation failed${NC}"
    echo "Fix the issues above before coding"
    exit 1
fi

# Step 3: Check environment status
echo -e "\n${BLUE}Step 3: Environment status check${NC}"
if ! run_slash_command "env-check"; then
    echo -e "${YELLOW}⚠️  Environment check had warnings${NC}"
fi

# Step 4: Show available commands
echo -e "\n${PURPLE}🛠️  Development Workflow Commands:${NC}"
echo -e "${CYAN}Primary:${NC}"
echo "• /dev-python [args]    - Run Python with proper environment"
echo "• /dev-test [args]      - Run tests with pytest"
echo "• /dev-uv [args]        - Package management with uv"
echo ""
echo -e "${CYAN}Utilities:${NC}"
echo "• /smart-commit         - AI-generated commit messages"
echo "• /auto-fix            - Auto-fix code issues"
echo "• /doc-check           - Documentation completeness"
echo ""
echo -e "${CYAN}System:${NC}"
echo "• /update-oos          - Update OOS from GitHub"
echo "• /dev-gate            - Run environment validation"
echo "• /env-check           - Check system status"

# Step 5: Project-specific tips
echo -e "\n${YELLOW}💡 Project Tips:${NC}"
if [[ -d "ops" ]]; then
    echo "• Agent-OS project: Use /oos-start for ops workflow"
fi

if [[ -f "pyproject.toml" ]]; then
    echo "• Python project: Use /dev-python for all Python commands"
fi

if [[ -d ".git" ]]; then
    echo "• Git repository: Use /smart-commit for intelligent commits"
fi

echo -e "\n${BOLD}${GREEN}🎉 Ready to code! All systems validated.${NC}"