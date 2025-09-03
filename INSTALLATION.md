# 🚀 OOS Installation Guide

## Quick Install

```bash
# Clone OOS anywhere you want
git clone https://github.com/Khamel83/oos.git
cd oos

# Make it globally accessible (recommended)
sudo ln -sf $(pwd)/run.py /usr/local/bin/oos

# OR add to your PATH
echo 'export PATH="$PATH:'$(pwd)'"' >> ~/.bashrc
source ~/.bashrc
```

## Usage After Installation

### Option 1: Global Command (Recommended)
```bash
# After installation with sudo ln -sf
cd anywhere
oos  # Works from any directory!
```

### Option 2: Full Path
```bash
# If you cloned to ~/oos
cd my-project
~/oos/run.py
```

### Option 3: Added to PATH
```bash
# If you added oos to PATH
cd my-project
run.py
```

## Installation Examples

### Example 1: System-wide Installation
```bash
# Install for all users
cd /opt
sudo git clone https://github.com/Khamel83/oos.git
sudo ln -sf /opt/oos/run.py /usr/local/bin/oos

# Now anyone can use:
oos
```

### Example 2: Personal Installation
```bash
# Install in your home directory
cd ~
git clone https://github.com/Khamel83/oos.git

# Use with full path:
~/oos/run.py

# OR create personal alias
echo 'alias oos="~/oos/run.py"' >> ~/.bashrc
source ~/.bashrc

# Now you can use:
oos
```

### Example 3: Project-specific
```bash
# Clone into your projects directory
cd ~/projects
git clone https://github.com/Khamel83/oos.git

# Use from any project:
cd my-existing-app
../oos/run.py
```

## Real-World Usage Flow

```bash
# 1. Install OOS once
git clone https://github.com/Khamel83/oos.git ~/oos
sudo ln -sf ~/oos/run.py /usr/local/bin/oos

# 2. Use anywhere
mkdir ~/projects/my-new-api
cd ~/projects/my-new-api
oos  # Context-aware setup!

# 3. Enhance existing projects
cd ~/projects/my-react-app
oos  # Adds OOS tools to existing project
```

## What Gets Installed Where

```
~/oos/                          # OOS repository
├── run.py                      # Main interactive launcher
├── bootstrap_enhanced.sh       # Legacy full bootstrap
├── lib/                        # Shared utilities
└── templates/                  # Project templates

/usr/local/bin/oos             # Global symlink (optional)
→ points to ~/oos/run.py
```

## Requirements Check

```bash
# Check if you have requirements
oos --help  # Should show help if installed correctly

# Requirements:
# ✅ Python 3 (usually pre-installed)
# ✅ Git (for project management)
# ⚠️  1Password CLI (optional, for secure environments)
# ⚠️  GitHub CLI (optional, for GitHub integration)
```

## Troubleshooting

### "oos: command not found"
```bash
# Check if symlink exists
ls -la /usr/local/bin/oos

# If not, create it:
sudo ln -sf ~/oos/run.py /usr/local/bin/oos

# Or use full path:
~/oos/run.py
```

### "Permission denied"
```bash
# Make sure it's executable
chmod +x ~/oos/run.py
```

### "Python not found"
```bash
# Install Python 3 (Ubuntu/Debian)
sudo apt update && sudo apt install python3

# Install Python 3 (macOS)
brew install python3
```

## One-Line Install Script

```bash
# Complete installation in one command
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash
```

This will:
1. Clone the repo to `~/oos`
2. Create the global `oos` command
3. Check all requirements
4. Show usage examples

## After Installation

### 1. Set up 1Password (Required for secure environment)
See **[1Password Setup Guide](1PASSWORD_SETUP.md)** for complete instructions.

Quick setup:
```bash
# Install 1Password CLI
brew install --cask 1password-cli  # macOS
# or follow OS-specific instructions in the guide

# Create bootstrap-env item in 1Password with your API keys
# See 1PASSWORD_SETUP.md for exact format
```

### 2. Use OOS anywhere
```bash
mkdir my-project && cd my-project
oos  # Context-aware setup with simple questions!
```

---

**After installation, just run `oos` from any directory!**