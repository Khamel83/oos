---
description: "Take screenshot and analyze with Claude"
argument-hint: <arguments>
allowed-tools: Bash
model: claude-3-5-sonnet-20241022
---


Take screenshot and analyze with Claude

```bash
./bin/take-screenshot.sh "$ARGUMENTS"
```

Features:
- Cross-platform screenshot capture (Linux, macOS, Windows)
- Automatic Claude analysis of screen content
- UI/UX feedback and improvement suggestions
- Bug identification and documentation
- Design review and accessibility checking

Perfect for getting AI feedback on your current work, debugging UI issues, or documenting user workflows.

Usage examples:
- `./bin/take-screenshot.sh` - Take and analyze screenshot
- `./bin/take-screenshot.sh --analyze-only` - Analyze existing screenshot