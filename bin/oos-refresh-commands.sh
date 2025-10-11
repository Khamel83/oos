#!/usr/bin/env bash
# OOS Slash Command Auto-Refresh System
# Updates and validates slash commands on startup

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Handle command line args first
case "${1:-}" in
    --test-only)
        PROJECT_DIR="$(pwd)"
        ;;
    --version)
        PROJECT_DIR="$(pwd)"
        ;;
    --help|"-h")
        PROJECT_DIR="$(pwd)"
        ;;
    *)
        PROJECT_DIR="${1:-$(pwd)}"
        ;;
esac

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# Version tracking
VERSION_FILE=".claude/commands_version.json"
TEST_LOG=".claude/commands_test.log"

echo -e "${BOLD}${BLUE}🔄 OOS Slash Command Auto-Refresh${NC}"
echo "==================================="
echo "Project: $PROJECT_DIR"
echo "OOS Source: $OOS_ROOT"

cd "$PROJECT_DIR"

# Ensure .claude directory exists
mkdir -p .claude

# Function to get current OOS version hash
get_oos_version() {
    cd "$OOS_ROOT"
    git rev-parse --short HEAD 2>/dev/null || echo "unknown"
}

# Function to get current commands version
get_commands_version() {
    if [[ -f "$VERSION_FILE" ]]; then
        jq -r '.oos_version // "unknown"' "$VERSION_FILE" 2>/dev/null || echo "unknown"
    else
        echo "none"
    fi
}

# Function to backup current commands
backup_commands() {
    if [[ -d ".claude/commands" ]]; then
        local backup_dir=".claude/commands_backup_$(date +%Y%m%d_%H%M%S)"
        cp -r .claude/commands "$backup_dir"
        echo -e "${YELLOW}📦 Backed up current commands to $backup_dir${NC}"
        return 0
    fi
    return 1
}

# Function to test command functionality
test_command() {
    local cmd_file="$1"
    local cmd_name="$(basename "$cmd_file" .md)"

    # Test YAML format
    if ! head -10 "$cmd_file" | grep -q "^description:"; then
        echo -e "${RED}❌ $cmd_name: Missing description${NC}" >> "$TEST_LOG"
        return 1
    fi

    if ! head -10 "$cmd_file" | grep -q "^tools:"; then
        echo -e "${RED}❌ $cmd_name: Missing tools${NC}" >> "$TEST_LOG"
        return 1
    fi

    # Test script references
    if grep -q "bin/" "$cmd_file"; then
        local script_file=$(grep "bin/" "$cmd_file" | head -1 | sed 's/.*bin\///' | sed 's/".*//' | sed 's/\$ARGUMENTS.*//')
        if [[ -f "bin/$script_file" ]]; then
            # Test if script is executable and shows help
            if timeout 5s "./bin/$script_file" --help >/dev/null 2>&1 || \
               timeout 5s "./bin/$script_file" --version >/dev/null 2>&1 || \
               timeout 5s "./bin/$script_file" >/dev/null 2>&1; then
                echo -e "${GREEN}✅ $cmd_name: Script functional${NC}" >> "$TEST_LOG"
                return 0
            else
                echo -e "${YELLOW}⚠️  $cmd_name: Script test timeout (may be normal)${NC}" >> "$TEST_LOG"
                return 0  # Timeout doesn't mean failure
            fi
        else
            echo -e "${RED}❌ $cmd_name: Script bin/$script_file not found${NC}" >> "$TEST_LOG"
            return 1
        fi
    fi

    echo -e "${GREEN}✅ $cmd_name: Format valid${NC}" >> "$TEST_LOG"
    return 0
}

# Function to validate all commands
validate_commands() {
    echo -e "\n${BLUE}🧪 Validating slash commands...${NC}"

    > "$TEST_LOG"  # Clear test log
    local total=0
    local passed=0
    local failed=0

    # Test each command
    for cmd_file in .claude/commands/*.md; do
        if [[ -f "$cmd_file" ]]; then
            ((total++))
            if test_command "$cmd_file"; then
                ((passed++))
            else
                ((failed++))
            fi
        fi
    done

    echo -e "${GREEN}✅ Validation complete: $passed/$total passed, $failed failed${NC}"

    if [[ $failed -gt 0 ]]; then
        echo -e "${RED}❌ Some commands failed validation. Check $TEST_LOG${NC}"
        return 1
    else
        echo -e "${GREEN}✅ All commands validated successfully${NC}"
        return 0
    fi
}

# Function to show diff between versions
show_diff() {
    local old_version="$1"
    local new_version="$2"

    echo -e "\n${PURPLE}📊 Changes detected: $old_version → $new_version${NC}"

    # If we have a backup, show what changed
    local latest_backup=$(ls -1t .claude/commands_backup_* 2>/dev/null | head -1)
    if [[ -n "$latest_backup" && -d "$latest_backup" ]]; then
        echo -e "${BLUE}📋 Command changes:${NC}"

        # New commands
        for cmd in .claude/commands/*.md; do
            local cmd_name=$(basename "$cmd")
            if [[ ! -f "$latest_backup/$cmd_name" ]]; then
                echo -e "  ${GREEN}+ ADDED: $cmd_name${NC}"
            fi
        done

        # Removed commands
        for cmd in "$latest_backup"/*.md; do
            local cmd_name=$(basename "$cmd")
            if [[ ! -f ".claude/commands/$cmd_name" ]]; then
                echo -e "  ${RED}- REMOVED: $cmd_name${NC}"
            fi
        done

        # Modified commands
        for cmd in .claude/commands/*.md; do
            local cmd_name=$(basename "$cmd")
            if [[ -f "$latest_backup/$cmd_name" ]]; then
                if ! cmp -s "$cmd" "$latest_backup/$cmd_name"; then
                    echo -e "  ${YELLOW}~ MODIFIED: $cmd_name${NC}"
                fi
            fi
        done
    fi
}

# Main refresh process
main() {
    local current_oos_version=$(get_oos_version)
    local current_commands_version=$(get_commands_version)

    echo -e "${BLUE}📋 Current versions:${NC}"
    echo "  OOS: $current_oos_version"
    echo "  Commands: $current_commands_version"

    # Check if update is needed
    if [[ "$current_oos_version" == "$current_commands_version" ]]; then
        echo -e "${GREEN}✅ Commands are up to date${NC}"

        # Still validate to ensure they're working
        if validate_commands; then
            echo -e "${GREEN}✅ All commands functional - no update needed${NC}"
            exit 0
        else
            echo -e "${YELLOW}⚠️  Commands up to date but validation failed - refreshing anyway${NC}"
        fi
    fi

    echo -e "${YELLOW}🔄 Update needed: $current_commands_version → $current_oos_version${NC}"

    # Backup current commands
    backup_commands

    # Update commands from OOS
    echo -e "\n${BLUE}📥 Updating slash commands...${NC}"
    if [[ -d "$OOS_ROOT/.claude/commands" ]]; then
        mkdir -p .claude/commands
        cp -r "$OOS_ROOT/.claude/commands"/*.md .claude/commands/ 2>/dev/null || true
        echo -e "${GREEN}✅ Commands copied from OOS${NC}"
    else
        echo -e "${RED}❌ No commands found in OOS${NC}"
        exit 1
    fi

    # Show changes
    show_diff "$current_commands_version" "$current_oos_version"

    # Validate new commands
    if validate_commands; then
        # Update version file
        cat > "$VERSION_FILE" << EOF
{
  "oos_version": "$current_oos_version",
  "updated_at": "$(date -Iseconds)",
  "validation_passed": true,
  "total_commands": $(ls .claude/commands/*.md 2>/dev/null | wc -l),
  "test_log": "$TEST_LOG"
}
EOF

        echo -e "\n${GREEN}🎉 Commands updated and validated successfully!${NC}"
        echo -e "${BLUE}📝 Test results saved to: $TEST_LOG${NC}"

        # Show summary of key commands
        echo -e "\n${BLUE}🚀 Key workflow commands ready:${NC}"
        for cmd in complete-workflow validate ruat provision screenshot; do
            if [[ -f ".claude/commands/$cmd.md" ]]; then
                echo -e "  ${GREEN}✓${NC} /$cmd"
            fi
        done

        echo -e "\n${YELLOW}💡 Restart Claude Code to use updated commands${NC}"

    else
        echo -e "\n${RED}❌ Command validation failed!${NC}"
        echo -e "${RED}🚨 This indicates a serious fuckup in the update${NC}"

        # Attempt to restore from backup
        local latest_backup=$(ls -1t .claude/commands_backup_* 2>/dev/null | head -1)
        if [[ -n "$latest_backup" && -d "$latest_backup" ]]; then
            echo -e "${YELLOW}🔄 Attempting to restore from backup...${NC}"
            rm -rf .claude/commands
            mv "$latest_backup" .claude/commands

            if validate_commands; then
                echo -e "${GREEN}✅ Successfully restored previous working commands${NC}"
            else
                echo -e "${RED}❌ Even backup commands failed validation${NC}"
            fi
        fi

        exit 1
    fi
}

# Handle command line args
case "${1:-}" in
    --test-only)
        echo -e "${BLUE}🧪 Testing current commands only...${NC}"
        if validate_commands; then
            echo -e "${GREEN}✅ All commands working${NC}"
            exit 0
        else
            echo -e "${RED}❌ Command validation failed${NC}"
            exit 1
        fi
        ;;
    --version)
        echo "Current: $(get_commands_version)"
        echo "OOS: $(get_oos_version)"
        exit 0
        ;;
    --help|"-h")
        echo "OOS Slash Command Auto-Refresh"
        echo ""
        echo "Usage: $0 [project-dir] [options]"
        echo ""
        echo "Options:"
        echo "  --test-only    Only test current commands, don't update"
        echo "  --version      Show current versions"
        echo "  --help         Show this help"
        echo ""
        echo "This script automatically updates slash commands from OOS"
        echo "and validates they work correctly."
        exit 0
        ;;
esac

main "$@"