#!/usr/bin/env bash
# Simple OOS Installer - Works from anywhere

set -euo pipefail

INSTALL_DIR="${1:-$(pwd)}"
PROJECT_NAME="$(basename "$INSTALL_DIR")"

echo -e "\033[1;34m🚀 Installing OOS into $PROJECT_NAME\033[0m"
echo "=================================="

cd "$INSTALL_DIR"
mkdir -p .claude bin

# Download working slash commands
echo "📋 Installing slash commands..."
curl -s https://raw.githubusercontent.com/Khamel83/oos/master/.claude/project_commands.json > .claude/slash_commands.json
echo "✅ Slash commands installed"

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

# Download modules
echo "🧩 Installing key modules..."
mkdir -p modules/{security,testing,python}

# Security modules
for module in scan_secrets.sh check_permissions.sh; do
    curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/security/$module" > "modules/security/$module"
    chmod +x "modules/security/$module"
done

# Testing modules
for module in lint_code.sh run_pytest.sh; do
    curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/testing/$module" > "modules/testing/$module"
    chmod +x "modules/testing/$module"
done

# Python modules
curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/modules/python/check_uv.sh" > "modules/python/check_uv.sh"
chmod +x "modules/python/check_uv.sh"

# Download compositions
echo "🏗️ Installing compositions..."
mkdir -p compositions

for comp in full-dev-setup.sh pre-commit.sh; do
    curl -s "https://raw.githubusercontent.com/Khamel83/oos/master/compositions/$comp" > "compositions/$comp"
    chmod +x "compositions/$comp"
done

# Create .gitignore
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# OOS (Open Operating System)
modules/
compositions/
bin/oos-*.sh
