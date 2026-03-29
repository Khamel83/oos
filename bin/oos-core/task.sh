#!/usr/bin/env bash
# OOS Task Management
# Wraps the Python task system with clean interface

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$OOS_ROOT/lib/oos-common.sh" 2>/dev/null || true

# Ensure task database exists
mkdir -p "$OOS_ROOT/.oos/tasks"

# Run task CLI through uv
exec_task_cli() {
    cd "$OOS_ROOT"
    if command -v uv &>/dev/null; then
        uv run python -m src.oos_task_system.cli "$@" 2>&1 | grep -v "RuntimeWarning" || true
    else
        # Fallback to direct Python if uv not available
        python -m src.oos_task_system.cli "$@" 2>/dev/null || {
            oos_log_error "Task system requires Python dependencies"
            echo "Run: oos dev setup"
            exit 1
        }
    fi
}

# Parse command
subcommand="${1:-list}"
shift || true

case "$subcommand" in
    list|ls)
        exec_task_cli list "$@"
        ;;
    create|new)
        if [[ $# -eq 0 ]]; then
            oos_log_error "Usage: oos task create <title> [description]"
            exit 1
        fi
        title="$1"
        shift || true
        description="${*:-}"

        if [[ -n "$description" ]]; then
            exec_task_cli create --title "$title" --description "$description"
        else
            exec_task_cli create --title "$title"
        fi
        ;;
    start|begin)
        if [[ $# -eq 0 ]]; then
            oos_log_error "Usage: oos task start <task-id>"
            exit 1
        fi
        exec_task_cli start "$1"
        ;;
    done|complete|finish)
        if [[ $# -eq 0 ]]; then
            oos_log_error "Usage: oos task done <task-id>"
            exit 1
        fi
        exec_task_cli complete "$1"
        ;;
    show|details)
        if [[ $# -eq 0 ]]; then
            oos_log_error "Usage: oos task show <task-id>"
            exit 1
        fi
        exec_task_cli show "$1"
        ;;
    update|edit)
        if [[ $# -eq 0 ]]; then
            oos_log_error "Usage: oos task update <task-id> [options]"
            exit 1
        fi
        exec_task_cli update "$@"
        ;;
    help|--help|-h)
        cat << 'EOF'
OOS Task Management

USAGE:
    oos task <subcommand> [arguments]

SUBCOMMANDS:
    list, ls                    List all tasks
    create, new <title>         Create new task
    start, begin <id>           Start working on task
    done, complete <id>         Mark task complete
    show, details <id>          Show task details
    update, edit <id> [opts]    Update task

EXAMPLES:
    oos task create "Build authentication system"
    oos task list
    oos task start abc123
    oos task done abc123
EOF
        ;;
    *)
        oos_log_error "Unknown subcommand: $subcommand"
        echo "Run 'oos task help' for usage"
        exit 1
        ;;
esac
