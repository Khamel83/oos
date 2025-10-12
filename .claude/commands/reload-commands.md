---
description: "Reload Claude Code slash commands from .claude/commands/ directory"
allowed-tools: Bash
model: claude-3-5-sonnet-20241022
---


Reload Claude Code slash commands

```bash
echo "🔄 Reloading slash commands..."
echo "📁 Commands directory: $(ls -la .claude/commands/ | wc -l) files"
echo "📋 Available commands:"
ls .claude/commands/*.md 2>/dev/null | head -10 | while read cmd; do
    basename "$(basename "$cmd" .md)"
done
echo ""
echo "✅ Commands should be available after restarting Claude Code"
echo "💡 If commands still don't appear, try:"
echo "   1. Restart Claude Code completely"
echo "   2. Check .claude/commands/ directory permissions"
echo "   3. Verify YAML frontmatter format"
```

This command helps diagnose and reload slash command issues.