#!/bin/bash
# OOS Command Migration Helper
# Helps users transition from old commands to new consolidated ones

set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔄 OOS Command Migration Guide${NC}"
echo "============================="
echo

# Detailed migration mapping with specific subcommands
declare -A migration_map=(
    ["dev-setup"]="/dev setup"
    ["startup-check"]="/dev check"
    ["modules"]="/dev modules"
    ["reload-commands"]="/dev refresh"
    ["test-debug"]="/test debug"
    ["test-connection"]="/test connection"
    ["test-user-scenarios"]="/test scenarios"
    ["auto-fix"]="/fix auto"
    ["optimize"]="/fix optimize"
    ["doc-check"]="/fix docs"
    ["brain-dump"]="/think dump"
    ["clarify"]="/think clarify"
    ["solve"]="/think solve"
    ["meta-ai"]="/think meta"
    ["agentic-workflow"]="/workflow agentic"
    ["complete-workflow"]="/workflow complete"
    ["idea-to-done"]="/workflow idea"
    ["create-project"]="/project create"
    ["provision"]="/project provision"
    ["update-oos"]="/project update"
    ["oos-refresh"]="/project refresh"
    ["op-signin"]="/op signin"
    ["op-status"]="/op status"
    ["op-setup"]="/op setup"
    ["op-get"]="/op get"
    ["op-secret"]="/op secret"
    ["op-session"]="/op session"
    ["op-session-automated"]="/op session automated"
    ["archon-research"]="/archon research"
    ["archon-status"]="/archon status"
    ["archon-task-start"]="/task start"
    ["archon-complete"]="/task complete"
    ["security-review"]="/check security"
    ["context-stats"]="/check context"
)

echo -e "${BLUE}📋 Command Migration Map (45 → 10 commands):${NC}"
echo

# Show migration suggestions grouped by new command
declare -A grouped_commands
for old_cmd in "${!migration_map[@]}"; do
    new_cmd="${migration_map[$old_cmd]}"
    base_cmd=$(echo "$new_cmd" | cut -d' ' -f1)

    if [[ -z "${grouped_commands[$base_cmd]:-}" ]]; then
        grouped_commands[$base_cmd]="$old_cmd"
    else
        grouped_commands[$base_cmd]+=" $old_cmd"
    fi
done

for base_cmd in $(printf '%s\n' "${!grouped_commands[@]}" | sort); do
    echo -e "${GREEN}${base_cmd}${NC} consolidates:"
    for old_cmd in ${grouped_commands[$base_cmd]}; do
        echo -e "  ❌ /${old_cmd} → ✅ ${migration_map[$old_cmd]}"
    done
    echo
done

echo -e "${YELLOW}💡 Migration Benefits:${NC}"
echo "  • 78% reduction in commands to remember (45 → 10)"
echo "  • Logical grouping by function area"
echo "  • Consistent subcommand interface"
echo "  • Enhanced discoverability with help systems"
echo "  • Future-proof architecture"
echo

echo -e "${CYAN}🚀 Quick Migration Examples:${NC}"
echo "  Old: /dev-setup && /startup-check"
echo "  New: /dev setup && /dev check"
echo
echo "  Old: /auto-fix && /optimize && /doc-check"
echo "  New: /fix auto && /fix optimize && /fix docs"
echo
echo "  Old: /archon-research \"patterns\" && /archon-task-start"
echo "  New: /archon research \"patterns\" && /task start"
echo

echo -e "${BLUE}📚 Documentation:${NC}"
echo "  • Each command has comprehensive help: /command help"
echo "  • All original functionality preserved"
echo "  • Enhanced with better error handling and UX"
echo

echo -e "${GREEN}✅ Ready for immediate use!${NC}"
