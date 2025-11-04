#!/usr/bin/env bash
# OOS Archon Integration (Advanced Tier)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$OOS_ROOT/lib/oos-common.sh" 2>/dev/null || true

subcommand="${1:-help}"
shift || true

case "$subcommand" in
    research)
        query="$*"
        if [[ -z "$query" ]]; then
            oos_log_error "Usage: oos archon research <query>"
            exit 1
        fi

        oos_log_info "Searching Archon knowledge base..."

        if [[ -f "$OOS_ROOT/bin/claude-archon.sh" ]]; then
            exec "$OOS_ROOT/bin/claude-archon.sh" research "$query"
        else
            oos_log_error "Archon integration not found"
            exit 1
        fi
        ;;

    status)
        oos_log_info "Checking Archon connection..."

        # Load .env
        if [[ -f "$OOS_ROOT/.env" ]]; then
            source "$OOS_ROOT/.env"
        fi

        if [[ -n "${ARCHON_URL:-}" ]]; then
            if curl -sf "${ARCHON_URL}/api/health" &>/dev/null; then
                oos_log_success "Archon connected: $ARCHON_URL"
            else
                oos_log_warning "Archon URL configured but not reachable"
            fi
        else
            oos_log_info "Archon not configured"
            echo "Run: oos help archon"
        fi
        ;;

    help|--help|-h)
        cat << 'EOF'
OOS Archon Integration (Advanced Tier)

USAGE:
    oos archon <subcommand>

SUBCOMMANDS:
    research <query>    Search knowledge base
    status              Check Archon connection

REQUIREMENTS:
    - Archon server running
    - ARCHON_URL in .env
    - Run: oos help archon

EXAMPLES:
    oos archon research "database patterns"
    oos archon status
EOF
        ;;

    *)
        oos_log_error "Unknown subcommand: $subcommand"
        echo "Run 'oos archon help' for usage"
        exit 1
        ;;
esac
