#!/usr/bin/env bash
set -euo pipefail

# Integrate OOS Development Gate with User Shell
# Automatically adds gate enforcement to shell startup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Shell configuration files to check
SHELL_CONFIGS=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile")

# Integration marker
INTEGRATION_MARKER="# OOS Development Gate Integration"
INTEGRATION_BLOCK="
$INTEGRATION_MARKER
if [[ -f \"$PROJECT_ROOT/bin/setup-shell-environment.sh\" ]]; then
    source \"$PROJECT_ROOT/bin/setup-shell-environment.sh\"
fi
"

echo -e "${BLUE}Integrating OOS Development Gate with shell...${NC}"

# Find which shell config file to use
for config in "${SHELL_CONFIGS[@]}"; do
    if [[ -f "$config" ]]; then
        # Check if already integrated
        if grep -q "$INTEGRATION_MARKER" "$config"; then
            echo -e "${YELLOW}Already integrated with $config${NC}"
            continue
        fi

        echo -e "${BLUE}Adding integration to $config${NC}"
        echo "$INTEGRATION_BLOCK" >> "$config"
        echo -e "${GREEN}✅ Integrated with $config${NC}"

        echo
        echo -e "${YELLOW}To activate in current session:${NC}"
        echo "source $config"
        break
    fi
done

echo
echo -e "${GREEN}Shell integration complete!${NC}"
echo "New shell sessions will have development gate enforcement."
