#!/bin/bash

# OOS Complete Development Environment Setup
# Comprehensive validation: security + python + git + environment
# This is a composition that runs multiple development setup and validation tools

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

echo -e "${CYAN}🚀 OOS Complete Development Environment Setup${NC}"
echo -e "${CYAN}==============================================${NC}"
echo ""

# Function to run a step with error handling
run_step() {
    local step_name="$1"
    local script_path="$2"
    local description="$3"

    echo -e "${BLUE}📋 $step_name${NC}"
    echo -e "   $description"

    if [[ -f "$script_path" ]]; then
        if "$script_path" "$@"; then
            echo -e "${GREEN}✅ $step_name completed successfully${NC}"
            echo ""
            return 0
        else
            echo -e "${RED}❌ $step_name failed${NC}"
            echo ""
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  $step_name script not found: $script_path${NC}"
        echo ""
        return 1
    fi
}

# Track overall success
TOTAL_STEPS=0
SUCCESSFUL_STEPS=0
FAILED_STEPS=0

# Step 1: Python Environment Setup
TOTAL_STEPS=$((TOTAL_STEPS + 1))
if run_step "Python Environment" "$PROJECT_ROOT/bin/setup-uv-environment.sh" "Setting up Python environment with uv"; then
    SUCCESSFUL_STEPS=$((SUCCESSFUL_STEPS + 1))
else
    FAILED_STEPS=$((FAILED_STEPS + 1))
fi

# Step 2: Development Gate (Security + Environment)
TOTAL_STEPS=$((TOTAL_STEPS + 1))
if run_step "Development Gate" "$PROJECT_ROOT/bin/dev-gate.sh" "Running security and environment validation"; then
    SUCCESSFUL_STEPS=$((SUCCESSFUL_STEPS + 1))
else
    FAILED_STEPS=$((FAILED_STEPS + 1))
fi

# Step 3: Git Setup (API Key Protection)
TOTAL_STEPS=$((TOTAL_STEPS + 1))
if run_step "Git Security" "$PROJECT_ROOT/bin/prevent_api_key_commits.sh" "Setting up git hooks to prevent API key commits"; then
    SUCCESSFUL_STEPS=$((SUCCESSFUL_STEPS + 1))
else
    FAILED_STEPS=$((FAILED_STEPS + 1))
fi

# Step 4: Agent OS Setup (if requested)
if [[ "${1:-}" == "--full" ]] || [[ "${1:-}" == "--agent-os" ]]; then
    TOTAL_STEPS=$((TOTAL_STEPS + 1))
    if run_step "Agent OS Setup" "$PROJECT_ROOT/bin/setup-agent-os.sh" "Setting up full agent operating system"; then
        SUCCESSFUL_STEPS=$((SUCCESSFUL_STEPS + 1))
    else
        FAILED_STEPS=$((FAILED_STEPS + 1))
    fi
fi

# Step 5: Claude MCP Setup (if requested)
if [[ "${1:-}" == "--full" ]] || [[ "${1:-}" == "--claude" ]]; then
    TOTAL_STEPS=$((TOTAL_STEPS + 1))
    if run_step "Claude MCP" "$PROJECT_ROOT/bin/setup-claude-mcp.sh" "Setting up Claude MCP integration"; then
        SUCCESSFUL_STEPS=$((SUCCESSFUL_STEPS + 1))
    else
        FAILED_STEPS=$((FAILED_STEPS + 1))
    fi
fi

# Summary
echo -e "${CYAN}📊 Development Environment Setup Summary${NC}"
echo -e "${CYAN}=======================================${NC}"
echo -e "Total steps: $TOTAL_STEPS"
echo -e "${GREEN}✅ Successful: $SUCCESSFUL_STEPS${NC}"

if [[ $FAILED_STEPS -gt 0 ]]; then
    echo -e "${RED}❌ Failed: $FAILED_STEPS${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Some setup steps failed. Your environment may not be fully configured.${NC}"
    echo -e "   Review the errors above and run individual setup scripts as needed."
    exit 1
else
    echo -e "${GREEN}🎉 All setup steps completed successfully!${NC}"
    echo ""
    echo -e "${GREEN}Your development environment is fully configured and ready.${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  • Run ${CYAN}/validate${NC} to verify everything is working"
    echo -e "  • Use ${CYAN}/start-coding${NC} to begin development"
    echo -e "  • Try ${CYAN}/complete-workflow${NC} for systematic project development"
fi

echo ""
echo -e "${CYAN}🔧 Available options:${NC}"
echo -e "  $0                # Basic setup (python + security + git)"
echo -e "  $0 --full         # Full setup including Agent OS and Claude MCP"
echo -e "  $0 --agent-os     # Include Agent OS setup"
echo -e "  $0 --claude       # Include Claude MCP setup"