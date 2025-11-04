#!/usr/bin/env bash
# OOS Development Environment Management

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$OOS_ROOT/lib/oos-common.sh" 2>/dev/null || true

subcommand="${1:-help}"
shift || true

case "$subcommand" in
    setup)
        oos_log_header "Development Environment Setup"

        # Check uv installation
        if ! command -v uv &>/dev/null; then
            oos_log_warning "uv not installed"
            echo "Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
            echo ""
        else
            oos_log_success "uv installed ($(uv --version))"
        fi

        # Sync Python dependencies if in OOS repo
        if [[ -f "$OOS_ROOT/pyproject.toml" ]] && grep -q "name = \"oos\"" "$OOS_ROOT/pyproject.toml" 2>/dev/null; then
            oos_log_info "Installing Python dependencies..."
            if uv sync; then
                oos_log_success "Python dependencies installed"
            else
                oos_log_error "Failed to install dependencies"
            fi
        fi

        # Create necessary directories
        mkdir -p "$OOS_ROOT/.oos/tasks"
        mkdir -p "$OOS_ROOT/.oos/logs"
        oos_log_success "OOS directories created"

        # Check for .env file
        if [[ ! -f "$OOS_ROOT/.env" ]]; then
            oos_log_info "Creating .env template..."
            cat > "$OOS_ROOT/.env" << 'ENVEOF'
# OOS Configuration

# Core (no configuration needed)

# Enhanced Tier - AI Features (optional)
# OPENROUTER_API_KEY=sk-your-key-here
# OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-your-key-here

# Advanced Tier - Archon Integration (optional)
# ARCHON_URL=https://your-archon-server
# ARCHON_API_KEY=your-api-key
ENVEOF
            oos_log_success ".env file created (add API keys to enable features)"
        fi

        echo ""
        oos_log_header "Setup Complete!"
        echo ""
        echo "Next steps:"
        echo "  oos status              # Check what features are available"
        echo "  oos task create \"Task\"  # Start tracking work"
        echo "  oos help setup          # Enable AI features (optional)"
        ;;

    check)
        oos_log_header "Development Environment Check"

        # Check uv
        if command -v uv &>/dev/null; then
            oos_log_success "uv: $(uv --version)"
        else
            oos_log_warning "uv: Not installed"
        fi

        # Check Python
        if command -v python3 &>/dev/null; then
            oos_log_success "Python: $(python3 --version)"
        else
            oos_log_warning "Python: Not found"
        fi

        # Check virtual environment
        if [[ -d "$OOS_ROOT/.venv" ]]; then
            oos_log_success "Virtual environment: Present"
        else
            oos_log_info "Virtual environment: Not created (run: oos dev setup)"
        fi

        # Check task database
        if [[ -f "$OOS_ROOT/.oos/tasks/tasks.db" ]]; then
            oos_log_success "Task database: Initialized"
        else
            oos_log_info "Task database: Will be created on first use"
        fi

        # Check .env
        if [[ -f "$OOS_ROOT/.env" ]]; then
            oos_log_success ".env file: Present"
        else
            oos_log_info ".env file: Missing (run: oos dev setup)"
        fi

        echo ""
        echo "Run 'oos status' to see available features"
        ;;

    modules)
        local module="${1:-}"
        if [[ -z "$module" ]]; then
            echo "Available modules:"
            echo "  security    Security checks"
            echo "  testing     Run tests"
            echo "  python      Python environment"
            echo "  git         Git status"
        else
            if [[ -f "$OOS_ROOT/modules/$module/"*.sh ]]; then
                exec "$OOS_ROOT/modules/$module/"*.sh
            else
                oos_log_error "Module not found: $module"
                exit 1
            fi
        fi
        ;;

    help|--help|-h)
        cat << 'EOF'
OOS Development Environment

USAGE:
    oos dev <subcommand>

SUBCOMMANDS:
    setup       Complete development environment setup
    check       Validate environment health
    modules     Run development modules

EXAMPLES:
    oos dev setup
    oos dev check
    oos dev modules security
EOF
        ;;

    *)
        oos_log_error "Unknown subcommand: $subcommand"
        echo "Run 'oos dev help' for usage"
        exit 1
        ;;
esac
