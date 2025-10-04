# 🚀 OOS - Open Operating System

**Unix Philosophy Development Toolchain - Modular, Composable, Reliable**

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/Khamel83/oos/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Working Commands](https://img.shields.io/badge/Working%20Commands-6-brightgreen.svg)](.claude/project_commands.json)
[![Installation](https://img.shields.io/badge/One%20Command%20Installation-✅-orange.svg)](#installation)

## 🎯 What OOS Actually Does

OOS is a **development toolchain** that installs into any project and provides reliable, repeatable workflows for security, testing, and environment validation.

**Core philosophy**: Write modules that do one thing well, compose intelligently.

### ⚡ What Actually Works

- **🔧 6 Working Slash Commands**: Proven functionality in Claude Code
- **🛡️ Security-First**: Automatic secret scanning and permission validation
- **🐍 Python Environment**: uv package manager and environment validation
- **🧪 Testing Integration**: Linting and test workflow automation
- **📦 Universal Installation**: One command works in any project
- **🔄 GitHub Updates**: Seamless updates that preserve working functionality

## 🚀 Installation (Actually Works)

### Method 1: GitHub Installation (Recommended)
```bash
# In ANY project directory:
bash <(curl -s https://raw.githubusercontent.com/Khamel83/oos/master/install.sh)
```

### Method 2: Local Installation
```bash
# From OOS source directory:
./bin/oos-install-into-project.sh /path/to/your-project
```

**After Installation:**
1. Restart Claude Code completely
2. Slash commands appear automatically

## 📋 Available Commands

### Core Workflow Commands
```bash
/start-coding      # Complete development session setup
/dev-setup         # Environment validation (security + python + git)
/pre-commit        # Pre-commit validation workflow
/modules list       # See all available modules
/modules run security/scan_secrets .  # Run specific module
/update-oos        # Update OOS from GitHub
/create-project    # Create new projects from templates
```

### Module Categories
- **Security**: `scan_secrets`, `check_permissions`, `check_1password`
- **Python**: `check_uv`, environment validation
- **Testing**: `lint_code`, `run_pytest`
- **Git**: `check_status`, validation workflows

## 🔧 Daily Usage Pattern

### Starting Development
```bash
cd /path/to/your-project
/start-coding
```
This validates your environment and sets up your development session.

### During Development
```bash
/modules security/scan_secrets .     # Before adding API keys
/modules python/check_uv              # Check dependencies
/modules testing/lint_code            # Code quality check
```

### Before Committing
```bash
/pre-commit
```
Runs security scan → linting → tests → generates commit message.

### New Projects
```bash
cd /path/to/new-project
bash <(curl -s https://raw.githubusercontent.com/Khamel83/oos/master/install.sh)
```

## 🏗️ System Architecture

### Core Components
```
oos/
├── .claude/
│   └── project_commands.json    # 6 working slash commands
├── bin/
│   ├── oos-module-runner.sh      # Module execution engine
│   ├── oos-update-from-github.sh # GitHub updater
│   └── claude-start-coding.sh    # Session setup
├── modules/
│   ├── security/                 # Security validation modules
│   ├── python/                   # Python environment modules
│   ├── testing/                  # Testing and linting modules
│   └── git/                      # Git workflow modules
└── compositions/
    ├── full-dev-setup.sh         # Complete environment validation
    └── pre-commit.sh             # Pre-commit workflow
```

### Design Principles
- **Unix Philosophy**: Each module does one thing well
- **Composable**: Modules combine into workflows
- **Reliable**: Fails fast with clear error messages
- **Portable**: Works on Linux, macOS, WSL
- **No Dependencies**: Pure shell scripts

## ✅ What's Been Thoroughly Tested

### Working Commands (100% Verified)
- ✅ `/modules` - Lists and executes all modules
- ✅ `/dev-setup` - Complete environment validation
- ✅ `/pre-commit` - Security + lint + test workflow
- ✅ `/update-oos` - GitHub updates preserve functionality
- ✅ `/create-project` - Project template creation
- ✅ `/start-coding` - Development session setup

### Installation Verified
- ✅ Fresh installation in clean directories
- ✅ GitHub curl installation method
- ✅ All referenced scripts exist and are executable
- ✅ Update cycles preserve working functionality

## 🛠️ Technical Details

### Module System
Each module is a standalone shell script that:
- Returns appropriate exit codes (0 = success, 1 = failure)
- Provides clear output for human reading
- Can be executed individually or composed
- Has no external dependencies beyond standard Unix tools

### Error Handling
- **Graceful Failure**: Modules fail with clear error messages
- **Environment Validation**: Checks for required tools before execution
- **Permission Safety**: Validates file permissions before operations
- **Secret Protection**: Scans for exposed credentials

### Performance Characteristics
- **Memory Usage**: Minimal (shell scripts only)
- **Disk Usage**: ~5MB for full installation
- **Network**: Required only for GitHub installation/updates
- **Execution Speed**: 1-120 seconds depending on operation

## 🔍 Troubleshooting

### Common Issues

**Slash commands not appearing:**
```bash
# Restart Claude Code completely
# Verify .claude/slash_commands.json exists
cat .claude/slash_commands.json
```

**Module execution failures:**
```bash
# Check module exists and is executable
ls -la modules/security/scan_secrets.sh
# Test module directly
./modules/security/scan_secrets.sh .
```

**Installation failures:**
```bash
# Use local installation method
./bin/oos-install-into-project.sh .
# Or verify GitHub connectivity
curl -s https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | head -5
```

### Getting Help
1. Check this README for your use case
2. Run `/modules list` to see available functionality
3. Test individual modules before compositions
4. Check GitHub issues for known problems

## 📚 Documentation Structure

### For Humans
- `README.md` - This file, comprehensive overview
- `QUICK_START.md` - Fast setup guide
- `OOS_2.0_VISION.md` - Future architecture discussion

### For AI/Machines
- `docs/AI_COMPREHENSIVE_GUIDE.md` - Complete technical specifications
- `.claude/project_commands.json` - Slash command definitions
- Module source code with clear interfaces

## 🤝 Contributing

OOS follows these principles:
- **Working code over theoretical architecture**
- **Test before commit** (use `/pre-commit`)
- **Unix philosophy** - keep it simple and composable
- **No breaking changes** without thorough testing

### Development Workflow
1. Install OOS in your development environment
2. Use `/start-coding` for session setup
3. Use `/pre-commit` before all commits
4. Test with fresh installations

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **GitHub Repository**: https://github.com/Khamel83/oos
- **Installation Script**: https://raw.githubusercontent.com/Khamel83/oos/master/install.sh
- **Issues**: https://github.com/Khamel83/oos/issues

---

**OOS is designed for developers who value reliability, security, and simplicity in their daily workflow. Install once, use everywhere.**