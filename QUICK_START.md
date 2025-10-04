# 🚀 Quick Start Guide

Get OOS running in your project in under 2 minutes.

## 1️⃣ Install OOS

```bash
# In any project directory:
bash <(curl -s https://raw.githubusercontent.com/Khamel83/oos/master/install.sh)
```

**Expected output:**
```
🚀 Installing OOS into your-project
==================================
📋 Installing slash commands...
✅ Slash commands installed
🔧 Installing OOS tools...
🧩 Installing modules...
🏗️ Installing compositions...
📝 Updating .gitignore...
✅ OOS Installation Complete!

Available commands in Claude Code:
  /dev-setup     - Validate development environment
  /modules       - Run security/python/git modules
  /pre-commit    - Pre-commit validation workflow
  /update-oos    - Update OOS from GitHub
  /create-project - Create new projects from templates
  /start-coding  - Complete development session setup

🔄 Restart Claude Code to use slash commands!
```

## 2️⃣ Restart Claude Code

Close and restart Claude Code to load the new slash commands.

## 3️⃣ Start Developing

```bash
cd /path/to/your-project
/start-coding
```

This validates your environment and sets up your development session.

## 4️⃣ Available Commands

### Daily Usage
```bash
/start-coding              # Start development session
/modules list              # See available modules
/modules security/scan_secrets .  # Scan for secrets
/dev-setup                 # Validate environment
/pre-commit               # Run before committing
```

### Project Management
```bash
/create-project           # Create new projects
/update-oos               # Update OOS from GitHub
```

## 5️⃣ What You Get

- ✅ **6 working slash commands** in Claude Code
- ✅ **Security scanning** for secrets and permissions
- ✅ **Python environment** validation with uv
- ✅ **Code linting** and test workflows
- ✅ **Pre-commit validation** automation

## 🆘 Need Help?

- **[USER_READY_SETUP.md](USER_READY_SETUP.md)** - Detailed usage guide
- **[README.md](README.md)** - Complete documentation
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

## 🎯 Pro Tips

1. **Run `/start-coding`** whenever you begin working on a project
2. **Use `/pre-commit`** before every commit for code quality
3. **Run `/modules security/scan_secrets .`** before adding API keys
4. **Update with `/update-oos`** to get the latest features

---

**That's it! You're ready to use OOS.** 🎉

**For more details, check out the [complete documentation](README.md#-documentation).**