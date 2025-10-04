#!/usr/bin/env bash
# OOS Project Integration - Install OOS into any project
# This is the KEY UX script that makes OOS actually usable

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="${1:-$(pwd)}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}🚀 Installing OOS into Project${NC}"
echo "==============================="
echo "Project: $PROJECT_DIR"
echo "OOS Source: $OOS_ROOT"

cd "$PROJECT_DIR"

# Step 1: Create .claude directory
echo -e "\n${BLUE}📁 Setting up Claude Code integration...${NC}"
mkdir -p .claude

# Step 2: Copy working slash commands (the key UX element!)
echo -e "${BLUE}📋 Installing slash commands...${NC}"
if [[ -f "$OOS_ROOT/.claude/project_commands.json" ]]; then
    cp "$OOS_ROOT/.claude/project_commands.json" .claude/slash_commands.json
    echo -e "${GREEN}✅ Slash commands installed${NC}"
else
    echo -e "${RED}❌ No working slash commands found in OOS${NC}"
    exit 1
fi

# Step 3: Copy essential OOS scripts to project
echo -e "\n${BLUE}🔧 Installing OOS tools...${NC}"
mkdir -p bin

# Core OOS scripts that projects need
essential_scripts=(
    "oos-module-runner.sh"
    "oos-template-manager.sh"
    "oos-update-from-github.sh"
    "dev-gate.sh"
    "claude-dev-gate.sh"
    "claude-start-coding.sh"
)

for script in "${essential_scripts[@]}"; do
    if [[ -f "$OOS_ROOT/bin/$script" ]]; then
        cp "$OOS_ROOT/bin/$script" bin/
        chmod +x "bin/$script"
        echo "  ✅ $script"
    else
        echo -e "  ${YELLOW}⚠️  $script not found${NC}"
    fi
done

# Step 4: Copy module system
echo -e "\n${BLUE}🧩 Installing module system...${NC}"
if [[ -d "$OOS_ROOT/modules" ]]; then
    cp -r "$OOS_ROOT/modules" .
    echo -e "${GREEN}✅ Module system installed${NC}"
else
    echo -e "${YELLOW}⚠️  Module system not found${NC}"
fi

# Step 5: Copy compositions
echo -e "\n${BLUE}🏗️ Installing compositions...${NC}"
if [[ -d "$OOS_ROOT/compositions" ]]; then
    cp -r "$OOS_ROOT/compositions" .
    echo -e "${GREEN}✅ Compositions installed${NC}"
else
    echo -e "${YELLOW}⚠️  Compositions not found${NC}"
fi

# Step 6: Create .gitignore entries (don't commit OOS internals)
echo -e "\n${BLUE}📝 Updating .gitignore...${NC}"
if [[ ! -f .gitignore ]]; then
    touch .gitignore
fi

# Add OOS entries to .gitignore if not already present
gitignore_entries=(
    "# OOS (Open Operating System) - these are copied from OOS repo"
    "# Remove these lines if you want to version control OOS in this project"
    "modules/"
    "compositions/"
    "bin/oos-*.sh"
    "bin/dev-gate.sh"
    "bin/claude-*.sh"
)

for entry in "${gitignore_entries[@]}"; do
    if ! grep -q "$entry" .gitignore 2>/dev/null; then
        echo "$entry" >> .gitignore
    fi
done

echo -e "${GREEN}✅ .gitignore updated${NC}"

# Step 7: Create OOS marker file
echo -e "\n${BLUE}🏷️ Creating OOS marker...${NC}"
cat > .oos-project << EOF
# OOS Project Marker
# This file indicates that this project uses OOS (Open Operating System)
# Generated: $(date)
# OOS Source: $OOS_ROOT

To update OOS in this project:
  /update-oos (in Claude Code)
  or: ./bin/oos-update-from-github.sh

Available OOS commands:
  /dev-setup     - Complete development environment validation
  /pre-commit    - Security + lint + test + AI commit message
  /modules       - Run/compose individual modules
  /create-project - Create new projects from templates
EOF

echo -e "${GREEN}✅ OOS marker created${NC}"

# Summary
echo -e "\n${PURPLE}🎉 OOS Installation Complete!${NC}"
echo "=========================="
echo -e "${GREEN}✅ Slash commands installed in .claude/${NC}"
echo -e "${GREEN}✅ Module system available${NC}"
echo -e "${GREEN}✅ Compositions ready${NC}"
echo -e "${GREEN}✅ Essential scripts in bin/${NC}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Restart Claude Code to load new slash commands"
echo "2. Run: /dev-setup (to validate your environment)"
echo "3. Run: /modules list (to see available modules)"
echo "4. Start using OOS workflows!"

echo -e "\n${BLUE}Available OOS Commands:${NC}"
echo "• /dev-setup     - Complete environment validation"
echo "• /pre-commit    - Pre-commit workflow"
echo "• /modules       - Module management"
echo "• /update-oos    - Update OOS from GitHub"

exit 0