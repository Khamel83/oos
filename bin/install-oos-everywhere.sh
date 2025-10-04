#!/usr/bin/env bash
set -euo pipefail

# OOS Universal Installer - One command to rule them all
# Usage: curl -s https://raw.githubusercontent.com/Khamel83/oos/main/bin/install-oos-everywhere.sh | bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_header() { echo -e "${BOLD}$1${NC}"; }

# Check if we're in a project directory
if [[ ! -d ".git" ]] && [[ "${1:-}" != "--force" ]]; then
    log_error "Not a git repository. Use --force to install anyway."
    exit 1
fi

# Check if we're in OOS repo itself
CURRENT_DIR="$(pwd)"
OOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
if [[ "$CURRENT_DIR" == "$OOS_ROOT" ]]; then
    log_error "You're in the OOS repository itself. Use this script in other projects."
    exit 1
fi

log_header "🚀 Installing OOS Development System"
echo "========================================"

# 1. Copy OOS files
log_info "Step 1: Copying OOS development scripts..."
if [[ -d "bin" ]]; then
    log_info "Existing bin/ directory found - backing up..."
    mv bin bin.backup.$(date +%Y%m%d_%H%M%S)
fi

cp -r "$PROJECT_ROOT/bin" .
cp -r "$PROJECT_ROOT/.claude" .

# Make scripts executable
chmod +x bin/*.sh

log_success "OOS scripts copied and made executable"

# 2. Configure Claude Code settings
log_info "Step 2: Configuring Claude Code settings..."

# Create settings directory
mkdir -p ~/.claude

# Create or update settings with OOS commands
cat > ~/.claude/settings.json << 'EOF'
{
  "mcpServers": {
    "archon": {
      "command": "npx",
      "args": ["-y", "@archon-ai/mcp-server@latest"]
    }
  },
  "slashCommands": {
    "start-coding": {
      "description": "🚀 One-command setup: validate environment and get ready to code",
      "script": "./bin/claude-start-coding.sh"
    },
    "dev-gate": {
      "description": "🚪 Mandatory development environment gate - ensures proper setup before coding",
      "script": "./bin/claude-dev-gate.sh"
    },
    "dev-python": {
      "description": "🐍 Run Python with mandatory environment validation",
      "script": "./bin/claude-dev-python.sh"
    },
    "dev-test": {
      "description": "🧪 Run tests with mandatory environment validation",
      "script": "./bin/claude-dev-test.sh"
    },
    "dev-uv": {
      "description": "📦 Run uv commands with mandatory environment validation",
      "script": "./bin/claude-dev-uv.sh"
    },
    "update-oos": {
      "description": "🔄 Update existing project with latest OOS development gate system",
      "script": "./bin/claude-update-oos.sh"
    }
  }
}
EOF

log_success "Claude Code settings configured"

# 3. Install git hooks (if git repo)
if [[ -d ".git" ]]; then
    log_info "Step 3: Installing development gate git hooks..."
    ./bin/install-mandatory-hooks.sh
    log_success "Git hooks installed"
fi

# 4. Install shell guards
log_info "Step 4: Installing command interceptors..."
./bin/install-shell-guards.sh
log_success "Command interceptors installed"

echo
log_header "🎉 OOS Installation Complete!"
echo "=================================="
echo
log_info "Available Commands:"
echo "  /start-coding     - One command to validate everything and start coding"
echo "  /dev-gate         - Environment validation and management"
echo "  /dev-python       - Protected Python execution"
echo "  /dev-test         - Protected test execution"
echo "  /dev-uv           - Protected uv commands"
echo "  /update-oos       - Update this project with latest OOS"
echo
log_info "Direct Script Usage:"
echo "  ./bin/claude-start-coding.sh"
echo "  ./bin/dev-gate.sh"
echo
log_warning "IMPORTANT: Restart Claude Code to load slash commands"
echo
log_success "Your project now has bulletproof development environment enforcement!"
echo
log_info "To get started:"
echo "  1. Restart Claude Code (exit with ctrl+c, run cc again)"
echo "  2. Run: /start-coding"
echo "  3. Start coding with confidence!"