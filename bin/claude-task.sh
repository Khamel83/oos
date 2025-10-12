#!/bin/bash
# OOS Task Management with Archon Integration
# Consolidates: archon-task-start, archon-complete

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

show_help() {
    cat << EOF
📋 Task Management and Execution

USAGE:
    /task <subcommand> [arguments]

SUBCOMMANDS:
    start [task-id]     Start working on a task
    complete [task-id]  Mark task as complete
    list [filter]       List tasks
    update <task-id>    Update task status
    help                Show this help

EXAMPLES:
    /task start
    /task complete "8614f52c"
    /task list todo
    /task update "task-123" doing

ARCHON MCP INTEGRATION:
    Uses: manage_task, find_tasks

CONSOLIDATES:
    /archon-task-start → /task start
    /archon-complete → /task complete

EOF
}

task_start() {
    local task_id="$1"

    echo -e "${CYAN}🚀 Starting task work...${NC}"

    if [ -n "$task_id" ]; then
        echo "Task ID: $task_id"
        echo -e "${GREEN}✅ Task marked as 'doing'${NC}"
        echo
        echo -e "${BLUE}💡 This will integrate with:${NC}"
        echo "  • mcp__archon__manage_task (update status to 'doing')"
        echo "  • mcp__archon__find_tasks (get task details)"
    else
        echo -e "${YELLOW}📋 Available tasks:${NC}"
        echo "  • Create unified command implementation scripts"
        echo "  • Test consolidated commands"
        echo "  • Create migration strategy"
        echo
        echo "Use: /task start <task-id>"
    fi

    echo
    echo -e "${YELLOW}⚠️  MCP integration pending - use original /archon-task-start for now${NC}"
}

task_complete() {
    local task_id="$1"

    echo -e "${CYAN}✅ Completing task...${NC}"

    if [ -n "$task_id" ]; then
        echo "Task ID: $task_id"
        echo -e "${GREEN}🎉 Task marked as 'done'${NC}"
        echo
        echo -e "${BLUE}💡 This will integrate with:${NC}"
        echo "  • mcp__archon__manage_task (update status to 'done')"
    else
        echo -e "${RED}❌ Please provide a task ID${NC}"
        echo "Use: /task complete <task-id>"
        return 1
    fi

    echo
    echo -e "${YELLOW}⚠️  MCP integration pending - use original /archon-complete for now${NC}"
}

task_list() {
    local filter="${1:-all}"

    echo -e "${CYAN}📋 Task List (filter: $filter)${NC}"
    echo "================================"
    echo

    echo -e "${BLUE}🎯 OOS Slash Command Consolidation:${NC}"
    echo "  📝 Create unified command implementation scripts (doing)"
    echo "  🧪 Test consolidated commands (todo)"
    echo "  🔄 Create migration strategy (todo)"
    echo "  🔗 Validate Archon MCP integration (todo)"

    echo
    echo -e "${BLUE}💡 This will integrate with:${NC}"
    echo "  • mcp__archon__find_tasks (with filter: $filter)"

    echo
    echo -e "${YELLOW}⚠️  MCP integration pending${NC}"
}

task_update() {
    local task_id="$1"
    local status="$2"

    if [ -z "$task_id" ] || [ -z "$status" ]; then
        echo -e "${RED}❌ Please provide task ID and status${NC}"
        echo "Usage: /task update <task-id> <status>"
        echo "Status options: todo, doing, review, done"
        return 1
    fi

    echo -e "${CYAN}🔄 Updating task...${NC}"
    echo "Task ID: $task_id"
    echo "New status: $status"

    echo
    echo -e "${BLUE}💡 This will integrate with:${NC}"
    echo "  • mcp__archon__manage_task (update status)"

    echo
    echo -e "${YELLOW}⚠️  MCP integration pending${NC}"
}

main() {
    local subcommand="${1:-help}"
    shift || true

    case "$subcommand" in
        start)
            task_start "${1:-}"
            ;;
        complete)
            task_complete "${1:-}"
            ;;
        list)
            task_list "${1:-}"
            ;;
        update)
            task_update "${1:-}" "${2:-}"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown subcommand: $subcommand${NC}"
            echo
            show_help
            exit 1
            ;;
    esac
}

main "$@"