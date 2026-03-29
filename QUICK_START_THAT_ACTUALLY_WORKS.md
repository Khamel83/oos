# Quick Start That Actually Works

**No BS. No "production ready" claims. Just what works.**

## For the OOS Repository Itself

**If you're IN the OOS repo (this one), here's what works:**

### 1. Install Dependencies

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv sync

# Takes ~15 seconds, downloads ~80 packages
```

### 2. Test It Works

```bash
# List tasks (should show 3 tasks)
./bin/claude-task.sh list

# OR use the Python CLI directly
uv run python -m src.oos_task_system.cli list

# If you see tasks, it works! 🎉
```

### 3. What Actually Works

**✅ Working commands:**
- `./bin/claude-task.sh list` - List all tasks
- `./bin/claude-task.sh ready` - Show ready tasks
- `./bin/claude-task.sh create "Title" "Description"` - Create task
- `./bin/claude-task.sh show <task-id>` - Show task details
- `./bin/claude-task.sh update <task-id> --status doing` - Update task

**❌ Not implemented yet:**
- Most other `/` commands (they're stubs)
- Archon integration (needs MCP setup)
- AI analysis features (need API keys)
- 1Password integration (need 1Password CLI)

---

## For OTHER Projects (Installing OOS)

**Installing OOS into a different project:**

### 1. Run Install Script

```bash
cd ~/your-project
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash
```

### 2. What You Get

**✅ Installed:**
- 11 bash scripts in `bin/`
- 11 Claude Code commands in `.claude/commands/`
- Module structure
- Compositions

**❌ NOT installed:**
- Python dependencies (not needed for lightweight install)
- Task system (OOS repo only)
- Python-based features

### 3. What Works in Other Projects

**These slash commands work:**
- `/dev check` - Basic environment check
- `/help` - Show command help
- Others mostly show help text or stubs

**To use task system in other projects:**
- Copy the task system from OOS repo
- Or just use OOS repo for task management

---

## Common Issues

### "ModuleNotFoundError: No module named 'click'"

**Problem:** Python dependencies not installed

**Fix:**
```bash
uv sync
```

### "uv: command not found"

**Problem:** uv not installed

**Fix:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Then restart shell or run: source ~/.bashrc
```

### "/task list shows fake output"

**Problem:** Old version of claude-task.sh (pre-fix)

**Fix:**
```bash
# Pull latest changes
git pull origin main

# Or re-download the script
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/bin/claude-task.sh > bin/claude-task.sh
chmod +x bin/claude-task.sh
```

---

## What's Actually Production Ready

**✅ Stable and working:**
- Task system (SQLite + JSONL)
- Python CLI (full featured)
- JSONL export/import
- Task dependencies
- Basic slash command structure

**🔧 Works but needs setup:**
- AI SDK (need API keys)
- Archon integration (need MCP server)
- 1Password (need CLI installed)

**❌ Not ready:**
- Most slash commands (stubs)
- Automated workflows
- "11 perfect commands" (only /task works fully)

---

## The Honest Roadmap

### What Works Today (2024-11-04)
- Task CLI (`./bin/claude-task.sh`)
- Python dependencies install (`uv sync`)
- Basic project structure

### What's Coming Next
1. Fix remaining slash commands to use real implementations
2. Test installation on fresh systems
3. Document what actually requires what dependencies
4. Remove "production ready" claims until it is

---

## Development Commands

**If you're developing OOS itself:**

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest

# Check code quality
uv run ruff check .
uv run black --check .

# Format code
uv run black .

# Run specific test
uv run pytest tests/test_task_database.py -v
```

---

## Getting Help

**When filing issues:**
1. Say which scenario: OOS repo OR other project
2. Show the exact command that failed
3. Include error message
4. Mention if you ran `uv sync`

**Good issue:**
```
Environment: OOS repository
Command: ./bin/claude-task.sh list
Error: ModuleNotFoundError: No module named 'click'
Ran uv sync: No

Fix: After running `uv sync` it works
```

**Bad issue:**
```
OOS doesn't work
```

---

## Summary

**TL;DR:**
1. In OOS repo: Run `uv sync`, then `./bin/claude-task.sh` works
2. In other projects: Install script gives you command structure only
3. Most features are WIP, don't expect everything to work yet
4. Task system is the main working feature right now

**Last updated:** 2024-11-04
**Status:** Partially working, actively fixing
