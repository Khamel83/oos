#!/usr/bin/env bash
# OOS AI-Powered Features (Enhanced Tier)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$OOS_ROOT/lib/oos-common.sh" 2>/dev/null || true

subcommand="${1:-help}"
shift || true

case "$subcommand" in
    analyze)
        query="$*"
        if [[ -z "$query" ]]; then
            oos_log_error "Usage: oos ai analyze <question>"
            exit 1
        fi

        oos_log_info "Analyzing with AI..."

        if [[ -f "$OOS_ROOT/bin/oos-full-stack" ]]; then
            exec "$OOS_ROOT/bin/oos-full-stack" "$query"
        elif [[ -f "$OOS_ROOT/src/ai_provider.py" ]]; then
            cd "$OOS_ROOT"
            uv run python src/ai_provider.py "$query"
        else
            oos_log_error "AI system not configured"
            exit 1
        fi
        ;;

    test)
        oos_log_info "Testing AI connection..."

        if [[ -f "$OOS_ROOT/src/ai_provider.py" ]]; then
            cd "$OOS_ROOT"
            uv run python -c "from src.ai_provider import AIProvider; print('AI connection OK')"
            oos_log_success "AI features are working"
        else
            oos_log_error "AI provider not found"
            exit 1
        fi
        ;;

    help|--help|-h)
        cat << 'EOF'
OOS AI Features (Enhanced Tier)

USAGE:
    oos ai <subcommand>

SUBCOMMANDS:
    analyze <query>     Analyze with AI
    test                Test AI connection

REQUIREMENTS:
    - API key in .env (OPENROUTER_API_KEY or OPENAI_API_KEY)
    - Run: oos help setup

EXAMPLES:
    oos ai analyze "How can I optimize my code?"
    oos ai test
EOF
        ;;

    *)
        oos_log_error "Unknown subcommand: $subcommand"
        echo "Run 'oos ai help' for usage"
        exit 1
        ;;
esac
