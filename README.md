# 🚀 OOS - Organized Operational Setup

**One command to transform any directory into an AI-powered development environment with secure credential management.**

## ⚡ 30-Second Quick Start

```bash
# 1. Install OOS (downloads everything needed)
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash

# 2. Use anywhere
mkdir my-project && cd my-project
oos
# → Asks you to sign into 1Password
# → Choose what you need (secure env, AI tools, etc.)
# → Done!
```

**That's it!** No complex commands, no manual configuration.

---

## 🎯 What is OOS?

OOS is a development environment bootstrapper that:
- 🔐 **Manages secrets securely** via 1Password (no API keys in your code!)
- 🤖 **Sets up AI development tools** (Claude, Gemini, Qwen) 
- ⚡ **Works context-aware** (different options based on where you run it)
- 🛠️ **Adds development utilities** (diagnostics, health checks, etc.)
- 📋 **Provides project templates** and best practices

---

## 🎪 How It Works

OOS detects your situation and shows relevant options:

### Empty Directory → New Project Setup
```
$ mkdir my-app && cd my-app && oos

🚀 OOS - Organized Operational Setup
📂 Empty directory - perfect for a new project!

What do you need?
1. 🔐 Just secure environment (.env from 1Password) ← RECOMMENDED
2. 🆕 Full project setup with AI tools
3. ❓ Show help

Choice [1-3]: 1
🔐 1Password authentication required
Run: eval $(op signin)
Continue after signing in? [y/N]: y
✅ Created .env with 50 secure variables
🎉 Done! Your secure environment is ready.
```

### Existing Project → Enhancement Options  
```
$ cd my-existing-app && oos

🛠️ Enhancing existing project...
Project: my-existing-app

What would you like to add?
1. 🔐 Add secure environment (.env from 1Password)
2. 🤖 Add AI CLI runners (Claude, Gemini, etc.)
3. 🔧 Add development tools (diagnostics, health checks)
4. 📋 All of the above
```

---

## 🔧 Requirements

### Automatically Checked During Install
- **Python 3.7+** (usually pre-installed)
- **Git** (for repository management)
- **curl, rsync** (common system tools)

### Optional (For Full Functionality)
- **1Password CLI** (`op`) - for secure environment management
- **GitHub CLI** (`gh`) - for GitHub integration  
- **Node.js/npm** - for JavaScript projects

**The installer checks everything and tells you exactly what to install if anything is missing.**

---

## 🚀 Real-World Usage

### Solo Developer - Quick Project Setup
```bash
# Install once
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash

# Use anywhere
mkdir side-project && cd side-project
oos  # Choose "secure environment" → instant API keys from 1Password
```

### Team Standardization
```bash
# Everyone runs the same install
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash

# Every project gets standardized setup
cd company-project && oos  # Same tools, same security, same workflow
```

### AI Development
```bash
oos  # Choose "full project setup"
# → Get Claude, Gemini, Qwen runners pre-configured
# → Start coding with AI immediately
```

---

## 🔐 Security Features

- **No secrets in code** - All API keys stored in 1Password
- **Environment isolation** - Each project gets its own `.env` 
- **Secure by default** - Automatically adds `.env` to `.gitignore`
- **Your credentials** - Uses your own 1Password vault

---

## 📖 Complete Documentation

- **[1Password Setup](1PASSWORD_SETUP.md)** - How to configure your secure environment
- **[Installation Guide](INSTALLATION.md)** - Detailed installation options
- **[Usage Examples](USAGE_EXAMPLES.md)** - Real-world scenarios  
- **[New Interface Guide](README_NEW_INTERFACE.md)** - Interactive system details
- **[System Overview](docs/SYSTEM_OVERVIEW.md)** - Technical architecture
- **[API Reference](docs/API_REFERENCE.md)** - Advanced features

---

## 🚨 Troubleshooting

### "oos: command not found"
```bash
# The installer creates a global command. If it doesn't work:
which oos  # Check if installed

# If not found, try full path:
~/oos/run.py

# Or reinstall:
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash
```

### "1Password authentication required"  
```bash
# Sign in first:
eval $(op signin)
# Enter your 1Password password

# Then use OOS:
oos
```

### "1Password item not found" or "No API keys"
You need to set up your 1Password vault with API keys:
- **[Complete 1Password Setup Guide](1PASSWORD_SETUP.md)** - Step-by-step instructions
- **Quick fix**: Create `bootstrap-env` item in `Private` vault with `env` field containing your API keys

### Missing System Requirements
```bash
# The installer tells you exactly what to install:

# Ubuntu/Debian:
sudo apt update && sudo apt install python3 git curl

# macOS:
brew install python3 git
# or install from https://www.python.org/downloads/
```

---

## 🎉 Why OOS?

### Before OOS
```bash
# Manual setup every project
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
pip install -r requirements.txt
mkdir -p .agents/runners
curl -o .agents/runners/run_claude.sh ...
chmod +x .agents/runners/run_claude.sh
echo ".env" >> .gitignore
# ... 30+ more lines of setup
```

### After OOS
```bash
oos
# Answer a few questions → Done!
```

---

## 🏗️ What Gets Created

When you use OOS, you get:

```
your-project/
├── .env                     # Secure API keys from 1Password
├── .gitignore              # Properly configured  
├── .agents/runners/        # AI CLI scripts
│   ├── run_claude.sh       # Claude with secure environment
│   ├── run_gemini.sh       # Gemini integration
│   └── run_qwen.sh         # Qwen integration
├── bin/                    # Development utilities
│   ├── diagnose.sh         # Fix problems automatically
│   ├── health_monitor.sh   # System monitoring
│   └── select_or_key.sh    # API key management
└── docs/                   # Project documentation
```

**Everything pre-configured, secure, and ready to use.**

---

## 🤝 Advanced Features

OOS also includes professional development tools:

| Tool | Purpose | Usage |
|------|---------|-------|
| **diagnose.sh** | Auto-fix problems | `./bin/diagnose.sh --self-heal` |
| **health_monitor.sh** | System monitoring | `./bin/health_monitor.sh daemon` |
| **security_audit.sh** | Security scanning | `./bin/security_audit.sh scan --fix` |
| **performance_monitor.sh** | Performance profiling | `./bin/performance_monitor.sh profile` |

**But you can ignore all this and just use `oos` for simple setup!**

---

## 🤝 Contributing

OOS is open source! Feel free to:
- Report issues on [GitHub Issues](https://github.com/Khamel83/oos/issues)
- Suggest features  
- Submit pull requests
- Share your project templates

---

## 💡 The OOS Philosophy

**Complex tools should have simple interfaces.**

OOS handles the complexity of:
- Secure credential management
- AI CLI configuration  
- Development tool setup
- Project scaffolding
- Security best practices

**So you can focus on building.**

---

**Ready to transform your development workflow?**

```bash
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash
```

**Then just run `oos` from any project directory! 🚀**