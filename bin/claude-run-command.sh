#!/usr/bin/env bash
set -euo pipefail

# Claude Code Command Runner
# Allows one slash command to execute another slash command

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

COMMAND_NAME="$1"
shift || true

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to find and execute a command
run_command() {
    local cmd_name="$1"
    shift || true

    # Check if we have the slash commands file
    local commands_file="$PROJECT_ROOT/.claude/slash_commands.json"
    if [[ ! -f "$commands_file" ]]; then
        echo -e "${RED}❌ No slash commands file found${NC}"
        return 1
    fi

    # Look up the script for this command
    local script_path=$(python3 -c "
import json
import sys
try:
    with open('$commands_file', 'r') as f:
        data = json.load(f)
    for cmd in data.get('commands', []):
        if cmd.get('name') == '$cmd_name':
            print(cmd.get('script', ''))
            sys.exit(0)
    print('')
except:
    print('')
" 2>/dev/null)

    if [[ -z "$script_path" ]]; then
        echo -e "${RED}❌ Command /$cmd_name not found${NC}"
        return 1
    fi

    local full_script_path="$PROJECT_ROOT/$script_path"
    if [[ ! -f "$full_script_path" ]]; then
        echo -e "${RED}❌ Script not found: $script_path${NC}"
        return 1
    fi

    echo -e "${BLUE}🔄 Running /$cmd_name...${NC}"
    bash "$full_script_path" "$@"
}

# Run the command
run_command "$COMMAND_NAME" "$@"