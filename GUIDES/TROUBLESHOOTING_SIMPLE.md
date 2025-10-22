# 🔧 Simple Troubleshooting

**When OOS doesn't work and you need help fast.**

---

## 🚀 Installation Issues

### "Command not found: oos"
```bash
# Try restarting your terminal first
# If that doesn't work, add OOS to your PATH:
echo 'export PATH="$HOME/oos/bin:$PATH"' >> ~/.zshrc  # or ~/.bashrc
source ~/.zshrc  # or ~/.bashrc

# Test it
oos --help
```

### "Permission denied"
```bash
# Make OOS executable
chmod +x ~/oos/bin/oos
chmod +x ~/oos/bin/*

# If you used the install script, try this:
chmod +x ~/oos/scripts/*.sh
```

### "Python not found"
```bash
# Install Python (you need it for OOS)
# On Mac:
brew install python3

# On Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip

# On Windows:
# Download from python.org
```

---

## 📁 Project Issues

### "Database not found"
```bash
# You're probably not in an OOS project
# Check if you're in the right directory:
pwd
ls -la

# Look for .oos/ directory
if [ -d ".oos" ]; then
  echo "You're in an OOS project"
else
  echo "Not an OOS project. Create one:"
  oos create new-project
  cd new-project
fi
```

### "Can't create tasks"
```bash
# Make sure .oos/tasks/ directory exists
mkdir -p .oos/tasks

# Check permissions
ls -la .oos/
chmod 755 .oos/
chmod 755 .oos/tasks/

# Try again
oos task create "Test task"
```

### "Git not initialized"
```bash
# Initialize git in your project
git init

# Or create a new project with git:
oos create my-project --git
cd my-project
```

---

## 📋 Task Issues

### "Task ID not found"
```bash
# Find the correct task ID
oos task list

# Or search for partial IDs
oos task list | grep "abc"

# Use the full ID shown in the list
oos task show abc12345  # Use the full ID, not just abc123
```

### "No ready tasks"
```bash
# See all tasks to understand why
oos task list

# Check blocked tasks
oos task list --status blocked

# You might need to complete dependencies first
oos task show [task_id] | grep "Depends"
```

### "Can't complete task"
```bash
# Check if task has dependencies
oos task show abc123

# Complete dependencies first
oos task complete [dependency_id]

# Or remove the dependency if it's not needed
oos task update abc123 --remove-dependencies [dependency_id]
```

---

## 🔧 Common Error Messages

### "Database is locked"
```bash
# Another process is using the database
# Wait a minute and try again

# Or find what's using it
lsof .oos/tasks/tasks.db

# Last resort - restart your terminal
```

### "Invalid JSON"
```bash
# Usually happens with import/export
# Validate your JSONL file
python -c "
import json
with open('your-file.jsonl') as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line)
        except json.JSONDecodeError:
            print(f'Invalid JSON on line {i}: {line.strip()}')
"

# Fix the line or remove it
```

### "Permission denied" when writing files
```bash
# Check directory permissions
ls -la .oos/
ls -la .oos/tasks/

# Fix permissions if needed
chmod -R 755 .oos/

# Or check if files are owned by you
ls -la .oos/tasks/tasks.db
```

---

## 🔄 Command Not Working

### "oos task command not found"
```bash
# Check if you're in an OOS project
if [ ! -d ".oos" ]; then
  echo "Not in an OOS project directory"
  echo "Current directory: $(pwd)"
  echo "OOS projects have a .oos/ folder"
fi

# Try full command path
python -m src.oos_task_system.cli task list
```

### Commands run but do nothing
```bash
# Check if database exists
if [ ! -f ".oos/tasks/tasks.db" ]; then
  echo "No task database found. Creating..."
  mkdir -p .oos/tasks
  oos task create "Initial task"
fi

# Check database content
sqlite3 .oos/tasks/tasks.db "SELECT COUNT(*) FROM tasks;"
```

---

## 📊 Performance Issues

### Commands are slow
```bash
# Check database size
ls -lh .oos/tasks/tasks.db

# If it's huge (>100MB), consider archiving
oos task export archive.jsonl --status done
# (then manually delete old tasks)

# Or check for corruption
sqlite3 .oos/tasks/tasks.db "PRAGMA integrity_check;"
```

### Too many tasks to process
```bash
# Use limits to reduce output
oos task list --limit 10

# Filter tasks
oos task list --status todo
oos task list --priority high
oos task list --assignee $(whoami)
```

---

## 🆘 Quick Reset

### Something is fundamentally broken
```bash
# Backup current tasks
oos task export backup-$(date +%Y%m%d).jsonl

# Reset task system (WARNING: deletes all tasks)
rm -f .oos/tasks/tasks.db
mkdir -p .oos/tasks

# Start fresh
oos task create "Fresh start after reset"
```

### Reset OOS installation
```bash
# Remove OOS (WARNING: deletes all OOS data)
rm -rf ~/oos

# Reinstall
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/scripts/install.sh | bash
```

---

## 🎯 Debug Mode

### Get more information
```bash
# Enable debug output
export OOS_TASKS_DEBUG=1

# Run commands with verbose output
oos task list --debug

# Check environment
echo "OOS installed at: $(which oos)"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "OOS project: $([ -d .oos ] && echo 'Yes' || echo 'No')"
```

### Check system health
```bash
# Basic checks
echo "=== System Check ==="
echo "Python: $(which python3)"
echo "Git: $(which git)"
echo "OOS: $(which oos)"
echo "Database: $([ -f .oos/tasks/tasks.db ] && echo 'Exists' || echo 'Not found')"

# Test basic functionality
echo "=== Functionality Test ==="
oos --help > /dev/null && echo "✅ OOS command works" || echo "❌ OOS command failed"
oos task list > /dev/null && echo "✅ Task list works" || echo "❌ Task list failed"
```

---

## 📱 Getting Help

### When all else fails
```bash
# Check OOS version (if available)
oos --version

# Get help on specific commands
oos task --help
oos task create --help
oos task list --help

# Look at logs (if they exist)
ls -la ~/.oos/logs/ 2>/dev/null || echo "No logs found"
tail -f ~/.oos/logs/oos.log 2>/dev/null || echo "No log file"
```

### What to report when asking for help
```bash
# Run this and share the output
echo "=== OOS Troubleshooting Info ==="
echo "Date: $(date)"
echo "OS: $(uname -s)"
echo "Shell: $SHELL"
echo "Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "Git: $(git --version)"
echo "OOS: $(oos --version 2>/dev/null || echo 'Not found')"
echo "Current dir: $(pwd)"
echo "OOS project: $([ -d .oos ] && echo 'Yes' || echo 'No')"
echo "Database: $([ -f .oos/tasks/tasks.db ] && echo 'Exists' || echo 'Not found')"
echo "Database size: $([ -f .oos/tasks/tasks.db ] && ls -lh .oos/tasks/tasks.db | awk '{print $5}' || echo 'N/A')"
```

---

## 💡 Prevention Tips

**Avoid these common problems:**

1. **Always work in OOS project directories** - Check for `.oos/` folder
2. **Regular backup tasks** - `oos task export backup.jsonl`
3. **Don't edit database manually** - Use the commands
4. **Keep reasonable task counts** - Archive old completed tasks
5. **Update dependencies properly** - Complete or remove them cleanly
6. **Use full task IDs** - Don't guess partial IDs

---

## 🎯 Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| **Command not found** | Restart terminal or check PATH |
| **Database not found** | Run `oos create new-project` in new directory |
| **Task ID not found** | Run `oos task list` to see correct IDs |
| **No ready tasks** | Check `oos task list` for blocked tasks |
| **Permission errors** | `chmod 755 .oos/` and subdirectories |
| **Something broken** | Export tasks, delete `.oos/tasks/tasks.db`, start fresh |

---

*Remember: Most OOS problems are either: 1) Not in the right directory, 2) Database issues, or 3) Task ID confusion. Check these three things first.*