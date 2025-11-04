# I Want to Start a New Project

## The Problem
I have an idea and want to start building it with OOS already set up.

## The Commands

```bash
# Create project
oos project create my-awesome-app

# Enter project
cd my-awesome-app

# Setup environment
oos dev setup

# Create first task
oos task create "Build MVP"

# Start working
oos task start <task-id>
```

## What You'll See

```
Creating project: my-awesome-app
📋 Installing Claude Code commands...
✅ All Claude Code commands installed
✅ OOS Installation Complete!

Development Environment Setup
========================================
✅ uv installed (uv 0.8.17)
📦 Installing Python dependencies...
✅ Python dependencies installed
✅ OOS directories created
✅ .env file created

Setup Complete!
```

## Next Steps

- Edit `.env` to add API keys (optional)
- Run `oos status` to see what's available
- Create tasks and start building

## Troubleshooting

**"Command not found: oos"**
- Make sure you ran install in OOS repo first
- Or add OOS bin to PATH

**"uv not found"**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
