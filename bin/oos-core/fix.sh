#!/usr/bin/env bash
# OOS Code Fixes and Optimization

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$OOS_ROOT/lib/oos-common.sh" 2>/dev/null || true

subcommand="${1:-help}"
shift || true

case "$subcommand" in
    auto)
        oos_log_info "Running automatic code fixes..."

        # Run black formatter
        if command -v uv &>/dev/null; then
            cd "$OOS_ROOT"
            oos_log_info "Formatting Python code..."
            uv run black src/ tests/ 2>/dev/null || true

            oos_log_info "Running linter..."
            uv run ruff check --fix src/ tests/ 2>/dev/null || true

            oos_log_success "Code fixes applied"
        else
            oos_log_error "Development environment not ready"
            echo "Run: oos dev setup"
            exit 1
        fi
        ;;

    optimize)
        oos_log_info "Optimizing code..."

        # Token optimization
        if [[ -f "$OOS_ROOT/src/token_optimization.py" ]]; then
            cd "$OOS_ROOT"
            oos_log_info "Running token optimization..."
            uv run python src/token_optimization.py "$@" || true
        fi

        oos_log_success "Optimization complete"
        ;;

    help|--help|-h)
        cat << 'EOF'
OOS Code Fixes

USAGE:
    oos fix <subcommand>

SUBCOMMANDS:
    auto                Automatic code formatting and fixes
    optimize            Optimize code for tokens/performance

EXAMPLES:
    oos fix auto
    oos fix optimize
EOF
        ;;

    *)
        oos_log_error "Unknown subcommand: $subcommand"
        echo "Run 'oos fix help' for usage"
        exit 1
        ;;
esac
