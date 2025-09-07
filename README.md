# 🚀 OOS - Organized Operational Setup

**Secure, bulletproof development environment setup with built-in API key protection and file safety.**

> **🔒 Security First**: OOS includes automatic API key detection and prevention, ensuring your secrets never get committed to repositories. Every operation is designed with security and user data preservation in mind.

---

## ⚡ Quick Start

**Set up a secure development environment in seconds:**

```bash
# 1. Clone and set up OOS
git clone https://github.com/Khamel83/oos.git
cd oos
./scripts/bootstrap_enhanced.sh

# 2. Use in any project (preserves existing files!)
./scripts/bootstrap_enhanced.sh --verbose my-project /path/to/project
# → Automatic API key protection installed
# → Safe file creation (never overwrites without --force)  
# → Complete development environment ready
```

**Key Features:**
- 🔒 **API Key Protection**: Pre-commit hooks prevent accidental key exposure
- 🛡️ **File Safety**: Never overwrites existing files without explicit consent
- ⚡ **One Command Setup**: Complete development environment in minutes
- 🤖 **AI-Ready**: Claude, Gemini, and Qwen integration included

---

## 📖 Documentation

### For Users

*   **🚀 Getting Started**
    *   [Installation Guide](docs/INSTALLATION.md)
    *   [Usage Guide](docs/USAGE_GUIDE.md)
    *   [1Password Setup](docs/1PASSWORD_SETUP.md)
*   **🔒 Security & Safety**
    *   [File Safety Features](docs/BOOTSTRAP_FILE_SAFETY.md) - How OOS protects your existing files
    *   [API Key Protection](bin/prevent_api_key_commits.sh) - Built-in security against credential exposure
*   **🔧 Advanced Topics**
    *   [Advanced Installation](docs/ADVANCED_INSTALLATION.md)
    *   [Advanced Usage](docs/ADVANCED_USAGE_GUIDE.md)
    *   [Troubleshooting](docs/TROUBLESHOOTING.md)

### For Contributors

*   **Core Concepts**
    *   [Contributing Guide](CONTRIBUTING.md)
    *   [System Overview](docs/SYSTEM_OVERVIEW.md)
    *   [Development Philosophy](docs/DEVELOPMENT_PHILOSOPHY.md)
    *   [Testing Philosophy](docs/TESTING_PHILOSOPHY.md)
*   **🛠️ Development Guides**
    *   [AI Collaboration Guide](docs/AI_COLLABORATION_GUIDE.md)
    *   [API Reference](docs/API_REFERENCE.md)
    *   [Archon Integration](docs/ARCHON_INTEGRATION.md)
    *   [Operations Guide](docs/OPERATIONS.md)
*   **📋 Launch & Quality**
    *   [Launch Readiness Checklist](docs/BOOTSTRAP_LAUNCH_READINESS.md) - Product launch methodology
    *   [Comprehensive Testing](tests/test_bootstrap_safe_files.sh) - Complete test suite
*   **Agent-Specific Guidelines**
    *   [Agent Guidelines](.agents/agents.md)
    *   [Claude](docs/CLAUDE.md)
    *   [Gemini](docs/GEMINI.md)
    *   [Qwen](docs/qwen.md)

---

## 🔒 Security & Safety Features

**OOS is built with security and user data protection as core principles:**

### Bulletproof API Key Protection
- **Pre-commit hooks** automatically scan every commit for API keys
- **Blocks dangerous patterns**: OpenAI, GitHub, Google, AWS, and generic long keys
- **Allows safe placeholders**: `your_api_key_here`, `sk-test-example`, etc.
- **Works everywhere**: OOS projects and all created projects get automatic protection

### Safe File Operations  
- **Never overwrites existing files** without explicit `--force` flag
- **Clear user warnings** with guidance on how to proceed
- **Automatic backups** when overwriting with `--force`
- **Edge case handling**: symlinks, directories, permission errors

### Monitoring & Validation
- **Self-contained logging** with sanitized sensitive data
- **Comprehensive testing** with 10+ scenarios covering all edge cases
- **Product launch methodology** ensuring reliability and user safety

### Usage Examples

```bash
# Safe by default - preserves existing files
./scripts/bootstrap_enhanced.sh my-project

# Output: [WARN] Skipping existing file: docs/CLAUDE.md
#         [WARN]   → Use --force to overwrite (automatic backup will be created)

# Explicit overwrite with backup
./scripts/bootstrap_enhanced.sh --force my-project

# API key protection in action
git commit -m "add config"
# Output: 🚨 COMMIT BLOCKED - API keys found in staged files!
#         File: config.js:10
#         Key: sk-proj-abc123... [REDACTED]
```

---

### Other Documents

*   [Security Policy](SECURITY.md)
*   [Code Manifest](CODE_MANIFEST.md)
*   [License](LICENSE)