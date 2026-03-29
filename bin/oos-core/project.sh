#!/usr/bin/env bash
# OOS Project Management

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$OOS_ROOT/lib/oos-common.sh" 2>/dev/null || true

subcommand="${1:-help}"
shift || true

case "$subcommand" in
    create)
        project_name="${1:-}"
        if [[ -z "$project_name" ]]; then
            oos_log_error "Usage: oos project create <project-name>"
            exit 1
        fi

        oos_log_info "Creating project: $project_name"

        # Create project directory
        mkdir -p "$project_name"
        cd "$project_name"

        # Install OOS into project
        if [[ -f "$OOS_ROOT/install.sh" ]]; then
            bash "$OOS_ROOT/install.sh" "$(pwd)"
        else
            oos_log_error "OOS installer not found"
            exit 1
        fi

        oos_log_success "Project created: $project_name"
        echo ""
        echo "Next steps:"
        echo "  cd $project_name"
        echo "  oos dev setup"
        ;;

    update)
        oos_log_info "Updating OOS from GitHub..."

        if [[ -f "$OOS_ROOT/bin/oos-update-from-github.sh" ]]; then
            exec "$OOS_ROOT/bin/oos-update-from-github.sh"
        else
            oos_log_error "Update script not found"
            exit 1
        fi
        ;;

    help|--help|-h)
        cat << 'EOF'
OOS Project Management

USAGE:
    oos project <subcommand>

SUBCOMMANDS:
    create <name>       Create new project with OOS
    update              Update OOS from GitHub

EXAMPLES:
    oos project create my-new-project
    cd my-new-project
    oos dev setup
EOF
        ;;

    *)
        oos_log_error "Unknown subcommand: $subcommand"
        echo "Run 'oos project help' for usage"
        exit 1
        ;;
esac
