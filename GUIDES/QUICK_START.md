# 🚀 5-Minute Quick Start

**Copy-paste these commands. Zero thinking required.**

---

## ⚡ Installation (2 minutes)

**Open your terminal and run this:**
```bash
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash
```

**That's it. OOS is now installed.**

---

## 🎯 Your First Project (3 minutes)

**Create a new project:**
```bash
# Go where you want your project
cd ~/Documents  # or wherever you keep projects

# Create new project with OOS
oos create my-awesome-project
```

**Start coding immediately:**
```bash
# Enter your new project
cd my-awesome-project

# See that everything is ready
ls -la

# Start using it with Claude Code
# (if you have Claude Code installed)
claude-code .
```

---

## ✅ What Just Happened?

You now have a complete development project with:
- ✅ Python environment ready
- ✅ Git repository initialized
- ✅ AI tools configured
- ✅ Code quality tools installed
- ✅ Testing framework ready
- ✅ Everything just works

---

## 🛠️ Next Steps

**Option 1: Start Coding Immediately**
```bash
# Your project is ready. Start building!
# Create files, write code, commit to git - everything works.
```

**Option 2: Use OOS Features**
```bash
# See available OOS commands
oos --help

# Create a task (optional)
oos task create "Set up user authentication"

# See what tasks are ready
oos task ready
```

**Option 3: Keep Reading**
- [First Project Walkthrough](FIRST_PROJECT.md) - See what OOS actually created
- [Task System Basics](TASK_SYSTEM_SIMPLE.md) - Learn about task management
- [Emergency Refresher](EMERGENCY_REFRESHER.md) - For when you forget this

---

## 🎯 You're Done!

**That's the whole quick start.**

You now have a properly configured development project. The rest of OOS's features are optional - use them if you want, ignore them if you don't.

---

## 🆘 Troubleshooting

**"Command not found: oos"**
```bash
# Try restarting your terminal first
# If that doesn't work, add this to your shell profile:
echo 'export PATH="$HOME/oos/bin:$PATH"' >> ~/.zshrc  # or ~/.bashrc
source ~/.zshrc  # or ~/.bashrc
```

**"Permission denied"**
```bash
# Make sure the script is executable
chmod +x ~/oos/bin/oos
```

**"Something went wrong"**
```bash
# Check if you have the basics installed
which python git curl

# If any of those are missing, install them first:
# On Mac: brew install python git curl
# On Ubuntu: sudo apt install python3 git curl
```

---

## 💡 Pro Tip

**Bookmark this page.** When you haven't used OOS in a month and forget everything, come back and run these three commands:

1. `cd ~/Documents` (or wherever)
2. `oos create another-project`
3. `cd another-project`

That's it. You're back in business.