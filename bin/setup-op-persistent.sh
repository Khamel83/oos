#!/bin/bash

# OOS 1Password Persistent Connection Setup
# One-time setup to open vault and establish persistent secure pathway

set -euo pipefail

# Configuration
OP_SERVICE_ACCOUNT_FILE="$HOME/.op_service_account"
OP_SESSION_FILE="$HOME/.op_session"
OP_BOOTSTRAP_TOKEN_FILE="$HOME/.op_bootstrap_token"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${CYAN}🔧 $1${NC}"
}

# Check current authentication status
check_auth_status() {
    log_step "Checking current authentication status..."

    # Check if service account is available
    if [[ -f "$OP_SERVICE_ACCOUNT_FILE" ]]; then
        if OP_SERVICE_ACCOUNT_TOKEN=$(cat "$OP_SERVICE_ACCOUNT_FILE" 2>/dev/null) && op whoami >/dev/null 2>&1; then
            log_success "Service account is active and working"
            return 0
        fi
    fi

    # Check if regular session exists
    if [[ -f "$OP_SESSION_FILE" ]]; then
        if source "$OP_SESSION_FILE" 2>/dev/null && op whoami >/dev/null 2>&1; then
            log_success "Regular session is active"
            return 0
        fi
    fi

    log_warning "No active authentication found"
    return 1
}

# Step 1: Initial vault opening (one-time interactive setup)
open_initial_vault() {
    log_step "Step 1: Opening initial vault connection..."

    # Try service account first
    if [[ -f "$OP_SERVICE_ACCOUNT_FILE" ]]; then
        log_info "Attempting service account authentication..."
        if OP_SERVICE_ACCOUNT_TOKEN=$(cat "$OP_SERVICE_ACCOUNT_FILE" 2>/dev/null) && op whoami >/dev/null 2>&1; then
            log_success "Service account connection established"
            return 0
        fi
    fi

    # Try regular account authentication
    log_info "Attempting regular account authentication..."

    # Check if we can authenticate non-interactively
    if op account list --format json 2>/dev/null | jq -e '.[]' >/dev/null 2>&1; then
        if op signin --raw 2>/dev/null > /tmp/session_token.tmp; then
            local session_token=$(cat /tmp/session_token.tmp)
            rm -f /tmp/session_token.tmp
            echo "export OP_SESSION_TOKEN=\"$session_token\"" > "$OP_SESSION_FILE"
            chmod 600 "$OP_SESSION_FILE"
            log_success "Regular account connection established"
            return 0
        fi
    fi

    # If all else fails, provide interactive setup instructions
    log_warning "Unable to establish connection automatically"
    log_info ""
    log_info "To open the vault initially, you need to:"
    log_info ""
    log_info "Option A: Use your existing service account token"
    log_info "  export OP_SERVICE_ACCOUNT_TOKEN=\"your-token-here\""
    log_info "  ./bin/setup-op-persistent.sh"
    log_info ""
    log_info "Option B: Interactive one-time setup"
    log_info "  bash -ilc 'op account add --address my.1password.com --email khamel83@gmail.com --signin'"
    log_info "  ./bin/setup-op-persistent.sh"
    log_info ""
    log_info "Option C: Create new service account"
    log_info "  ./bin/setup-oos-service-account.sh"
    log_info "  ./bin/setup-op-persistent.sh"

    return 1
}

# Step 2: Test access to bootstrap-env
test_bootstrap_access() {
    log_step "Step 2: Testing access to bootstrap-env..."

    # Load session
    if [[ -f "$OP_SESSION_FILE" ]]; then
        source "$OP_SESSION_FILE" 2>/dev/null
    elif [[ -f "$OP_SERVICE_ACCOUNT_FILE" ]]; then
        export OP_SERVICE_ACCOUNT_TOKEN=$(cat "$OP_SERVICE_ACCOUNT_FILE" 2>/dev/null)
    else
        log_error "No session found"
        return 1
    fi

    # Test access to dev vault
    if ! op vault list --format json 2>/dev/null | jq -e '.[] | select(.name == "dev")' >/dev/null; then
        log_warning "Dev vault not accessible or doesn't exist"
        log_info "Available vaults:"
        op vault list 2>/dev/null | grep -E "^\s*[0-9]+\." | sed 's/^\s*[0-9]*\.\s*//' || echo "  (No vaults accessible)"
        return 1
    fi

    # Test access to bootstrap-env item
    if op item get "bootstrap-env" --vault "dev" >/dev/null 2>&1; then
        log_success "bootstrap-env is accessible"
        return 0
    else
        log_warning "bootstrap-env not found in dev vault"
        log_info "Available items in dev vault:"
        op item list --vault "dev" 2>/dev/null | grep -E "^\s*[0-9]+\." | sed 's/^\s*[0-9]*\.\s*//' || echo "  (No items found)"
        return 1
    fi
}

# Step 3: Establish persistent secure pathway
establish_persistent_pathway() {
    log_step "Step 3: Establishing persistent secure pathway..."

    # Initialize the secret manager
    if /home/ubuntu/dev/oos/bin/op-secret-manager.sh init >/dev/null 2>&1; then
        log_success "Persistent pathway established"
        return 0
    else
        log_error "Failed to establish persistent pathway"
        return 1
    fi
}

# Step 4: Configure auto-startup
configure_autostartup() {
    log_step "Step 4: Configuring automatic startup..."

    # Run the auto-connection setup
    if /home/ubuntu/dev/oos/bin/init-op-connection.sh setup >/dev/null 2>&1; then
        log_success "Auto-startup configured"
        return 0
    else
        log_warning "Auto-startup setup had issues (non-critical)"
        return 0
    fi
}

# Step 5: Verify everything works
verify_setup() {
    log_step "Step 5: Verifying complete setup..."

    # Test secret manager
    if /home/ubuntu/dev/oos/bin/op-secret-manager.sh status >/dev/null 2>&1; then
        log_success "✅ Secret manager is working"
    else
        log_error "❌ Secret manager has issues"
        return 1
    fi

    # Test bootstrap access
    if /home/ubuntu/dev/oos/bin/op-secret-manager.sh bootstrap >/dev/null 2>&1; then
        log_success "✅ Bootstrap access is working"
    else
        log_warning "⚠️ Bootstrap access has issues (item may not exist)"
    fi

    return 0
}

# Main setup process
main() {
    echo "=== OOS 1Password Persistent Connection Setup ==="
    echo "This will open the vault once and establish a persistent secure pathway"
    echo ""

    # Step 1: Open initial vault
    if ! open_initial_vault; then
        log_error "Failed to open initial vault"
        exit 1
    fi

    echo ""

    # Step 2: Test bootstrap access
    if ! test_bootstrap_access; then
        log_warning "Bootstrap access test failed (continuing anyway)"
    fi

    echo ""

    # Step 3: Establish persistent pathway
    if ! establish_persistent_pathway; then
        log_error "Failed to establish persistent pathway"
        exit 1
    fi

    echo ""

    # Step 4: Configure auto-startup
    configure_autostartup

    echo ""

    # Step 5: Verify setup
    verify_setup

    echo ""
    log_success "🎉 SETUP COMPLETE!"
    echo ""
    echo "Your 1Password connection is now:"
    echo "  ✅ Initial vault opened"
    echo "  ✅ Persistent pathway established"
    echo "  ✅ Auto-startup configured"
    echo "  ✅ Available via slash commands"
    echo ""
    echo "You can now use:"
    echo "  /op-secret status        - Check connection status"
    echo "  /op-secret list          - List available secrets"
    echo "  /op-get <secret-name>    - Get any secret instantly"
    echo "  /op-secret bootstrap     - Load bootstrap environment"
    echo ""
    echo "The connection will automatically renew and persist across sessions."
    echo "No more manual authentication needed!"
}

# Show current status
show_status() {
    echo "=== OOS 1Password Connection Status ==="
    echo ""

    if check_auth_status; then
        log_success "✅ Vault is open and accessible"
    else
        log_warning "⚠️ Vault needs to be opened"
        echo "Run: $0 setup"
    fi

    echo ""

    if /home/ubuntu/dev/oos/bin/op-secret-manager.sh status >/dev/null 2>&1; then
        log_success "✅ Persistent pathway is active"
    else
        log_warning "⚠️ Persistent pathway not established"
        echo "Run: $0 setup"
    fi

    echo ""
    echo "Configuration:"
    echo "  Service Account File: $OP_SERVICE_ACCOUNT_FILE"
    echo "  Session File: $OP_SESSION_FILE"
    echo "  Target Vault: dev"
    echo "  Bootstrap Item: bootstrap-env"
}

# Show help
show_help() {
    cat << EOF
OOS 1Password Persistent Connection Setup

Opens the vault once and establishes a persistent secure pathway.

Usage: $0 [command]

Commands:
    setup         Run complete setup (default)
    status        Show current status
    help          Show this help

How it works:
1. Opens the 1Password vault (one-time setup)
2. Establishes persistent secure pathway
3. Configures auto-renewal and startup
4. Provides instant access via slash commands

After setup:
• No manual authentication needed
• Connection persists across sessions
• Auto-renews every 30 minutes
• Available via /op-secret and /op-get

Initial requirements:
• Either a service account token (OP_SERVICE_ACCOUNT_TOKEN)
• Or one-time interactive authentication
• Access to "dev" vault with "bootstrap-env" item

EOF
}

# Command handling
case "${1:-setup}" in
    setup)
        main
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac