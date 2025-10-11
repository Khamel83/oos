# Slash Commands Issue - Root Cause Analysis

## 🚨 Critical Discovery

Found the root cause of slash commands not working: **OOS has two conflicting command systems**

## Problem Details

### System 1: Claude Code Native (WORKING) ✅
- Location: `.claude/commands/*.md`
- Format: Markdown files with YAML frontmatter
- Example: `help-me.md`, `validate.md`, `archon-status.md`
- **This is what Claude Code actually uses**

### System 2: OOS Custom Scripts (BROKEN) ❌
- Location: `.claude/slash_commands.json`
- Format: JSON with script paths
- Example: `"start-coding": "bin/claude-start-coding.sh"`
- **Claude Code cannot read this format**

## Evidence

Commands that DO work (markdown files exist):
- `/help-me` ✅ (.claude/commands/help-me.md exists)
- `/validate` ✅ (.claude/commands/validate.md exists)
- `/archon-status` ✅ (.claude/commands/archon-status.md exists)

Commands that DON'T work (only in JSON):
- `/start-coding` ❌ (only in slash_commands.json)
- `/screenshot` ❌ (only in slash_commands.json)
- `/provision` ❌ (only in slash_commands.json)

## Root Cause

When Claude Code looks for `/start-coding`, it searches:
1. `.claude/commands/start-coding.md` - doesn't exist
2. `.claude/slash_commands.json` - ignored by Claude Code

The JSON system is **completely invisible** to Claude Code.

## Why This Happened

1. **Original OOS**: Used custom JSON format for slash commands
2. **Claude Code evolution**: Switched to markdown-based commands
3. **Missed migration**: OOS never updated to new format
4. **Result**: Commands exist in JSON but Claude can't see them

## Immediate Fix Needed

Convert JSON commands to markdown format and remove deprecated system.