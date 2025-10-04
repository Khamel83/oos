#!/usr/bin/env bash
# OOS Bootstrap - One-command OOS installation
# This is the FIRST script someone runs to get OOS

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

OOS_REPO="https://github.com/Khamel83/oos.git"
INSTALL_DIR="$HOME/.oos"
PROJECT_DIR="${1:-$(pwd)}"

echo -e "${BOLD}${CYAN}🚀 OOS (Open Operating System) Bootstrap${NC}"
echo "========================================"
echo ""
echo -e "${BLUE}What is OOS?${NC}"
echo "OOS is a modular development system based on Unix Philosophy."
echo "It provides instant development workflows, security scanning,"
echo "testing automation, and AI-assisted coding - all through"
echo "simple slash commands in Claude Code."
echo ""

# Step 1: Check if OOS already exists
if [[ -d "$INSTALL_DIR" ]]; then
    echo -e "${YELLOW}⚠️  OOS already installed at $INSTALL_DIR${NC}"
    echo "Updating from GitHub..."
    cd "$INSTALL_DIR"
    git pull origin master >/dev/null 2>&1 || {
        echo -e "${RED}❌ Failed to update OOS${NC}"
        echo "You may need to reinstall. Delete $INSTALL_DIR and try again."
        exit 1
    }
    echo -e "${GREEN}✅ OOS updated${NC}"
else
    # Step 2: Install OOS
    echo -e "${BLUE}📦 Installing OOS...${NC}"
    git clone "$OOS_REPO" "$INSTALL_DIR" >/dev/null 2>&1 || {
        echo -e "${RED}❌ Failed to clone OOS repository${NC}"
        echo "Please check your internet connection and try again."
        exit 1
    }
    echo -e "${GREEN}✅ OOS installed to $INSTALL_DIR${NC}"
fi

# Step 3: Install into current project
echo -e "\n${BLUE}🏗️ Installing OOS into current project...${NC}"
cd "$PROJECT_DIR"

if "$INSTALL_DIR/bin/oos-install-into-project.sh" "$PROJECT_DIR"; then
    echo -e "${GREEN}✅ OOS installed into project${NC}"
else
    echo -e "${RED}❌ Failed to install OOS into project${NC}"
    exit 1
fi

# Step 4: Quick start guide
echo -e "\n${PURPLE}🎯 Quick Start Guide${NC}"
echo "=================="
echo ""
echo -e "${BOLD}1. Restart Claude Code${NC}"
echo "   Close and reopen Claude Code to load new slash commands"
echo ""
echo -e "${BOLD}2. Try these commands:${NC}"
echo "   /dev-setup      - Validate your development environment"
echo "   /modules list   - See all available modules"
echo "   /pre-commit     - Run before committing code"
echo ""
echo -e "${BOLD}3. Create a new project:${NC}"
echo "   /create-project python-project my-app"
echo ""
echo -e "${BOLD}4. Learn more:${NC}"
echo "   Check the docs/ directory for complete documentation"

# Step 5: Show what was installed
echo -e "\n${BLUE}📋 What was installed:${NC}"
echo "• Slash commands (.claude/slash_commands.json)"
echo "• Module system (modules/)"
echo "• Workflow compositions (compositions/)"
echo "• OOS tools (bin/oos-*.sh)"
echo "• Project marker (.oos-project)"

echo -e "\n${BOLD}${GREEN}🎉 OOS Bootstrap Complete!${NC}"
echo ""
echo -e "${YELLOW}Next: Restart Claude Code and run /dev-setup${NC}"

exit 0