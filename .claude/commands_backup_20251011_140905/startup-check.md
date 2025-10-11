---
description: "Startup health check and command refresh - runs automatically to ensure OOS is ready"
tools: ["Bash"]
---

OOS Startup Health Check - ensures slash commands are fresh and working

```bash
echo "🚀 OOS Startup Health Check"
echo "=========================="

# Check if we need to refresh commands
if [[ ! -f ".claude/commands_version.json" ]] || \
   [[ "$(git -C "$OOS_ROOT" rev-parse --short HEAD 2>/dev/null)" != "$(jq -r '.oos_version // "unknown"' .claude/commands_version.json 2>/dev/null)" ]]; then

    echo "📥 Detected OOS update or new installation"
    echo "🔄 Refreshing slash commands..."

    if ./bin/oos-refresh-commands.sh; then
        echo "✅ Commands refreshed successfully"

        # Show key commands that are ready
        echo ""
        echo "🎯 Ready to use:"
        for cmd in complete-workflow validate ruat provision screenshot oos-refresh; do
            if [[ -f ".claude/commands/$cmd.md" ]]; then
                echo "  • /$cmd"
            fi
        done

    else
        echo "❌ Command refresh failed"
        echo "🔧 Try manual refresh: /oos-refresh"
    fi
else
    echo "✅ OOS commands are up to date"

    # Quick validation
    if ./bin/oos-refresh-commands.sh --test-only; then
        echo "✅ All commands validated"
    else
        echo "⚠️  Commands need validation - run /oos-refresh"
    fi
fi

echo ""
echo "💡 Run /oos-refresh to manually update commands"
echo "📋 Status: .claude/commands_version.json"
echo "🧪 Tests: .claude/commands_test.log"
```

This startup check ensures:
- Commands are always current with OOS version
- Any fuckups are detected immediately
- Validation passes before commands are used
- Clear feedback on command status

Run this manually or set it as your startup command to ensure OOS is always ready.