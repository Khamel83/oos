#!/bin/bash

# 1Password Automated Authentication Manager
# For non-interactive, automated environments like CI/CD, agents, and VMs

set -euo pipefail

# Configuration
OP_SERVICE_ACCOUNT_FILE="$HOME/.op_service_account"
OP_SESSION_FILE="$HOME/.op_session"
OP_SESSION_DURATION="${OP_SESSION_DURATION:-12h}"

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

# Check if service account token is available and valid
is_service_account_available() {
    [[ -f "$OP_SERVICE_ACCOUNT_FILE" ]] && [[ -s "$OP_SERVICE_ACCOUNT_FILE" ]]
}

# Check if session is valid
is_session_valid() {
    if [[ ! -f "$OP_SESSION_FILE" ]]; then
        return 1
    fi

    # Check if file is older than session duration
    local max_age_seconds
    case "$OP_SESSION_DURATION" in
        *h) max_age_seconds=$((${OP_SESSION_DURATION%h} * 3600)) ;;
        *m) max_age_seconds=$((${OP_SESSION_DURATION%m} * 60)) ;;
        *) max_age_seconds=43200 ;; # Default 12 hours
    esac

    local file_age=$(($(date +%s) - $(stat -c %Y "$OP_SESSION_FILE" 2>/dev/null || echo 0)))

    if [[ $file_age -gt $max_age_seconds ]]; then
        return 1
    fi

    # Test session
    if source "$OP_SESSION_FILE" 2>/dev/null && op whoami >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Authenticate using service account token
authenticate_service_account() {
    log_info "Authenticating with 1Password service account..."

    if ! is_service_account_available; then
        log_error "Service account token not found"
        log_info "Expected location: $OP_SERVICE_ACCOUNT_FILE"
        return 1
    fi

    # Load service account token
    local service_account_token
    service_account_token=$(cat "$OP_SERVICE_ACCOUNT_FILE")

    # Try to authenticate using service account
    if OP_SERVICE_ACCOUNT_TOKEN="$service_account_token" op whoami >/dev/null 2>&1; then
        log_success "Successfully authenticated with service account"

        # Create session file with service account token
        echo "export OP_SERVICE_ACCOUNT_TOKEN=\"$service_account_token\"" > "$OP_SESSION_FILE"
        chmod 600 "$OP_SESSION_FILE"

        log_info "Service account session saved to $OP_SESSION_FILE"
        return 0
    else
        log_error "Failed to authenticate with service account"
        log_info "Please check if the service account token is valid and has proper permissions"
        return 1
    fi
}

# Authenticate using session token (traditional method)
authenticate_session_token() {
    log_info "Attempting traditional session authentication..."

    # Try to use existing session or create new one
    if op signin --raw 2>/dev/null > /tmp/session_token.tmp; then
        local session_token
        session_token=$(cat /tmp/session_token.tmp)
        rm -f /tmp/session_token.tmp

        echo "export OP_SESSION_TOKEN=\"$session_token\"" > "$OP_SESSION_FILE"
        chmod 600 "$OP_SESSION_FILE"

        log_success "Successfully authenticated with session token"
        return 0
    else
        log_warning "Session authentication failed"
        return 1
    fi
}

# Setup service account from environment variables
setup_service_account_from_env() {
    if [[ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]]; then
        log_info "Setting up service account from environment variable..."
        echo "$OP_SERVICE_ACCOUNT_TOKEN" > "$OP_SERVICE_ACCOUNT_FILE"
        chmod 600 "$OP_SERVICE_ACCOUNT_FILE"
        log_success "Service account token saved to $OP_SERVICE_ACCOUNT_FILE"
        return 0
    fi
    return 1
}

# Main authentication function
authenticate() {
    log_info "Starting 1Password automated authentication..."

    # Setup service account from environment if available
    setup_service_account_from_env

    # Try service account authentication first (most reliable for automation)
    if is_service_account_available; then
        if authenticate_service_account; then
            return 0
        fi
    fi

    # Fallback to session token authentication
    if authenticate_session_token; then
        return 0
    fi

    # All methods failed
    log_error "All authentication methods failed"
    log_info ""
    log_info "To set up automated authentication, choose one of these methods:"
    log_info ""
    log_info "Method 1: Service Account (Recommended for automation)"
    log_info "  1. Create a service account in 1Password:"
    log_info "     op service-account create your-service-account --vault VaultName:read_items"
    log_info "  2. Save the token securely and set it as environment variable:"
    log_info "     export OP_SERVICE_ACCOUNT_TOKEN=\"your-service-account-token\""
    log_info "  3. Run: ./bin/op-auth-automated.sh authenticate"
    log_info ""
    log_info "Method 2: Session Token (For development/testing)"
    log_info "  1. Set up account interactively first:"
    log_info "     op account add --address your-account.1password.com --email your@email.com --signin"
    log_info "  2. Run: ./bin/op-auth-automated.sh authenticate"
    log_info ""
    log_info "Method 3: Save service account token to file:"
    log_info "  echo \"your-service-account-token\" > ~/.op_service_account"
    log_info "  chmod 600 ~/.op_service_account"
    log_info ""

    return 1
}

# Ensure valid authentication exists
ensure() {
    if is_session_valid; then
        log_success "Valid 1Password authentication already exists"
        return 0
    fi

    log_info "No valid authentication found, attempting to authenticate..."
    authenticate
}

# Show authentication status
status() {
    echo "=== 1Password Automated Authentication Status ==="
    echo

    if [[ -f "$OP_SERVICE_ACCOUNT_FILE" ]]; then
        echo "Service Account: ✅ Configured"
        echo "File: $OP_SERVICE_ACCOUNT_FILE"
        if OP_SERVICE_ACCOUNT_TOKEN=$(cat "$OP_SERVICE_ACCOUNT_FILE" 2>/dev/null); then
            if OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" op whoami >/dev/null 2>&1; then
                echo "Status: ✅ Valid"
                OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" op whoami 2>/dev/null || echo "Account: Unable to fetch account info"
            else
                echo "Status: ❌ Invalid token"
            fi
        fi
    else
        echo "Service Account: ❌ Not configured"
    fi

    echo

    if [[ -f "$OP_SESSION_FILE" ]]; then
        echo "Session File: ✅ Exists"
        echo "File: $OP_SESSION_FILE"
        if source "$OP_SESSION_FILE" 2>/dev/null; then
            if [[ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]]; then
                echo "Type: Service Account"
            elif [[ -n "${OP_SESSION_TOKEN:-}" ]]; then
                echo "Type: Session Token"
            fi

            if op whoami >/dev/null 2>&1; then
                echo "Status: ✅ Valid"
                op whoami 2>/dev/null || echo "Account: Unable to fetch account info"
            else
                echo "Status: ❌ Invalid session"
            fi
        else
            echo "Status: ❌ Cannot load session file"
        fi
    else
        echo "Session File: ❌ Not found"
    fi

    echo
}

# Show help
show_help() {
    cat << EOF
1Password Automated Authentication Manager

Usage: $0 [COMMAND]

Commands:
    authenticate     Authenticate with 1Password (tries all available methods)
    ensure           Ensure valid authentication exists (most common usage)
    status           Show current authentication status
    help             Show this help message

Authentication Methods (in order of preference):
1. Service Account Token (recommended for automation)
2. Session Token (traditional method)

Environment Variables:
    OP_SERVICE_ACCOUNT_TOKEN    Service account token for automated auth
    OP_SESSION_DURATION         Session duration (default: 12h)

Examples:
    $0 ensure                    # Ensure authentication (most common)
    $0 status                    # Check status
    $0 authenticate              # Force authentication

Setup Service Account:
    op service-account create my-agent --vault MyVault:read_items
    export OP_SERVICE_ACCOUNT_TOKEN="token-from-command-above"
    $0 ensure

EOF
}

# Main command handling
case "${1:-}" in
    authenticate|auth)
        authenticate
        ;;
    ensure)
        ensure
        ;;
    status)
        status
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