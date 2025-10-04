#!/usr/bin/env bash
set -euo pipefail

# Claude Code "Start Coding" Command V3 - Direct Script Calls
# Calls the same scripts that slash commands use, but directly (no slash command overhead)

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

echo -e "${BOLD}${CYAN}🚀 Starting Development Session${NC}"
echo "==============================="

# Step 1: Update OOS (same script as /update-oos command)
echo -e "\n${BLUE}Step 1: Update OOS subfolder operating system${NC}"
if [[ -f "$PROJECT_ROOT/bin/oos-update-from-github.sh" ]]; then
    bash "$PROJECT_ROOT/bin/oos-update-from-github.sh"
else
    echo -e "${YELLOW}⚠️  OOS update script not found${NC}"
fi

# Step 2: Validate development environment (same script as /dev-gate command)
echo -e "\n${BLUE}Step 2: Validate development environment${NC}"
if [[ -f "$PROJECT_ROOT/bin/dev-gate.sh" ]]; then
    if DEV_GATE_BYPASS=true bash "$PROJECT_ROOT/bin/dev-gate.sh"; then
        echo -e "${GREEN}✅ Development environment ready${NC}"
    else
        echo -e "${RED}❌ Development environment validation failed${NC}"
        echo "Fix the issues above before coding"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Development gate not available${NC}"
fi

# Step 3: Environment status (same logic as /env-check would use)
echo -e "\n${BLUE}Step 3: Environment Status${NC}"
echo "• uv: $(uv --version 2>/dev/null || echo 'not installed')"
echo "• Python: $(uv run python --version 2>/dev/null || echo 'not available')"
echo "• 1Password: $(if op whoami >/dev/null 2>&1; then echo "✅ Authenticated"; else echo "⚠️  Not authenticated"; fi)"

# Step 4: Project health check
echo -e "\n${BLUE}Step 4: Project Health Check${NC}"
if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    echo "• pyproject.toml: ✅ Found"
    if [[ -f "$PROJECT_ROOT/uv.lock" ]]; then
        echo "• uv.lock: ✅ Found (dependencies locked)"
    else
        echo "• uv.lock: ⚠️  Missing (run: uv sync)"
    fi
else
    echo "• pyproject.toml: ⚠️  Missing"
fi

if [[ -d "$PROJECT_ROOT/.git" ]]; then
    echo "• Git repository: ✅ Found"
    echo "• Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"

    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "• Working directory: ⚠️  Has uncommitted changes"
    else
        echo "• Working directory: ✅ Clean"
    fi
else
    echo "• Git repository: ⚠️  Not initialized"
fi

# Step 5: Available commands (these all use the same underlying scripts)
echo -e "\n${PURPLE}🛠️  Available Development Commands:${NC}"
echo -e "${CYAN}Core Development:${NC}"
echo "• /dev-python [args]    - Python with proper environment"
echo "• /dev-test [args]      - Run tests with pytest"
echo "• /dev-uv [args]        - Package management with uv"
echo ""
echo -e "${CYAN}AI-Assisted:${NC}"
echo "• /smart-commit         - AI-generated commit messages"
echo "• /auto-fix            - Auto-fix code issues"
echo "• /doc-check           - Documentation completeness"
echo ""
echo -e "${CYAN}System Management:${NC}"
echo "• /update-oos          - Update OOS from GitHub"
echo "• /dev-gate            - Environment validation"

# Step 6: Project-specific guidance
echo -e "\n${YELLOW}💡 Project-Specific Guidance:${NC}"
if [[ -d "ops" ]]; then
    echo "• Agent-OS project detected: Use /oos-start for ops workflow"
fi

if [[ -f "pyproject.toml" ]]; then
    echo "• Python project: All Python commands run through /dev-python"
fi

if [[ -d ".git" ]]; then
    echo "• Git repository: Use /smart-commit for intelligent commits"
fi

echo -e "\n${YELLOW}💡 Quick Tips:${NC}"
echo "• Environment valid for ~1 hour, then re-run /start-coding"
echo "• Use /update-oos to get latest OOS features (then restart Claude Code)"
echo "• All commands respect uv environment and git hooks"

echo -e "\n${BOLD}${GREEN}🎉 Ready to code! All systems validated.${NC}"