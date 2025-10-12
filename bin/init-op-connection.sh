#!/bin/bash

# OOS 1Password Auto-Connection Script
# Ensures 1Password connection is always active on system startup

set -euo pipefail

# Add to shell profile for automatic startup
add_to_shell_profile() {
    local profile_file="$1"
    local init_line='eval $(/home/ubuntu/dev/oos/bin/op-secret-manager.sh init 2>/dev/null || true)'

    if [[ -f "$profile_file" ]]; then
        if ! grep -q "op-secret-manager.sh init" "$profile_file"; then
            echo "" >> "$profile_file"
            echo "# OOS 1Password Secret Manager - Auto-start" >> "$profile_file"
            echo "$init_line" >> "$profile_file"
            echo "Added to $profile_file"
        else
            echo "Already configured in $profile_file"
        fi
    fi
}

# Create systemd service for persistent connection
create_systemd_service() {
    local service_file="/etc/systemd/user/oos-op-connection.service"

    cat > /tmp/oos-op-connection.service << EOF
[Unit]
Description=OOS 1Password Secret Manager Connection
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/home/ubuntu/dev/oos/bin/op-secret-manager.sh init
ExecStop=/home/ubuntu/dev/oos/bin/op-secret-manager.sh close
Restart=on-failure
RestartSec=30
Environment=HOME=/home/ubuntu

[Install]
WantedBy=default.target
EOF

    echo "Systemd service file created at /tmp/oos-op-connection.service"
    echo "To install: sudo cp /tmp/oos-op-connection.service $service_file"
    echo "To enable: systemctl --user enable oos-op-connection"
    echo "To start: systemctl --user start oos-op-connection"
}

# Create cron job for connection renewal
create_cron_job() {
    local cron_entry="*/30 * * * * /home/ubuntu/dev/oos/bin/op-secret-manager.sh init >/dev/null 2>&1"

    # Check if cron job already exists
    if ! crontab -l 2>/dev/null | grep -q "op-secret-manager.sh init"; then
        (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
        echo "Added cron job for connection renewal (every 30 minutes)"
    else
        echo "Cron job already exists"
    fi
}

# Main setup
main() {
    echo "=== OOS 1Password Auto-Connection Setup ==="
    echo ""

    echo "1. Adding to shell profiles..."
    add_to_shell_profile "$HOME/.bashrc"
    add_to_shell_profile "$HOME/.profile"

    echo ""
    echo "2. Creating systemd service..."
    create_systemd_service

    echo ""
    echo "3. Setting up cron job for renewal..."
    create_cron_job

    echo ""
    echo "4. Testing immediate connection..."
    /home/ubuntu/dev/oos/bin/op-secret-manager.sh init

    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Your 1Password connection will now:"
    echo "  • Auto-start on shell login"
    echo "  • Renew every 30 minutes via cron"
    echo "  • Be available through systemd service"
    echo ""
    echo "To use immediately:"
    echo "  source ~/.bashrc"
    echo "  /op-secret status"
    echo "  /op-get your-secret-name"
}

# Show help
show_help() {
    cat << EOF
OOS 1Password Auto-Connection Setup

Sets up automatic 1Password connection that's always available.

Usage: $0 [command]

Commands:
    setup              Run full setup (default)
    shell-only         Only add to shell profiles
    systemd-only       Only create systemd service
    cron-only          Only create cron job
    help               Show this help

What it does:
1. Adds initialization to shell profiles (~/.bashrc, ~/.profile)
2. Creates systemd user service for persistent connection
3. Sets up cron job for connection renewal every 30 minutes
4. Tests immediate connection

After setup:
• Connection auto-starts on login
• Connection persists for 1 hour with auto-renewal
• Available via /op-secret and /op-get slash commands
• No manual authentication required

EOF
}

# Command handling
case "${1:-setup}" in
    setup)
        main
        ;;
    shell-only)
        echo "Adding to shell profiles..."
        add_to_shell_profile "$HOME/.bashrc"
        add_to_shell_profile "$HOME/.profile"
        ;;
    systemd-only)
        echo "Creating systemd service..."
        create_systemd_service
        ;;
    cron-only)
        echo "Setting up cron job..."
        create_cron_job
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