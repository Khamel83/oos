#!/bin/bash
# Simple OOS Integration - Just copy the working files out
# 5 lines that actually work instead of 500 lines of overcomplicated BS

set -e

echo "🔧 Simple OOS Integration - Copy files out and be done"

# Step 1: Update OOS folder (if we're in parent project)
PARENT_DIR="$(dirname "$(pwd)")"
if [ "$(basename "$(pwd)")" = "oos" ] && [ -d "$PARENT_DIR/.git" ]; then
    echo "📁 In OOS subdirectory - updating and copying out..."

    # Update OOS
    git pull origin master

    # Copy slash commands out of OOS to parent
    mkdir -p "../.claude"
    cp .claude/slash_commands.json ../.claude/

    # Copy scripts out of OOS to parent
    mkdir -p "../bin"
    cp bin/claude-*.sh ../bin/ 2>/dev/null || true
    cp bin/oos-v1.2.sh ../bin/ 2>/dev/null || true
    cp bin/task_runner.sh ../bin/ 2>/dev/null || true
    cp bin/simple_*.sh ../bin/ 2>/dev/null || true

    # Make scripts executable
    chmod +x ../bin/claude-*.sh ../bin/ 2>/dev/null || true
    chmod +x ../bin/oos-v1.2.sh ../bin/ 2>/dev/null || true
    chmod +x ../bin/task_runner.sh ../bin/ 2>/dev/null || true
    chmod +x ../bin/simple_*.sh ../bin/ 2>/dev/null || true

    # Copy v1.2 task definitions
    mkdir -p "../.oos"
    cp .oos/tasks.json ../.oos/ 2>/dev/null || true

    echo "✅ Done! /consultant should work after Claude Code restart"
    echo "🚀 OOS v1.2 features now available: ./bin/oos-v1.2.sh"

else
    echo "ℹ️  Not in OOS subdirectory - nothing to copy out"
fi