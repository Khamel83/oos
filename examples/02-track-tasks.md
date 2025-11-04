# I Want to Track My Tasks

## The Problem
I have work to do and want to track it systematically.

## The Commands

```bash
# Create tasks
oos task create "Build authentication system"
oos task create "Add database migrations"
oos task create "Write API documentation"

# See all tasks
oos task list

# Start working on one
oos task start abc123

# Check what I'm working on
oos task list

# Mark it done
oos task done abc123
```

## What You'll See

```
Created task: abc123 - Build authentication system

Found 3 task(s):
⏳ 🟠 abc123: Build authentication system
⏳ 🟠 def456: Add database migrations
⏳ 🟠 ghi789: Write API documentation

Started task: abc123

Found 3 task(s):
🚀 🟢 abc123: Build authentication system (in progress)
⏳ 🟠 def456: Add database migrations
⏳ 🟠 ghi789: Write API documentation

Completed task: abc123
```

## Troubleshooting

**"Task database not found"**
```bash
oos dev setup
```

**"ModuleNotFoundError: click"**
```bash
oos dev setup
```
