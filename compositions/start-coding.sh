#!/usr/bin/env bash
# Composition: start-coding
# Purpose: Complete development environment setup using module composition
# Based on: Unix Philosophy + Modular Architecture

set -euo pipefail

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

echo -e "${BOLD}${CYAN}🚀 Start Coding - Module Composition${NC}"
echo "===================================="

# Step 1: System modules (core requirements)
echo -e "\n${BLUE}📦 System Validation${NC}"
"$PROJECT_ROOT/bin/oos-module-runner.sh" compose \
    python/check_uv \
    git/check_status \
    security/check_1password

# Step 2: Show available development modules
echo -e "\n${PURPLE}🧩 Available Development Modules:${NC}"
"$PROJECT_ROOT/bin/oos-module-runner.sh" list

# Step 3: Composition examples
echo -e "\n${YELLOW}🏗️  Example Compositions:${NC}"
echo "• Basic validation: oos-module-runner.sh compose python/check_uv git/check_status"
echo "• Security check: oos-module-runner.sh run security check_1password"
echo "• Custom workflow: Create your own composition script"

echo -e "\n${YELLOW}💡 Unix Philosophy in Action:${NC}"
echo "• Each module does ONE thing well"
echo "• Modules compose into workflows"
echo "• Add new modules without changing existing ones"
echo "• AI writes focused modules, humans compose products"

echo -e "\n${BOLD}${GREEN}🎉 Module system ready!${NC}"
echo "Next: Create your product by composing these modules"