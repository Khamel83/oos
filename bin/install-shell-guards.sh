#!/usr/bin/env bash
set -euo pipefail

# Install Shell Guards - Block Development Commands Without Gate
# This creates command interceptors that prevent development without proper environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[shell-guards]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[shell-guards]${NC} $1"
}

log_error() {
    echo -e "${RED}[shell-guards]${NC} $1" >&2
}

# Create interceptor directory
create_interceptors() {
    local interceptor_dir="$PROJECT_ROOT/bin/interceptors"
    mkdir -p "$interceptor_dir"

    log "Creating command interceptors..."

    # List of commands to intercept
    local commands=("python" "python3" "uv" "pip" "pip3" "pytest" "black" "ruff")

    for cmd in "${commands[@]}"; do
        cat > "$interceptor_dir/$cmd" << 'EOF'
#!/usr/bin/env bash

# Command Interceptor - Requires Development Gate
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Check if gate has been passed recently
if [[ -f "$PROJECT_ROOT/.dev-gate-passed" ]]; then
    # Check if gate is recent (within last hour)
    gate_time=$(stat -c %Y "$PROJECT_ROOT/.dev-gate-passed" 2>/dev/null || stat -f %m "$PROJECT_ROOT/.dev-gate-passed" 2>/dev/null)
    current_time=$(date +%s)
    age=$((current_time - gate_time))

    if [[ $age -lt 3600 ]]; then
        # Gate is recent, allow command
        # Find the real COMMAND_NAME (not our interceptor)
real_command=$(which -a COMMAND_NAME | grep -v interceptors | head -1)
if [[ -z "$real_command" ]]; then
    case COMMAND_NAME in
        python|python3) real_command="/usr/bin/python3" ;;
        uv) real_command="/usr/local/bin/uv" ;;
        *) real_command="/usr/bin/COMMAND_NAME" ;;
    esac
fi
exec "$real_command" "$@"
    fi
fi

# Gate not passed or stale
echo -e "\033[0;31m❌ Development environment not ready\033[0m"
echo -e "\033[0;33mRun: ./bin/dev-gate.sh\033[0m"
echo
echo "This command is blocked until development environment is validated."
echo "Emergency bypass: DEV_GATE_BYPASS=true COMMAND_NAME"
exit 1
EOF

        # Replace COMMAND_NAME placeholder
        sed -i "s/COMMAND_NAME/$cmd/g" "$interceptor_dir/$cmd"
        chmod +x "$interceptor_dir/$cmd"
    done

    log_success "Created interceptors for: ${commands[*]}"
}

# Create shell environment setup
create_shell_setup() {
    local shell_setup="$PROJECT_ROOT/bin/setup-shell-environment.sh"

    log "Creating shell environment setup..."

    cat > "$shell_setup" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Shell Environment Setup for Mandatory Development Gate
# Adds interceptors to PATH and sets up environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Add interceptors to PATH (prepend so they take precedence)
export PATH="$PROJECT_ROOT/bin/interceptors:$PATH"

# Set up gate environment check function
dev_gate_check() {
    if [[ ! -f "$PROJECT_ROOT/.dev-gate-passed" ]]; then
        echo "⚠️  Development gate not passed. Run: ./bin/dev-gate.sh"
        return 1
    fi

    # Check if gate is recent (within last hour)
    gate_time=$(stat -c %Y "$PROJECT_ROOT/.dev-gate-passed" 2>/dev/null || stat -f %m "$PROJECT_ROOT/.dev-gate-passed" 2>/dev/null)
    current_time=$(date +%s)
    age=$((current_time - gate_time))

    if [[ $age -gt 3600 ]]; then
        echo "⚠️  Development gate is stale. Run: ./bin/dev-gate.sh"
        return 1
    fi

    return 0
}

# Add helpful aliases
alias gate='./bin/dev-gate.sh'
alias check-env='dev_gate_check'

# Show status when sourcing
if dev_gate_check 2>/dev/null; then
    echo "✅ Development environment ready"
else
    echo "⚠️  Development environment needs validation"
    echo "Run: ./bin/dev-gate.sh"
fi
EOF

    chmod +x "$shell_setup"
    log_success "Shell environment setup created"
}

# Create auto-setup for common shells
create_shell_integration() {
    local integration_script="$PROJECT_ROOT/bin/integrate-shell.sh"

    log "Creating shell integration script..."

    cat > "$integration_script" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Integrate OOS Development Gate with User Shell
# Automatically adds gate enforcement to shell startup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Shell configuration files to check
SHELL_CONFIGS=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile")

# Integration marker
INTEGRATION_MARKER="# OOS Development Gate Integration"
INTEGRATION_BLOCK="
$INTEGRATION_MARKER
if [[ -f \"$PROJECT_ROOT/bin/setup-shell-environment.sh\" ]]; then
    source \"$PROJECT_ROOT/bin/setup-shell-environment.sh\"
fi
"

echo -e "${BLUE}Integrating OOS Development Gate with shell...${NC}"

# Find which shell config file to use
for config in "${SHELL_CONFIGS[@]}"; do
    if [[ -f "$config" ]]; then
        # Check if already integrated
        if grep -q "$INTEGRATION_MARKER" "$config"; then
            echo -e "${YELLOW}Already integrated with $config${NC}"
            continue
        fi

        echo -e "${BLUE}Adding integration to $config${NC}"
        echo "$INTEGRATION_BLOCK" >> "$config"
        echo -e "${GREEN}✅ Integrated with $config${NC}"

        echo
        echo -e "${YELLOW}To activate in current session:${NC}"
        echo "source $config"
        break
    fi
done

echo
echo -e "${GREEN}Shell integration complete!${NC}"
echo "New shell sessions will have development gate enforcement."
EOF

    chmod +x "$integration_script"
    log_success "Shell integration script created"
}

# Test the interceptors
test_interceptors() {
    log "Testing interceptor functionality..."

    # Remove gate file to test blocking
    rm -f "$PROJECT_ROOT/.dev-gate-passed"

    # Test that python is blocked
    local test_result
    if output=$(./bin/interceptors/python --version 2>&1); then
        log_error "Interceptor failed - python command was not blocked"
        return 1
    else
        log_success "Python command correctly blocked without gate"
    fi

    # Pass the gate
    DEV_GATE_BYPASS=true ./bin/dev-gate.sh >/dev/null 2>&1 || true

    # Test that python works with gate
    if ./bin/interceptors/python --version >/dev/null 2>&1; then
        log_success "Python command works after gate passes"
    else
        log_error "Interceptor failed - python blocked even with gate"
        return 1
    fi
}

# Main installation function
main() {
    echo -e "\n${BOLD}${BLUE}🛡️  Installing Shell Guards for Development Gate${NC}"
    echo "=================================================="

    create_interceptors
    create_shell_setup
    create_shell_integration
    test_interceptors

    echo
    log_success "Shell guards installed successfully!"

    echo
    echo -e "${YELLOW}What this provides:${NC}"
    echo "  🚫 Blocks python/uv/pip commands without gate"
    echo "  ⏰ Automatically expires after 1 hour"
    echo "  🔧 Easy shell integration available"
    echo
    echo -e "${BLUE}To activate shell integration:${NC}"
    echo "  ./bin/integrate-shell.sh"
    echo
    echo -e "${BLUE}Manual activation (current session):${NC}"
    echo "  source ./bin/setup-shell-environment.sh"
    echo
    echo -e "${GREEN}Result: Commands literally won't work without proper environment${NC}"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi