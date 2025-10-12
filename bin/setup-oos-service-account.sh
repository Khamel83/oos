#!/bin/bash

# OOS Service Account Setup Script
# Creates a service account with access to the "dev" vault for bootstrap-env

set -euo pipefail

# Configuration
SERVICE_ACCOUNT_NAME="oos-agent"
VAULT_NAME="dev"
ITEM_NAME="bootstrap-env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if user is authenticated with a regular account first
check_user_authentication() {
    log_info "Checking user authentication..."

    if ! op whoami >/dev/null 2>&1; then
        log_error "You need to authenticate with your regular 1Password account first"
        log_info "Please run: op account add --address my.1password.com --email khamel83@gmail.com --signin"
        log_info "Or use: bash -ilc 'op account add --address my.1password.com --email khamel83@gmail.com --signin'"
        return 1
    fi

    log_success "User authentication confirmed"
    return 0
}

# Check if vault exists
check_vault_exists() {
    log_info "Checking if vault '$VAULT_NAME' exists..."

    if op vault list --format json | jq -e ".[] | select(.name == \"$VAULT_NAME\")" >/dev/null 2>&1; then
        log_success "Vault '$VAULT_NAME' found"
        return 0
    else
        log_warning "Vault '$VAULT_NAME' not found"
        log_info "Available vaults:"
        op vault list | grep -E "^\s*[0-9]+\." | sed 's/^\s*[0-9]*\.\s*//'
        return 1
    fi
}

# Check if item exists in vault
check_item_exists() {
    log_info "Checking if item '$ITEM_NAME' exists in vault '$VAULT_NAME'..."

    if op item list --vault "$VAULT_NAME" --format json | jq -e ".[] | select(.title == \"$ITEM_NAME\")" >/dev/null 2>&1; then
        log_success "Item '$ITEM_NAME' found in vault '$VAULT_NAME'"
        return 0
    else
        log_warning "Item '$ITEM_NAME' not found in vault '$VAULT_NAME'"
        log_info "Available items in '$VAULT_NAME':"
        op item list --vault "$VAULT_NAME" | grep -E "^\s*[0-9]+\." | sed 's/^\s*[0-9]*\.\s*//' || echo "  (No items found)"
        return 1
    fi
}

# Create service account with vault access
create_service_account() {
    log_info "Creating service account '$SERVICE_ACCOUNT_NAME' with access to vault '$VAULT_NAME'..."

    # Create service account with read access to the dev vault
    local service_account_output
    if service_account_output=$(op service-account create "$SERVICE_ACCOUNT_NAME" --vault "$VAULT_NAME":read_items --raw 2>/dev/null); then
        log_success "Service account created successfully"
        echo "$service_account_output"
        return 0
    else
        log_error "Failed to create service account"
        return 1
    fi
}

# Test the service account
test_service_account() {
    local service_account_token="$1"

    log_info "Testing service account access..."

    # Test authentication
    if OP_SERVICE_ACCOUNT_TOKEN="$service_account_token" op whoami >/dev/null 2>&1; then
        log_success "Service account authentication works"
    else
        log_error "Service account authentication failed"
        return 1
    fi

    # Test vault access
    if OP_SERVICE_ACCOUNT_TOKEN="$service_account_token" op item list --vault "$VAULT_NAME" >/dev/null 2>&1; then
        log_success "Service account can access vault '$VAULT_NAME'"
    else
        log_error "Service account cannot access vault '$VAULT_NAME'"
        return 1
    fi

    # Test item access
    if OP_SERVICE_ACCOUNT_TOKEN="$service_account_token" op item get "$ITEM_NAME" --vault "$VAULT_NAME" >/dev/null 2>&1; then
        log_success "Service account can access item '$ITEM_NAME'"
    else
        log_warning "Service account cannot access item '$ITEM_NAME' (item may not exist)"
    fi

    return 0
}

# Save service account token
save_service_account_token() {
    local service_account_token="$1"

    log_info "Saving service account token..."

    # Save to file
    echo "$service_account_token" > "$HOME/.op_service_account"
    chmod 600 "$HOME/.op_service_account"

    log_success "Service account token saved to ~/.op_service_account"

    # Show environment variable setup
    log_info "To use this service account, set this environment variable:"
    echo ""
    echo "export OP_SERVICE_ACCOUNT_TOKEN=\"$service_account_token\""
    echo ""
    log_info "Or add it to your shell profile (~/.bashrc, ~/.zshrc, etc.)"
}

# Main setup process
main() {
    echo "=== OOS Service Account Setup ==="
    echo "This will create a service account with access to vault '$VAULT_NAME' and item '$ITEM_NAME'"
    echo ""

    # Check prerequisites
    if ! check_user_authentication; then
        return 1
    fi

    if ! check_vault_exists; then
        log_error "Vault '$VAULT_NAME' not found. Please create it first or update the VAULT_NAME variable."
        return 1
    fi

    # Check if item exists (optional, not required for service account creation)
    check_item_exists || true

    echo ""
    log_info "Ready to create service account '$SERVICE_ACCOUNT_NAME' with read access to vault '$VAULT_NAME'"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Setup cancelled"
        return 0
    fi

    # Create service account
    echo ""
    local service_account_token
    if service_account_token=$(create_service_account); then
        # Test the service account
        echo ""
        if test_service_account "$service_account_token"; then
            # Save the token
            echo ""
            save_service_account_token "$service_account_token"

            echo ""
            log_success "=== Setup Complete ==="
            log_info "Service account '$SERVICE_ACCOUNT_NAME' is ready to use"
            log_info "Test with: ./bin/op-auth-automated.sh ensure"
            log_info "Or: ./bin/op-session-manager.sh ensure"
        else
            log_error "Service account test failed"
            return 1
        fi
    else
        log_error "Failed to create service account"
        return 1
    fi
}

# Show help
show_help() {
    cat << EOF
OOS Service Account Setup Script

Usage: $0 [options]

This script creates a 1Password service account with access to a specific vault and item.

Environment Variables (optional):
    SERVICE_ACCOUNT_NAME    Name for the service account (default: oos-agent)
    VAULT_NAME             Name of the vault to access (default: dev)
    ITEM_NAME              Name of the item to access (default: bootstrap-env)

Prerequisites:
    1. You must be authenticated with your regular 1Password account first
    2. The target vault must exist
    3. You need permission to create service accounts

Authentication:
    op account add --address my.1password.com --email khamel83@gmail.com --signin

Examples:
    $0                                    # Use default settings
    VAULT_NAME=prod $0                    # Use different vault
    SERVICE_ACCOUNT_NAME=my-agent $0      # Use different service account name

EOF
}

# Command line handling
case "${1:-}" in
    help|--help|-h)
        show_help
        ;;
    *)
        main
        ;;
esac