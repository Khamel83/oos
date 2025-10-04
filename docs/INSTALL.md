# OOS Installation Guide

## 🚀 One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/Khamel83/oos/master/bin/oos-bootstrap.sh | bash
```

This command will:
1. Clone OOS to `~/.oos`
2. Install OOS into your current project
3. Set up Claude Code slash commands
4. Give you a quick start guide

## 📋 What You Get

After installation, you'll have these **slash commands** in Claude Code:

- `/dev-setup` - Complete development environment validation
- `/pre-commit` - Security scan + lint + tests + AI commit message
- `/modules` - Run/compose individual modules
- `/create-project` - Create new projects from templates
- `/update-oos` - Update OOS from GitHub

## 🎯 Real UX Workflow

### First Time Using OOS
```bash
# 1. In your project directory
curl -sSL https://raw.githubusercontent.com/Khamel83/oos/master/bin/oos-bootstrap.sh | bash

# 2. Restart Claude Code

# 3. In Claude Code
/dev-setup
```

### Daily Development Workflow
```bash
# Before coding
/dev-setup

# Before committing
/pre-commit

# Create new project
/create-project python-project my-new-app
```

### Updating OOS
```bash
# In Claude Code
/update-oos

# Then restart Claude Code to get new commands
```

## 🔧 Manual Installation (Alternative)

If you prefer manual control:

```bash
# 1. Clone OOS
git clone https://github.com/Khamel83/oos.git ~/.oos

# 2. Install into your project
~/.oos/bin/oos-install-into-project.sh

# 3. Restart Claude Code
```

## 🏗️ Project Structure After Install

```
your-project/
├── .claude/
│   └── slash_commands.json    # Claude Code slash commands
├── modules/                   # OOS module system
├── compositions/             # Workflow compositions
├── bin/                      # OOS tools
├── .oos-project             # OOS marker file
└── .gitignore               # Updated with OOS entries
```

## 🎯 UX Goals Achieved

### ✅ **Discovery**: One-line install from anywhere
### ✅ **Integration**: Automatically sets up Claude Code
### ✅ **Persistence**: Slash commands travel with your project
### ✅ **Updates**: `/update-oos` keeps everything current
### ✅ **Portability**: Works in any project, any directory

## 🚨 Important UX Notes

1. **Restart Claude Code** after installation to load slash commands
2. **Restart Claude Code** after `/update-oos` to get new commands
3. **OOS files are in .gitignore** by default (they get copied, not versioned)
4. **`.oos-project` marker** shows this project uses OOS

## 🔄 The Complete UX Loop

```
1. curl install → 2. restart Claude Code → 3. /dev-setup → 4. start coding
                                                ↓
5. /pre-commit → 6. commit → 7. /update-oos (occasionally) → restart Claude Code
```

This creates a **seamless development experience** where OOS is always available but never in your way.