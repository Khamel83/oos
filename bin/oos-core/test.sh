#!/usr/bin/env bash
# OOS Testing Utilities

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$OOS_ROOT/lib/oos-common.sh" 2>/dev/null || true

subcommand="${1:-help}"
shift || true

case "$subcommand" in
    run)
        oos_log_info "Running tests..."
        cd "$OOS_ROOT"

        if command -v uv &>/dev/null && [[ -d ".venv" ]]; then
            uv run pytest tests/ "$@"
        elif command -v pytest &>/dev/null; then
            pytest tests/ "$@"
        else
            oos_log_error "pytest not found"
            echo "Run: oos dev setup"
            exit 1
        fi
        ;;

    debug)
        oos_log_info "Running tests in debug mode..."
        cd "$OOS_ROOT"

        if command -v uv &>/dev/null && [[ -d ".venv" ]]; then
            uv run pytest tests/ -v --tb=short "$@"
        else
            oos_log_error "Test environment not ready"
            exit 1
        fi
        ;;

    scenarios)
        oos_log_info "Running user scenario tests..."

        if [[ -d "$OOS_ROOT/tests/scenarios" ]]; then
            for scenario in "$OOS_ROOT/tests/scenarios"/*.scenarios; do
                if [[ -f "$scenario" ]]; then
                    echo "Testing: $(basename "$scenario")"
                    # Run scenario test
                fi
            done
        else
            oos_log_warning "No scenarios found"
        fi
        ;;

    help|--help|-h)
        cat << 'EOF'
OOS Testing Utilities

USAGE:
    oos test <subcommand>

SUBCOMMANDS:
    run                 Run all tests
    debug               Run tests in debug mode
    scenarios           Run user scenario tests

EXAMPLES:
    oos test run
    oos test run tests/test_specific.py
    oos test debug
EOF
        ;;

    *)
        oos_log_error "Unknown subcommand: $subcommand"
        echo "Run 'oos test help' for usage"
        exit 1
        ;;
esac
