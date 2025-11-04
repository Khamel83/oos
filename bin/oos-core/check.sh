#!/usr/bin/env bash
# OOS Validation and Security Checks

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$OOS_ROOT/lib/oos-common.sh" 2>/dev/null || true

subcommand="${1:-help}"
shift || true

case "$subcommand" in
    security)
        oos_log_header "Security Check"

        # Check for secrets in git
        if [[ -f "$OOS_ROOT/bin/validate-no-secrets.sh" ]]; then
            "$OOS_ROOT/bin/validate-no-secrets.sh"
        fi

        # Check file permissions
        if [[ -d "$OOS_ROOT/modules/security" ]]; then
            for script in "$OOS_ROOT/modules/security"/*.sh; do
                [[ -f "$script" ]] && bash "$script"
            done
        fi

        oos_log_success "Security check complete"
        ;;

    all)
        oos_log_header "Running All Checks"

        # Development environment
        "$SCRIPT_DIR/dev.sh" check

        echo ""

        # Security
        oos check security

        echo ""
        oos_log_success "All checks complete"
        ;;

    help|--help|-h)
        cat << 'EOF'
OOS Validation and Checks

USAGE:
    oos check <subcommand>

SUBCOMMANDS:
    security            Run security checks
    all                 Run all validation checks

EXAMPLES:
    oos check security
    oos check all
EOF
        ;;

    *)
        oos_log_error "Unknown subcommand: $subcommand"
        echo "Run 'oos check help' for usage"
        exit 1
        ;;
esac
