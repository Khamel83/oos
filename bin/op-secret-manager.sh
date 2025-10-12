#!/bin/bash

# OOS 1Password Secret Manager
# Persistent connection to 1Password for on-demand secret access

set -euo pipefail

# Configuration
OP_SERVICE_ACCOUNT_FILE="$HOME/.op_service_account"
OP_SESSION_FILE="$HOME/.op_session"
OP_CACHE_DIR="$HOME/.op_cache"
OP_CONNECTION_STATUS_FILE="$OP_CACHE_DIR/connection_status"
OP_VAULT="Dev"
OP_BOOTSTRAP_ITEM="bootstrap-env"

# Create cache directory
mkdir -p "$OP_CACHE_DIR"

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

log_debug() {
    echo -e "${CYAN}🔧 $1${NC}"
}

# Check if 1Password connection is active and valid
is_connection_active() {
    [[ -f "$OP_CONNECTION_STATUS_FILE" ]] || return 1

    local status_time
    status_time=$(cat "$OP_CONNECTION_STATUS_FILE" 2>/dev/null || echo "0")
    local current_time=$(date +%s)
    local age=$((current_time - status_time))

    # Connection is valid for 1 hour (3600 seconds)
    [[ $age -lt 3600 ]]
}

# Establish or verify 1Password connection
establish_connection() {
    log_debug "Establishing 1Password connection..."

    # Check if we have a valid service account session
    if [[ -f "$OP_SESSION_FILE" ]] && source "$OP_SESSION_FILE" 2>/dev/null; then
        if [[ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]] && op whoami >/dev/null 2>&1; then
            log_debug "Service account session is valid"
            echo "$(date +%s)" > "$OP_CONNECTION_STATUS_FILE"
            return 0
        fi
    fi

    # Try to authenticate using automated system
    if ./bin/op-auth-automated.sh ensure >/dev/null 2>&1; then
        log_debug "Automated authentication successful"
        echo "$(date +%s)" > "$OP_CONNECTION_STATUS_FILE"
        return 0
    fi

    log_error "Failed to establish 1Password connection"
    return 1
}

# Get a secret from 1Password
get_secret() {
    local secret_name="$1"
    local field="${2:-password}"  # Default to password field

    log_debug "Retrieving secret: $secret_name (field: $field)"

    # Ensure connection is active
    if ! is_connection_active; then
        establish_connection || return 1
    fi

    # Load session and get the secret
    if source "$OP_SESSION_FILE" 2>/dev/null; then
        # Try to get the item
        local secret_value
        if secret_value=$(op item get "$secret_name" --vault "$OP_VAULT" --field "$field" 2>/dev/null); then
            echo "$secret_value"
            return 0
        else
            log_error "Secret '$secret_name' not found in vault '$OP_VAULT'"
            return 1
        fi
    else
        log_error "Failed to load 1Password session"
        return 1
    fi
}

# List all available secrets
list_secrets() {
    log_debug "Listing secrets in vault '$OP_VAULT'"

    # Ensure connection is active
    if ! is_connection_active; then
        establish_connection || return 1
    fi

    # Load session and list items
    if source "$OP_SESSION_FILE" 2>/dev/null; then
        echo "Available secrets in vault '$OP_VAULT':"
        op item list --vault "$OP_VAULT" --format json 2>/dev/null | \
            jq -r '.[] | "- \(.title) (ID: \(.id))"' 2>/dev/null || \
            op item list --vault "$OP_VAULT" 2>/dev/null | \
            grep -E "^\s*[0-9]+\." | sed 's/^\s*[0-9]*\.\s*/- /'
    else
        log_error "Failed to load 1Password session"
        return 1
    fi
}

# Show connection status
show_status() {
    echo "=== 1Password Secret Manager Status ==="
    echo

    if is_connection_active; then
        echo "Connection: ✅ Active"
        local status_time=$(cat "$OP_CONNECTION_STATUS_FILE" 2>/dev/null || echo "0")
        local current_time=$(date +%s)
        local age=$((current_time - status_time))
        echo "Age: ${age}s (expires in $((3600 - age))s)"
    else
        echo "Connection: ❌ Inactive"
    fi

    echo

    if [[ -f "$OP_SESSION_FILE" ]]; then
        echo "Session File: ✅ Exists"
        if source "$OP_SESSION_FILE" 2>/dev/null; then
            if [[ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]]; then
                echo "Type: Service Account"
                if op whoami >/dev/null 2>&1; then
                    echo "Status: ✅ Valid"
                    local account_info=$(op whoami 2>/dev/null || echo "Unknown")
                    echo "$account_info"
                else
                    echo "Status: ❌ Invalid"
                fi
            fi
        fi
    else
        echo "Session File: ❌ Not found"
    fi

    echo
    echo "Target Vault: $OP_VAULT"
    echo "Bootstrap Item: $OP_BOOTSTRAP_ITEM"
}

# Bootstrap environment variables from 1Password
bootstrap_environment() {
    log_info "Bootstrapping environment from 1Password..."

    # Ensure connection is active
    if ! is_connection_active; then
        establish_connection || return 1
    fi

    # Load session and get bootstrap item
    if source "$OP_SESSION_FILE" 2>/dev/null; then
        # Get all fields from the bootstrap item
        local bootstrap_data
        if bootstrap_data=$(op item get "$OP_BOOTSTRAP_ITEM" --vault "$OP_VAULT" --format json 2>/dev/null); then
            echo "Bootstrapping environment variables from '$OP_BOOTSTRAP_ITEM'..."

            # Extract and export environment variables
            echo "$bootstrap_data" | jq -r '.fields[] | select(.type == "concealed" or .type == "string") | "export \(.label // .name)=\"\(.value // .secret_content)\""' 2>/dev/null | while IFS= read -r line; do
                if [[ -n "$line" && "$line" != "export =\"" ]]; then
                    echo "  $line"
                    eval "$line"
                fi
            done

            log_success "Environment bootstrapped successfully"
            return 0
        else
            log_error "Bootstrap item '$OP_BOOTSTRAP_ITEM' not found in vault '$OP_VAULT'"
            return 1
        fi
    else
        log_error "Failed to load 1Password session"
        return 1
    fi
}

# Initialize the secret manager (run on system startup)
initialize() {
    # Silent initialization for shell startup - only output errors
    if establish_connection >/dev/null 2>&1; then
        return 0
    else
        log_error "Failed to initialize 1Password Secret Manager" >&2
        return 1
    fi
}

# Close the connection (cleanup)
close_connection() {
    log_info "Closing 1Password connection..."
    rm -f "$OP_CONNECTION_STATUS_FILE"
    log_success "Connection closed"
}

# Show help
show_help() {
    cat << EOF
OOS 1Password Secret Manager

Provides persistent connection to 1Password for automated secret access.

Usage: $0 [COMMAND] [options]

Commands:
    init                    Initialize secret manager (run on startup)
    get <secret> [field]    Get a specific secret value
    list                    List all available secrets
    bootstrap               Load bootstrap environment variables
    status                  Show connection status
    close                   Close connection
    help                    Show this help

Examples:
    $0 init                           # Initialize on startup
    $0 get "database-password"        # Get password field
    $0 get "api-key" "username"       # Get username field
    $0 list                          # List all secrets
    $0 bootstrap                      # Load environment variables
    $0 status                        # Check status

Configuration:
    OP_VAULT=dev                     # Target vault (default: dev)
    OP_BOOTSTRAP_ITEM=bootstrap-env  # Bootstrap item (default: bootstrap-env)

Integration:
    Add to shell startup: eval \$($0 init)
    Or add to ~/.bashrc: $0 init

EOF
}

# Main command handling
case "${1:-}" in
    init|initialize)
        initialize
        ;;
    get)
        if [[ -z "${2:-}" ]]; then
            log_error "Missing secret name"
            echo "Usage: $0 get <secret-name> [field]"
            exit 1
        fi
        get_secret "$2" "${3:-password}"
        ;;
    list|ls)
        list_secrets
        ;;
    bootstrap|boot)
        bootstrap_environment
        ;;
    status|st)
        show_status
        ;;
    close|disconnect)
        close_connection
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: ${1:-}"
        echo
        show_help
        exit 1
        ;;
esac