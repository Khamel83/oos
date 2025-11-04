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
mkdir -p .claude/commands

# Download only the 11 perfect OOS commands
commands=(
    "dev.md"
    "test.md"
    "fix.md"
    "think.md"
    "workflow.md"
    "project.md"
    "op.md"
    "archon.md"
    "task.md"
    "check.md"
    "help.md"
)

for cmd in "${commands[@]}"; do
    echo "  📥 Installing /$cmd"
    curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/.claude/commands/$cmd" > .claude/commands/"$cmd"
done

# Only the 11 perfect commands are installed - no additional inline commands

echo "✅ All Claude Code commands installed in project"

# Download essential scripts
echo "🔧 Installing OOS tools..."
scripts=(
    "oos-module-runner.sh"
    "oos-template-manager.sh"
    "oos-update-from-github.sh"
    "claude-start-coding.sh"
    "claude-dev.sh"
    "claude-help.sh"
    "claude-think.sh"
    "claude-workflow.sh"
    "claude-project.sh"
    "claude-fix.sh"
    "claude-test.sh"
    "claude-op.sh"
    "claude-archon.sh"
    "claude-task.sh"
    "claude-check.sh"
    "setup-1password-service.sh"
    "setup-archon.sh"
    "dev-gate.sh"
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

# If this IS the OOS repo (has pyproject.toml), install Python dependencies
if [[ -f "pyproject.toml" ]] && grep -q "name = \"oos\"" pyproject.toml 2>/dev/null; then
    echo ""
    echo "📦 Installing Python dependencies..."
    if command -v uv &> /dev/null; then
        if uv sync; then
            echo "✅ Python dependencies installed"
        else
            echo "⚠️  Failed to install Python dependencies - run: uv sync"
        fi
    else
        echo "⚠️  uv not found - install from: https://github.com/astral-sh/uv"
        echo "   Or run: curl -LsSf https://astral.sh/uv/install.sh | sh"
    fi
fi

echo -e "\033[1;32m✅ OOS Installation Complete!\033[0m"
echo ""
echo "🚀 Your 11 perfect commands are ready:"
echo ""
echo "  /dev setup              # Start development session"
echo "  /dev check              # Validate environment"
echo "  /test scenarios         # Run user testing"
echo "  /fix auto               # Fix code issues"
echo "  /think clarify          # AI problem solving"
echo "  /workflow complete      # Complete workflows"
echo "  /project create [name]  # Create projects"
echo "  /op status              # 1Password status"
echo "  /archon research [topic] # Search knowledge base"
echo "  /task start             # Start working on tasks"
echo "  /help                   # Get help with commands"
echo ""
echo "🎯 That's it! 11 commands for everything you need."
echo "🔄 Restart Claude Code to use all slash commands!"