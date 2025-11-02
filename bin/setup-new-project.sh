#!/usr/bin/env bash
set -euo pipefail

# Copy secrets to a new project (no more copy-paste errors)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $*${NC}"; }
info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
error() { echo -e "${RED}❌ $*${NC}"; }
header() { echo -e "${BOLD}$*${NC}"; }

copy_secrets_to_project() {
    local target_dir="$1"

    header "📁 Setting up secrets for new project: $target_dir"

    # Check if source .env exists
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        error "Source .env file not found in $PROJECT_ROOT"
        info "Run the main setup first:"
        echo "  ./bin/setup-just-works-security.sh"
        exit 1
    fi

    # Create target directory if it doesn't exist
    mkdir -p "$target_dir"

    # Check if target already has .env
    if [[ -f "$target_dir/.env" ]]; then
        warn "Target already has .env file"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Cancelled setup"
            exit 0
        fi
    fi

    # Check for .env.example in target to know what keys to copy
    local keys_to_copy=()
    if [[ -f "$target_dir/.env.example" ]]; then
        info "Found .env.example, copying only required keys..."
        while IFS= read -r line; do
            if [[ -n "$line" && ! "$line" =~ ^# ]]; then
                local key=$(echo "$line" | cut -d'=' -f1)
                keys_to_copy+=("$key")
            fi
        done < "$target_dir/.env.example"
    else
        # Copy all keys if no .env.example
        info "No .env.example found, copying all keys..."
        while IFS= read -r line; do
            if [[ -n "$line" && ! "$line" =~ ^# ]]; then
                local key=$(echo "$line" | cut -d'=' -f1)
                keys_to_copy+=("$key")
            fi
        done < "$PROJECT_ROOT/.env"
    fi

    # Create target .env file
    {
        echo "# Environment variables for new project"
        echo "# Generated from master secrets: $(date)"
        echo "# Source: $PROJECT_ROOT/.env"
        echo ""

        # Copy each key value
        for key in "${keys_to_copy[@]}"; do
            local value=$(grep "^${key}=" "$PROJECT_ROOT/.env" | cut -d'=' -f2-)
            echo "${key}=${value}"
        done

        echo ""
        echo "# Local project settings"
        echo "PROJECT_NAME=\"$(basename "$target_dir")\""
        echo "PROJECT_ROOT=\"$target_dir\""

    } > "$target_dir/.env"

    # Create .gitignore if it doesn't exist
    if [[ ! -f "$target_dir/.gitignore" ]]; then
        echo ".env" > "$target_dir/.gitignore"
        success "Created .gitignore in target project"
    else
        if ! grep -q "^\.env$" "$target_dir/.gitignore"; then
            echo ".env" >> "$target_dir/.gitignore"
            success "Added .env to target .gitignore"
        fi
    fi

    # Copy access tool to target project
    cp "$PROJECT_ROOT/bin/access-secrets.sh" "$target_dir/bin/" 2>/dev/null || mkdir -p "$target_dir/bin" && cp "$PROJECT_ROOT/bin/access-secrets.sh" "$target_dir/bin/"
    chmod +x "$target_dir/bin/access-secrets.sh"

    success "Secrets copied to $target_dir"
    echo
    info "Next steps for your new project:"
    echo "1. cd $target_dir"
    echo "2. ./bin/access-secrets.sh test"
    echo "3. Use environment variables in your code"
}

# Main execution
case "${1:-help}" in
    "help"|"-h"|"--help"|"")
        cat << 'EOF'
New Project Secrets Setup

Usage: setup-new-project.sh <target_directory>

This script copies your master secrets to a new project without
any manual copy-paste operations.

Example:
  ./bin/setup-new-project.sh ~/projects/my-new-app
  ./bin/setup-new-project.sh ./my-project

Features:
• No manual copy-paste (prevents exposure errors)
• Only copies required keys (from .env.example)
• Creates proper .gitignore automatically
• Copies access-secrets tool for easy access
• Safe and reversible

Requirements:
• Run after setup-just-works-security.sh
• Have your master .env configured

EOF
        ;;
    *)
        if [[ -n "$1" ]]; then
            copy_secrets_to_project "$1"
        else
            error "Target directory required"
            echo "Usage: $0 <target_directory>"
            exit 1
        fi
        ;;
esac