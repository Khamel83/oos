#!/usr/bin/env bash
set -euo pipefail

# The "Just Works" Security System
# For people who 1Password failed them

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $*${NC}"; }
info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
header() { echo -e "${BOLD}$*${NC}"; }

install_just_works_security() {
    header "🔐 Installing 'Just Works' Security System"
    echo "This system actually works - no complex interfaces, no CLI failures"
    echo

    # Step 1: Ensure Python and dotenv are available
    if command -v python3 >/dev/null 2>&1; then
        success "Python 3 found"

        # Install python-dotenv if not present
        if ! python3 -c "import dotenv" 2>/dev/null; then
            info "Installing python-dotenv..."
            pip3 install python-dotenv
            success "python-dotenv installed"
        else
            success "python-dotenv already available"
        fi
    else
        error "Python 3 is required but not found"
        exit 1
    fi

    # Step 2: Set up .env file if it doesn't exist
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        info "Creating .env file..."
        cat > "$PROJECT_ROOT/.env" << 'EOF'
# OOS Environment Configuration
# Add your API keys here - NEVER commit this file

# AI Service Keys
OPENROUTER_API_KEY=""
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""

# Project Configuration
PROJECT_NAME=""
PROJECT_DESCRIPTION=""
EOF
        success "Created .env file"
        warn "Please add your API keys to the .env file"
    else
        success ".env file already exists"
    fi

    # Step 3: Ensure .env is in .gitignore
    if ! grep -q "^\.env$" "$PROJECT_ROOT/.gitignore" 2>/dev/null; then
        info "Adding .env to .gitignore..."
        echo ".env" >> "$PROJECT_ROOT/.gitignore"
        success ".env added to .gitignore"
    else
        success ".env already in .gitignore"
    fi

    # Step 4: Install simple pre-commit hook
    info "Setting up simple security validation..."
    cat > "$PROJECT_ROOT/bin/simple-secret-check.sh" << 'EOF'
#!/bin/bash
# Simple secret checker - no complex dependencies

# Check for common API key patterns
SECRETS_FOUND=false

# OpenRouter API keys
if grep -r "sk-or-v1-[a-f0-9]{48}" . --exclude-dir=.git --exclude-dir=venv --exclude-dir=.oos 2>/dev/null; then
    echo "❌ Found potential OpenRouter API key!"
    SECRETS_FOUND=true
fi

# OpenAI API keys
if grep -r "sk-[A-Za-z0-9]{48}" . --exclude-dir=.git --exclude-dir=venv --exclude-dir=.oos 2>/dev/null; then
    echo "❌ Found potential OpenAI API key!"
    SECRETS_FOUND=true
fi

# Generic API keys
if grep -r -i "api[_-]?key[\"'][^\"']*[A-Za-z0-9]{20,}[\"']" . --exclude-dir=.git --exclude-dir=venv --exclude-dir=.oos 2>/dev/null; then
    echo "❌ Found potential API key!"
    SECRETS_FOUND=true
fi

if $SECRETS_FOUND; then
    echo ""
    echo "🚨 SECRETS DETECTED - Commit blocked"
    echo "Please remove the secrets from your files"
    exit 1
else
    echo "✅ No secrets detected - commit allowed"
fi
EOF
    chmod +x "$PROJECT_ROOT/bin/simple-secret-check.sh"

    # Create pre-commit hook
    cat > "$PROJECT_ROOT/.git/hooks/pre-commit" << 'EOF'
#!/bin/bash
echo "🔒 Running security check..."
./bin/simple-secret-check.sh
EOF
    chmod +x "$PROJECT_ROOT/.git/hooks/pre-commit"

    success "Pre-commit security hook installed"

    # Step 5: Create universal secrets access tool
    cat > "$PROJECT_ROOT/bin/access-secrets.sh" << 'EOF'
#!/bin/bash
# Universal secrets access tool

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source_env() {
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
        echo "✅ Environment variables loaded from .env"
    else
        echo "❌ .env file not found"
        exit 1
    fi
}

get_secret() {
    local key_name="$1"
    source_env
    echo "${!key_name}"
}

list_secrets() {
    source_env
    echo "Available secrets in .env:"
    grep "=" "$PROJECT_ROOT/.env" | cut -d'=' -f1 | grep -v "^#"
}

test_access() {
    local key_name="$1"
    local key_value=$(get_secret "$key_name")
    if [[ -n "$key_value" ]]; then
        echo "✅ $key_name: ${key_value:0:10}... (${#key_value} chars)"
        return 0
    else
        echo "❌ $key_name: Not found or empty"
        return 1
    fi
}

case "${1:-help}" in
    "source")
        source_env
        ;;
    "get")
        if [[ -n "${2:-}" ]]; then
            get_secret "$2"
        else
            echo "Usage: $0 get <key_name>"
            exit 1
        fi
        ;;
    "list")
        list_secrets
        ;;
    "test")
        if [[ -n "${2:-}" ]]; then
            test_access "$2"
        else
            echo "Testing all secrets..."
            source_env
            grep "=" "$PROJECT_ROOT/.env" | cut -d'=' -f1 | while read -r key; do
                test_access "$key"
            done
        fi
        ;;
    "help"|"-h"|"--help"|*)
        cat << 'EOF'
Universal Secrets Access Tool

Usage: access-secrets.sh <command> [options]

Commands:
  source              Load environment variables
  get <key>          Get value of a specific key
  list               List all available keys
  test [key]         Test if secrets are accessible
  help               Show this help

Examples:
  ./bin/access-secrets.sh get OPENROUTER_API_KEY
  ./bin/access-secrets.sh test
  ./bin/access-secrets.sh list

This tool provides simple, non-interactive access to your secrets.
EOF
        ;;
esac
EOF

    chmod +x "$PROJECT_ROOT/bin/access-secrets.sh"

    success "Universal secrets access tool created"

    echo
    header "🎉 'Just Works' Security System Installed!"
    echo
    echo "📝 What you need to do:"
    echo "1. Add your API keys to the .env file:"
    echo "   nano .env"
    echo
    echo "2. Test the system:"
    echo "   ./bin/access-secrets.sh test"
    echo
    echo "3. Your applications can now access secrets with:"
    echo "   source bin/access-secrets.sh source"
    echo "   ./bin/access-secrets.sh get OPENROUTER_API_KEY"
    echo
    echo "🔒 Security features:"
    echo "• Pre-commit hooks block secret commits"
    echo "• .env file is gitignored"
    echo "• Simple, reliable, no complex interfaces"
    echo "• Works with any AI agent or application"
    echo
    success "Installation complete! Your security system is ready."
}

# Run the installation
install_just_works_security