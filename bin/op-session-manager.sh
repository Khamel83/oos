#!/bin/bash

# 1Password CLI Session Manager for OCI VM
# Handles persistent sessions without desktop app integration

set -euo pipefail

# Configuration
OP_SESSION_FILE="$HOME/.op_session"
OP_SESSION_DURATION="${OP_SESSION_DURATION:-12h}"
OP_ACCOUNT="${OP_ACCOUNT:-}"

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

# Check if session file exists and is recent
is_session_valid() {
    if [[ ! -f "$OP_SESSION_FILE" ]]; then
        return 1
    fi

    # Check if file is older than session duration (convert to seconds)
    local max_age_seconds
    case "$OP_SESSION_DURATION" in
        *h) max_age_seconds=$((${OP_SESSION_DURATION%h} * 3600)) ;;
        *m) max_age_seconds=$((${OP_SESSION_DURATION%m} * 60)) ;;
        *) max_age_seconds=43200 ;; # Default 12 hours
    esac

    local file_age=$(($(date +%s) - $(stat -c %Y "$OP_SESSION_FILE" 2>/dev/null || echo 0)))

    if [[ $file_age -gt $max_age_seconds ]]; then
        log_warning "Session file is older than ${OP_SESSION_DURATION}, needs refresh"
        return 1
    fi

    # Load session and test it
    if source "$OP_SESSION_FILE" 2>/dev/null && op account list >/dev/null 2>&1; then
        return 0
    else
        log_warning "Session file exists but session is invalid"
        return 1
    fi
}

# Interactive signin with better UX
signin_interactive() {
    log_info "Starting 1Password CLI signin process..."

    # Try service account authentication first (most reliable for automation)
    if command -v ./bin/op-auth-automated.sh >/dev/null 2>&1; then
        log_info "Trying automated service account authentication..."
        if ./bin/op-auth-automated.sh ensure >/dev/null 2>&1; then
            log_success "Service account authentication successful"
            return 0
        fi
        log_info "Service account authentication not available, trying traditional method..."
    fi

    # Check available accounts
    local accounts
    if accounts=$(op account list --format json 2>/dev/null); then
        if [[ "$accounts" == "[]" ]]; then
            log_warning "No 1Password accounts configured yet"
            log_info "To add a 1Password account, you need:"
            log_info "  1. Your account sign-in address (e.g., my.1password.com)"
            log_info "  2. Your email address"
            log_info "  3. Your Secret Key"
            log_info "  4. Your account password"
            echo

            # Try to get account details from environment variables
            if [[ -n "${OP_ACCOUNT_ADDRESS:-}" && -n "${OP_ACCOUNT_EMAIL:-}" ]]; then
                # Validate address format - should be a domain, not a secret key
                if [[ "$OP_ACCOUNT_ADDRESS" == *"-"* ]] && [[ ${#OP_ACCOUNT_ADDRESS} -gt 20 ]]; then
                    log_error "Invalid format for OP_ACCOUNT_ADDRESS"
                    log_warning "This appears to be a Secret Key, not a sign-in address"
                    log_info ""
                    log_info "Your OP_ACCOUNT_ADDRESS should be like: my.1password.com"
                    log_info "Your OP_ACCOUNT_EMAIL should be like: your-email@example.com"
                    log_info ""
                    log_info "The Secret Key should be provided during the signin process, not as an environment variable"
                    return 1
                fi

                log_info "Using account details from environment variables..."
                log_info "Address: $OP_ACCOUNT_ADDRESS"
                log_info "Email: $OP_ACCOUNT_EMAIL"

                # Try automated authentication first
                log_info "Attempting automated authentication..."
                if ./bin/op-auth-automated.sh ensure; then
                    log_success "Automated authentication successful"
                    return 0
                else
                    log_warning "Automated authentication failed"
                    log_info ""
                    log_info "For automated environments, set up a service account:"
                    log_info "  1. Create service account: op service-account create my-agent --vault VaultName:read_items"
                    log_info "  2. Set environment variable: export OP_SERVICE_ACCOUNT_TOKEN=\"your-token\""
                    log_info "  3. Run: ./bin/op-auth-automated.sh ensure"
                    log_info ""
                    log_info "For one-time interactive setup, use:"
                    log_info "  bash -ilc 'op account add --address $OP_ACCOUNT_ADDRESS --email $OP_ACCOUNT_EMAIL --signin'"
                    return 1
                fi
            else
                log_error "Account details not found in environment variables"
                log_info "To configure an account, set these environment variables:"
                log_info "  export OP_ACCOUNT_ADDRESS=\"your-account.1password.com\""
                log_info "  export OP_ACCOUNT_EMAIL=\"your-email@example.com\""
                log_info "Then run: ./bin/op-session-manager.sh signin"
                log_info ""
                log_info "Or add manually: op account add --address <address> --email <email> --signin"
                return 1
            fi
        else
            log_info "Available accounts:"
            echo "$accounts" | jq -r '.[] | "  - \(.url) (\(.email))"' 2>/dev/null || echo "$accounts"
        fi
    fi

    log_info "Please sign in (session will last ${OP_SESSION_DURATION})..."

    # Attempt signin with duration
    local signin_output
    if signin_output=$(op signin --duration "$OP_SESSION_DURATION" --raw 2>/dev/null); then
        # Save session token
        echo "export OP_SESSION_TOKEN=\"$signin_output\"" > "$OP_SESSION_FILE"
        chmod 600 "$OP_SESSION_FILE"

        # Load the session
        source "$OP_SESSION_FILE"

        log_success "Successfully signed in to 1Password CLI"
        log_info "Session saved to $OP_SESSION_FILE (expires in ${OP_SESSION_DURATION})"
        return 0
    else
        log_error "Failed to sign in to 1Password CLI"
        return 1
    fi
}

# Load existing session
load_session() {
    if [[ -f "$OP_SESSION_FILE" ]]; then
        source "$OP_SESSION_FILE"
        log_success "Loaded existing 1Password session"
        return 0
    fi
    return 1
}

# Main session management
ensure_session() {
    if is_session_valid; then
        load_session
        log_success "1Password CLI session is active"
        return 0
    else
        log_info "No valid 1Password session found"
        signin_interactive
    fi
}

# Status check
status() {
    echo -e "${BLUE}🔍 1Password CLI Status${NC}"
    echo "=========================="

    echo -n "CLI Version: "
    op --version 2>/dev/null || echo "Not installed"

    echo -n "Session File: "
    if [[ -f "$OP_SESSION_FILE" ]]; then
        echo "$(stat -c '%y' "$OP_SESSION_FILE")"
    else
        echo "Not found"
    fi

    echo -n "Authentication: "
    if op account list >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Signed in${NC}"
        op account list
    else
        echo -e "${RED}❌ Not signed in${NC}"
    fi
}

# Cleanup session
signout() {
    if [[ -f "$OP_SESSION_FILE" ]]; then
        rm -f "$OP_SESSION_FILE"
        log_success "Removed session file"
    fi

    if op signout >/dev/null 2>&1; then
        log_success "Signed out of 1Password CLI"
    else
        log_warning "Already signed out or no active session"
    fi
}

# Refresh session
refresh() {
    log_info "Refreshing 1Password session..."
    signout
    signin_interactive
}

# Usage information
usage() {
    cat << EOF
1Password CLI Session Manager for OCI VM

Usage: $0 [COMMAND]

Commands:
    ensure      Ensure valid session exists (signin if needed)
    signin      Interactive signin with persistent session
    signout     Sign out and cleanup session
    refresh     Refresh existing session
    status      Show current authentication status
    help        Show this help message

Environment Variables:
    OP_SESSION_DURATION    Session duration (default: 12h)
    OP_ACCOUNT            Specific account URL/ID

Examples:
    $0 ensure           # Ensure session (most common)
    $0 signin           # Force new signin
    $0 status           # Check current status

    OP_SESSION_DURATION=24h $0 signin  # 24-hour session

Session File: $OP_SESSION_FILE
EOF
}

# Main command dispatch
case "${1:-ensure}" in
    ensure)
        ensure_session
        ;;
    signin)
        signin_interactive
        ;;
    signout|logout)
        signout
        ;;
    refresh)
        refresh
        ;;
    status)
        status
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        log_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac