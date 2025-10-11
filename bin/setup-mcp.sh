#!/bin/bash
# Complete MCP setup and validation for OOS
set -euo pipefail

PROJECT_NAME="${1:-$(basename "$(pwd)")}"
CONFIG_DIR=".claude"
CONFIG_FILE="$CONFIG_DIR/mcp_servers.json"

echo "🔧 Setting up MCP for project: $PROJECT_NAME"

# 1. Fix server name issues
if [[ -f "$CONFIG_FILE" ]]; then
    echo "📝 Fixing server name..."
    sed -i 's/"oos-context-engineering"/"oos"/g' "$CONFIG_FILE"
    sed -i 's/"my-project-server"/"my-project"/g' "$CONFIG_FILE"
fi

# 2. Create proper configuration if missing
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "📝 Creating MCP configuration..."
    mkdir -p "$CONFIG_DIR"

    # Detect Python environment
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    VENV_PATH="venv/lib/python${PYTHON_VERSION}/site-packages"

    if [[ ! -d "$VENV_PATH" ]]; then
        VENV_PATH="venv/lib/python3.12/site-packages"
    fi

    cat > "$CONFIG_FILE" << EOF
{
  "${PROJECT_NAME}": {
    "command": "python3",
    "args": ["mcp_server.py"],
    "cwd": "$(pwd)",
    "env": {
      "PYTHONPATH": "$(pwd)/src:$VENV_PATH"
    }
  }
}
EOF
fi

# 3. Validate configuration
echo "🔍 Validating MCP configuration..."
python3 -c "import json; json.load(open('$CONFIG_FILE'))" || {
    echo "❌ Invalid JSON in MCP configuration"
    exit 1
}

# 4. Convert slash commands to markdown format
echo "🔄 Converting slash commands to markdown..."
if [[ -f ".claude/slash_commands.json" ]]; then
    ./bin/convert-slash-commands.sh
else
    echo "✅ No JSON commands to convert"
fi

# 5. Check MCP server file
if [[ ! -f "mcp_server.py" ]]; then
    echo "⚠️  Warning: mcp_server.py not found"
fi

# 6. Test with Claude CLI
if command -v claude &> /dev/null; then
    echo "🔗 Testing MCP connection..."
    if claude mcp list | grep -q "$PROJECT_NAME"; then
        echo "✅ MCP server '$PROJECT_NAME' is connected"
    else
        echo "🔗 Adding MCP server to Claude..."
        claude mcp add "$PROJECT_NAME" python3 mcp_server.py --cwd "$(pwd)" || {
            echo "❌ Failed to add MCP server"
            echo "Manual command: claude mcp add $PROJECT_NAME python3 mcp_server.py"
        }
    fi
else
    echo "⚠️  Claude CLI not found - skipping connection test"
fi

# 7. Validate slash commands
echo "🔍 Validating slash commands..."
critical_commands=("help-me" "validate" "start-coding" "screenshot")
missing_commands=()

for cmd in "${critical_commands[@]}"; do
    if [[ ! -f ".claude/commands/${cmd}.md" ]]; then
        missing_commands+=("$cmd")
    fi
done

if [[ ${#missing_commands[@]} -gt 0 ]]; then
    echo "⚠️  Missing commands: ${missing_commands[*]}"
else
    echo "✅ All critical slash commands present"
fi

echo "✅ MCP and slash commands setup complete"
echo "💡 Restart Claude Code to see all changes"