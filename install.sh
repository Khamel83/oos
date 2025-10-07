#!/usr/bin/env bash
# OOS Installer - Run from any project
# URL: https://raw.githubusercontent.com/Khamel83/oos/master/install.sh

set -euo pipefail

INSTALL_DIR="${1:-$(pwd)}"
PROJECT_NAME="$(basename "$INSTALL_DIR")"

echo -e "\033[1;34m🚀 Installing OOS into $PROJECT_NAME\033[0m"
echo "=================================="

cd "$INSTALL_DIR"
mkdir -p .claude bin modules compositions

# Install Claude Code commands (new Markdown format)
echo "📋 Installing Claude Code commands..."
mkdir -p ~/.claude/commands

# Create global start-coding command
cat > ~/.claude/commands/start-coding.md << 'EOF'
---
description: 🚀 Complete development session setup
argument-hint: [optional project context]
allowed-tools: Bash(*)
---

Run the complete development session setup script to validate environment and prepare for coding.

Please run the start-coding script from the project's bin directory:

```bash
./bin/claude-start-coding.sh
```

This will:
- Update OOS subfolder operating system
- Validate development environment
- Check project health
- Set up development commands
- Show available tools and tips
EOF

echo "✅ Claude Code commands installed globally"

# Download essential scripts
echo "🔧 Installing OOS tools..."
scripts=(
    "oos-module-runner.sh"
    "oos-template-manager.sh"
    "oos-update-from-github.sh"
    "claude-start-coding.sh"
)

for script in "${scripts[@]}"; do
    echo "  📥 $script"
    curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/bin/$script" > "bin/$script"
    chmod +x "bin/$script"
done

# Download key modules
echo "🧩 Installing modules..."
mkdir -p modules/{security,testing,python,git,ai}

# Security
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/security/scan_secrets.sh" > "modules/security/scan_secrets.sh"
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/security/check_permissions.sh" > "modules/security/check_permissions.sh"
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/security/check_1password.sh" > "modules/security/check_1password.sh"
chmod +x modules/security/*.sh

# Testing
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/testing/lint_code.sh" > "modules/testing/lint_code.sh"
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/testing/run_pytest.sh" > "modules/testing/run_pytest.sh"
chmod +x modules/testing/*.sh

# Python
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/python/check_uv.sh" > "modules/python/check_uv.sh"
chmod +x modules/python/*.sh

# Git
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/git/check_status.sh" > "modules/git/check_status.sh"
chmod +x modules/git/*.sh

# AI
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/ai/generate_commit.sh" > "modules/ai/generate_commit.sh"
chmod +x modules/ai/*.sh

# Download compositions
echo "🏗️ Installing compositions..."
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/compositions/full-dev-setup.sh" > "compositions/full-dev-setup.sh"
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/compositions/pre-commit.sh" > "compositions/pre-commit.sh"
chmod +x compositions/*.sh

# Create .gitignore
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# OOS (Open Operating System) - copied from OOS repo
modules/
compositions/
bin/oos-*.sh
bin/dev-gate.sh
bin/claude-*.sh
EOF

echo -e "\033[1;32m✅ OOS Installation Complete!\033[0m"
echo ""
echo "Available commands in Claude Code:"
echo "  /start-coding  - Complete development session setup (installed globally)"
echo ""
echo "To access other OOS tools, run ./bin/claude-start-coding.sh or use the modules directly."
echo ""
echo "🔄 Restart Claude Code to use the /start-coding command!"