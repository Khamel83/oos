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

**Quick Navigation:**
- [For Users](#for-users) | [For Contributors](#for-contributors)
- [Security Features](#-security--safety-features) | [LLM Gateway](#-llm-gateway-bifrost--zai-overflow)

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

## 🌐 LLM Gateway (Bifrost) + Z.AI Overflow

**Seamlessly switch between Anthropic Pro and cost-effective Z.AI GLM-4.5 while preserving your existing Claude Code + MCP setup.**

**Quick Navigation:**
- [How to Use (Day-to-Day)](#how-to-use-day-to-day)
- [One-Time Setup](#one-time-setup)
- [MCP (Archon + Others)](#mcp-archon--others)
- [Gateway Management](#gateway-management)
- [Keys & Safety](#keys--safety)

### How to Use (Day-to-Day)

**🎯 Best UX (Recommended):** Start every session through Bifrost on Anthropic → switch to Z.AI in-session when you hit Pro limits.

```bash
# 1. Start gateway once (on your OCI VM)
bash scripts/llm_gateway_up.sh

# 2. Start Claude Code on Anthropic (via gateway)
source scripts/cc-launchers.sh
cc-sona

# 3. Work as usual. When you hit limits, don't restart—just:
/model zai/glm-4.5

# You can always switch back: /model anthropic/claude-4-sonnet
# Model switching mid-session is fully supported
```

**Alternative:** Start direct Pro, switch to gateway when needed:
```bash
cc-pro                    # Start direct Pro
# When you hit limits, exit and run:
cc-sona                   # Switch to gateway mode  
claude -c                 # Resume your last conversation
# Or resume specific session: claude -r "<session-id>"
```

### One-Time Setup

```bash
# 1. Start the gateway
bash scripts/llm_gateway_up.sh

# 2. Open Bifrost UI → add providers
# Open http://127.0.0.1:8080
# Go to Providers → Add:
#   • Anthropic: paste your console API key
#   • Z.AI: paste your GLM Coding Plan API key

# 3. Load launcher functions (add to your shell profile for persistence)
source scripts/cc-launchers.sh
```

### Usage Options

**Direct Anthropic Pro (unchanged):**
```bash
cc-pro              # Use normal Claude Code with Pro/Max
# Inside Claude Code: /login once, then use /model claude-4-sonnet
```

**Via Gateway (switchable models):**
```bash
cc-sona             # Start on Anthropic Sonnet via gateway
# Inside Claude Code: /status shows base URL .../anthropic
# Switch models: /model zai/glm-4.5
# Switch back: /model anthropic/claude-4-sonnet

# Or launch directly on Z.AI
cc-zai              # Start directly on Z.AI GLM-4.5
```

### MCP (Archon + Others)

**Once you've added your MCP servers, they work the same in both modes (direct or gateway):**

```bash
# Add once, reuse everywhere
claude mcp add-json archon '{"type":"sse","url":"https://archon.example.com:8051/mcp"}'
claude mcp get archon

# Works in both cc-pro and cc-sona/cc-zai sessions
# Claude Code supports MCP; add once, reuse everywhere
```

### Gateway Management

```bash
# Start gateway
bash scripts/llm_gateway_up.sh

# Stop gateway  
bash scripts/llm_gateway_down.sh

# Check if running
docker ps | grep oos-bifrost
```

### OCI Security Notes

- **Default**: Gateway binds to `127.0.0.1:8080` (localhost only)
- **For remote access**: SSH tunneling recommended
- **If you must expose**: Add NSG ingress rule for TCP/8080 and open host firewall

### Keys & Safety

**Keep keys out of git.** Put API keys into Bifrost UI or a local `.env` that's already ignored by OOS:

```bash
# LLM Gateway (optional; store keys in Bifrost UI or local .env)
ZAI_API_KEY=your_zai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
# Optional future providers:
DEEPSEEK_API_KEY=
KIMI_API_KEY=
```

**Security:** Bifrost binds to `127.0.0.1` (localhost-only). If you must expose it on OCI, open an NSG ingress + host firewall, but localhost is safer.

---

### Other Documents

*   [Security Policy](SECURITY.md)
*   [Code Manifest](CODE_MANIFEST.md)
*   [License](LICENSE)