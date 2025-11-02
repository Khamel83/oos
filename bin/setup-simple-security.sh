#!/bin/bash
set -euo pipefail

# Simple Security Setup - No Complex Interfaces
# This actually works when 1Password fails

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $*${NC}"; }
info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
header() { echo -e "${BOLD}$*${NC}"; }

install_simple_security() {
    header "🔐 Installing Simple Security System"
    echo "This actually works - no 1Password headaches"
    echo

    # Step 1: Create .env file
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

    # Step 2: Ensure .env is in .gitignore
    if ! grep -q "^\.env$" "$PROJECT_ROOT/.gitignore" 2>/dev/null; then
        info "Adding .env to .gitignore..."
        echo ".env" >> "$PROJECT_ROOT/.gitignore"
        success ".env added to .gitignore"
    else
        success ".env already in .gitignore"
    fi

    # Step 3: Install python-dotenv if not present
    if ! python3 -c "import dotenv" 2>/dev/null; then
        if command -v uv >/dev/null 2>&1; then
            info "Installing python-dotenv with uv..."
            uv add python-dotenv
        else
            pip3 install python-dotenv --break-system-packages
        fi
        success "python-dotenv installed"
    else
        success "python-dotenv already available"
    fi

    # Step 4: Create AI secrets client
    if [[ ! -f "$PROJECT_ROOT/bin/get-secrets.py" ]]; then
        info "Creating AI secrets client..."
        cat > "$PROJECT_ROOT/bin/get-secrets.py" << 'PYTHON_EOF'
#!/usr/bin/env python3
"""
Simple AI Secrets Client
No complex interfaces - just works
"""

import os
from pathlib import Path
from dotenv import load_dotenv

class SimpleSecrets:
    def __init__(self):
        load_dotenv()  # Load from .env file

    def get(self, key):
        """Get a secret value"""
        value = os.getenv(key)
        if value:
            # Mask for logging
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"🔑 {key}: {masked}")
            return value
        else:
            print(f"❌ Secret not found: {key}")
            return None

    def list_all(self):
        """List all available secrets"""
        print("🔑 Available secrets:")
        for key, value in os.environ.items():
            if any(secret_type in key.upper() for secret_type in ['API', 'KEY', 'SECRET', 'TOKEN']):
                masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                print(f"  • {key}: {masked}")

if __name__ == "__main__":
    import sys
    secrets = SimpleSecrets()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "get" and len(sys.argv) > 2:
            value = secrets.get(sys.argv[2])
            if value:
                print(value)
        elif command == "list":
            secrets.list_all()
        else:
            print("Usage: python get-secrets.py <get|list> [key]")
    else:
        print("Simple AI Secrets Client")
        print("Usage: python get-secrets.py <command>")
        print("Commands:")
        print("  get <key>    Get a secret value")
        print("  list         List all secrets")
PYTHON_EOF
        chmod +x "$PROJECT_ROOT/bin/get-secrets.py"
        success "Created AI secrets client"
    else
        success "AI secrets client already exists"
    fi

    echo
    header "🎉 Simple Security System Ready!"
    echo
    echo "📝 What to do next:"
    echo "1. Add your API keys to .env:"
    echo "   nano .env"
    echo
    echo "2. Test it works:"
    echo "   python bin/get-secrets.py list"
    echo "   python bin/get-secrets.py get OPENROUTER_API_KEY"
    echo
    echo "3. Your AI agents can now access secrets with:"
    echo "   import sys"
    echo "   sys.path.append('bin')"
    echo "   from get_secrets import SimpleSecrets"
    echo "   secrets = SimpleSecrets()"
    echo "   api_key = secrets.get('OPENROUTER_API_KEY')"
    echo
    success "Setup complete! No more 1Password headaches."
}

# Run installation
install_simple_security

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    install_simple_security
fi