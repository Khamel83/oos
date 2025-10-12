#!/bin/bash

# 1Password CLI Setup for OCI VM
# One-time setup script for optimal 1Password CLI experience on OCI VMs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo -e "${BLUE}🔧 1Password CLI Setup for OCI VM${NC}"
echo "===================================="

# Check if 1Password CLI is installed
if ! command -v op &> /dev/null; then
    log_error "1Password CLI is not installed"
    echo "Install with:"
    echo "  curl -sS https://downloads.1password.com/linux/keys/1password.asc | gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg"
    echo "  echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/amd64 stable main' | sudo tee /etc/apt/sources.list.d/1password.list"
    echo "  sudo apt update && sudo apt install 1password-cli"
    exit 1
fi

log_success "1Password CLI v$(op --version) installed"

# Setup shell integration
SHELL_RC=""
case "$SHELL" in
    */bash) SHELL_RC="$HOME/.bashrc" ;;
    */zsh) SHELL_RC="$HOME/.zshrc" ;;
    *) log_warning "Unknown shell: $SHELL" ;;
esac

if [[ -n "$SHELL_RC" && -f "$SHELL_RC" ]]; then
    log_info "Setting up shell integration in $SHELL_RC"

    # Add convenience functions
    cat >> "$SHELL_RC" << 'EOF'

# 1Password CLI Session Management
export OP_SESSION_DURATION="${OP_SESSION_DURATION:-12h}"

# Convenience aliases
alias op-signin='~/dev/oos/bin/op-session-manager.sh signin'
alias op-status='~/dev/oos/bin/op-session-manager.sh status'
alias op-ensure='~/dev/oos/bin/op-session-manager.sh ensure'
alias op-refresh='~/dev/oos/bin/op-session-manager.sh refresh'

# Auto-load session on shell startup (optional)
# if command -v ~/dev/oos/bin/op-session-manager.sh &> /dev/null; then
#     ~/dev/oos/bin/op-session-manager.sh ensure 2>/dev/null || true
# fi
EOF

    log_success "Shell integration added to $SHELL_RC"
    log_info "Restart your shell or run: source $SHELL_RC"
else
    log_warning "Could not setup shell integration automatically"
fi

# Create initial session
log_info "Setting up initial 1Password session..."
if "$SCRIPT_DIR/op-session-manager.sh" signin; then
    log_success "Initial session created successfully"
else
    log_warning "Could not create initial session - run manually later"
fi

# Setup cron job for session refresh (optional)
read -p "Setup automatic session refresh via cron? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CRON_JOB="0 */6 * * * $SCRIPT_DIR/op-session-manager.sh ensure 2>/dev/null || true"

    if crontab -l 2>/dev/null | grep -q "op-session-manager"; then
        log_info "Cron job already exists"
    else
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        log_success "Cron job added: refresh session every 6 hours"
    fi
fi

# Final status check
echo
log_info "Final setup verification:"
"$SCRIPT_DIR/op-session-manager.sh" status

echo
log_success "1Password CLI setup complete!"
echo
echo "Available commands:"
echo "  op-signin   - Sign in to 1Password"
echo "  op-status   - Check session status"
echo "  op-ensure   - Ensure valid session"
echo "  op-refresh  - Refresh session"
echo
echo "Or use the full script:"
echo "  $SCRIPT_DIR/op-session-manager.sh [command]"