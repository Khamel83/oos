# OOS Slash Commands - Complete Guide

## Overview

OOS provides comprehensive slash commands for systematic project development. This guide explains how they work, how to troubleshoot them, and how to ensure they're available in all projects.

## Command Types

### 1. JSON-based Commands (Legacy)
- Location: `.claude/slash_commands.json`
- Format: JSON with name, description, and script fields
- Status: Being phased out in favor of markdown commands

### 2. Markdown Commands (Current)
- Location: `.claude/commands/*.md`
- Format: YAML frontmatter with description and tools
- Example:
```markdown
---
description: "Run comprehensive OOS validation"
tools: ["Bash"]
---

Run comprehensive OOS validation

```bash
./bin/validate-oos "$ARGUMENTS"
```
```

## Core Workflow Commands

### Complete Workflow System
- `/complete-workflow` - Run complete A→B→C→D workflow
- `/idea-to-done` - Alias for complete workflow
- `/validate` - Comprehensive OOS validation
- `/ruat` - User acceptance testing
- `/test-user-scenarios` - Full RUAT command
- `/provision` - Infrastructure provisioning
- `/screenshot` - Screen analysis

### Development Commands
- `/start-coding` - Complete development session setup
- `/dev-setup` - Environment validation
- `/pre-commit` - Pre-commit validation
- `/modules` - Module management

## Installation & Validation

### Automatic Installation
When you run `./bin/oos-install-into-project.sh`, it:
1. Copies markdown commands to `.claude/commands/`
2. Validates command installation
3. Shows which key commands are available

### Manual Validation
```bash
# Check if commands exist
ls .claude/commands/*.md | wc -l

# Test specific commands
ls .claude/commands/complete-workflow.md
ls .claude/commands/validate.md
ls .claude/commands/ruat.md
```

## Troubleshooting

### Commands Don't Appear After Installation

**Symptoms**: `/complete-workflow` or other commands return "Unknown slash command"

**Solutions**:

1. **Restart Claude Code**
   - Completely exit and restart Claude Code
   - This is the most common fix

2. **Check File Permissions**
   ```bash
   ls -la .claude/commands/
   # Should show readable .md files
   ```

3. **Validate YAML Format**
   ```bash
   # Check first few lines of command file
   head -5 .claude/commands/complete-workflow.md
   # Should show proper YAML frontmatter
   ```

4. **Use Reload Command**
   ```bash
   /reload-commands
   ```
   This shows diagnostic information and command count.

5. **Verify Installation**
   ```bash
   # Re-run installation to validate
   ./bin/oos-install-into-project.sh
   ```

### Commands Still Don't Work

If commands still don't appear after trying the above:

1. **Check for Duplicate Configurations**
   ```bash
   # Look for conflicting config files
   find .claude -name "*.json" -o -name "*.yml" -o -name "*.yaml"
   ```

2. **Test with Simple Command**
   ```bash
   # Try the test command
   /test-debug
   ```

3. **Check Claude Code Version**
   - Ensure you're using a recent Claude Code version
   - Some older versions have different slash command behavior

## Architecture

### How Slash Commands Work

1. **Discovery**: Claude Code scans `.claude/commands/*.md` files
2. **Parsing**: Reads YAML frontmatter for description and tools
3. **Execution**: Runs the code block when command is invoked
4. **Arguments**: Passes arguments via `$ARGUMENTS` variable

### Command Structure

```markdown
---
description: "Brief description of what the command does"
tools: ["Bash"]  # or other tools
---

Optional explanatory text

```bash
# Command implementation
./bin/script.sh "$ARGUMENTS"
```
```

## Best Practices

### Command Design
1. **Clear Descriptions**: Use concise, actionable descriptions
2. **Consistent Naming**: Use kebab-case for command names
3. **Error Handling**: Include proper error handling in scripts
4. **Help Integration**: Provide help information for complex commands

### Installation Validation
Always validate command installation after setting up new projects:

```bash
# Quick validation
./bin/oos-install-into-project.sh | grep "✅"

# Detailed validation
ls .claude/commands/ | wc -l
```

### Project Integration
- Include slash command validation in project setup
- Test commands work after installation
- Document project-specific commands

## Maintenance

### Updating Commands
1. Update `.claude/commands/*.md` files
2. Restart Claude Code
3. Test updated commands

### Adding New Commands
1. Create new `.md` file in `.claude/commands/`
2. Follow YAML frontmatter format
3. Test command functionality
4. Update documentation

### Removing Commands
1. Delete `.md` file from `.claude/commands/`
2. Restart Claude Code
3. Update documentation

## FAQ

**Q: Why do some commands use JSON and others use markdown?**
A: OOS is transitioning from JSON to markdown commands for better flexibility and documentation integration.

**Q: Do I need to restart Claude Code after every command change?**
A: Yes, Claude Code needs to reload the command database.

**Q: Can I have both JSON and markdown commands?**
A: Yes, but markdown commands are preferred for new development.

**Q: How do I debug a command that's not working?**
A: Use `/reload-commands` to see diagnostic information and verify command files exist.

**Q: Can I use MCP tools in slash commands?**
A: Yes! See `archon-status.md` for examples of MCP tool usage.