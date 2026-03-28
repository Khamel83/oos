#!/usr/bin/env bash
# OOS One-Click Deployment

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$OOS_ROOT/lib/oos-common.sh" 2>/dev/null || true

subcommand="${1:-help}"
shift || true

case "$subcommand" in
    init)
        platform="${1:-}"
        if [[ -z "$platform" ]]; then
            oos_log_error "Usage: oos deploy init <platform>"
            echo "Platforms: vercel, oci, railway, fly"
            exit 1
        fi

        case "$platform" in
            vercel)
                oos_log_info "Setting up Vercel deployment..."

                # Install Vercel CLI if needed
                if ! command -v vercel &>/dev/null; then
                    oos_log_info "Installing Vercel CLI..."
                    npm install -g vercel
                fi

                # Login
                oos_log_info "Authenticate with Vercel..."
                vercel login

                # Link project
                vercel link

                oos_log_success "Vercel deployment configured"
                echo ""
                echo "Deploy with: oos deploy vercel"
                ;;

            oci)
                oos_log_info "Setting up OCI VM deployment..."

                # Collect VM details
                read -p "VM IP address: " vm_ip
                read -p "SSH user: " ssh_user
                read -p "SSH key path [~/.ssh/oci_key]: " ssh_key
                ssh_key="${ssh_key:-~/.ssh/oci_key}"

                # Save config
                mkdir -p "$OOS_ROOT/.oos/deploy"
                cat > "$OOS_ROOT/.oos/deploy/oci.conf" <<OCIEOF
VM_IP=$vm_ip
SSH_USER=$ssh_user
SSH_KEY=$ssh_key
OCIEOF

                # Test connection
                oos_log_info "Testing SSH connection..."
                if ssh -i "$ssh_key" "$ssh_user@$vm_ip" "echo 'Connection OK'"; then
                    oos_log_success "OCI VM deployment configured"
                    echo ""
                    echo "Deploy with: oos deploy oci"
                else
                    oos_log_error "Could not connect to VM"
                    echo "Check SSH key permissions: chmod 600 $ssh_key"
                    exit 1
                fi
                ;;

            railway|fly)
                oos_log_warning "$platform deployment coming soon"
                echo "Use: vercel or oci for now"
                ;;

            *)
                oos_log_error "Unknown platform: $platform"
                echo "Supported: vercel, oci"
                exit 1
                ;;
        esac
        ;;

    vercel)
        oos_log_info "Deploying to Vercel..."

        if ! command -v vercel &>/dev/null; then
            oos_log_error "Vercel not configured"
            echo "Run: oos deploy init vercel"
            exit 1
        fi

        # Deploy
        vercel --prod "$@"

        oos_log_success "Deployment complete!"
        ;;

    oci)
        oos_log_info "Deploying to OCI VM..."

        # Load config
        if [[ ! -f "$OOS_ROOT/.oos/deploy/oci.conf" ]]; then
            oos_log_error "OCI not configured"
            echo "Run: oos deploy init oci"
            exit 1
        fi

        source "$OOS_ROOT/.oos/deploy/oci.conf"

        # Build and deploy
        oos_log_info "Building application..."

        # Detect project type
        if [[ -f "package.json" ]]; then
            npm run build || true
        elif [[ -f "pyproject.toml" ]]; then
            uv build || true
        fi

        # Transfer files
        oos_log_info "Transferring to VM..."
        rsync -avz -e "ssh -i $SSH_KEY" \
            --exclude node_modules \
            --exclude .venv \
            --exclude .git \
            ./ "$SSH_USER@$VM_IP:~/apps/$(basename $PWD)/"

        # Start service
        oos_log_info "Starting service..."
        ssh -i "$SSH_KEY" "$SSH_USER@$VM_IP" << 'SSHEOF'
cd ~/apps/$(basename $PWD)
# Start with systemd or docker-compose
SSHEOF

        oos_log_success "Deployed to OCI VM!"
        echo "Access at: http://$VM_IP"
        ;;

    logs)
        oos_log_info "Deployment logs..."
        # Show recent deployment logs
        ;;

    help|--help|-h)
        cat << 'EOF'
OOS Deployment

USAGE:
    oos deploy <subcommand>

SUBCOMMANDS:
    init <platform>     Setup deployment for platform
    vercel              Deploy to Vercel
    oci                 Deploy to OCI VM
    logs                Show deployment logs

EXAMPLES:
    # First time setup
    oos deploy init vercel

    # Deploy
    oos deploy vercel

    # OCI VM deployment
    oos deploy init oci
    oos deploy oci

SUPPORTED PLATFORMS:
    vercel              Web apps, serverless functions
    oci                 Full VMs, Docker containers
    railway             (coming soon)
    fly                 (coming soon)
EOF
        ;;

    *)
        oos_log_error "Unknown subcommand: $subcommand"
        echo "Run 'oos deploy help' for usage"
        exit 1
        ;;
esac
