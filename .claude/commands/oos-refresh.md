---
description: "Auto-refresh OOS slash commands and validate functionality"
allowed-tools: Bash
model: claude-3-5-sonnet-20241022
---


Auto-refresh OOS slash commands from latest version and validate they work correctly.

```bash
# Run the OOS refresh system
./bin/oos-refresh-commands.sh

# Show results
if [[ $? -eq 0 ]]; then
    echo "✅ OOS commands refreshed and validated"
    echo "💡 Commands ready for use"
else
    echo "❌ OOS command refresh failed"
    echo "🚨 Check .claude/commands_test.log for details"
fi
```

This command automatically:
1. Checks if slash commands are up to date with OOS version
2. Updates commands if needed
3. Validates all commands work correctly
4. Shows what changed
5. Maintains backups of previous working versions
6. Detects and reports any fuckups in the update process

Run this after updating OOS or if slash commands aren't working properly.

Version tracking info stored in: `.claude/commands_version.json`
Test results saved in: `.claude/commands_test.log`