# OOS (Organized Operational Setup)

**One-command project bootstrap and management system** for AI-powered development with Claude, Gemini, and Qwen.

🎯 **Quick Start:** `./bootstrap_enhanced.sh my-project /path/to/project` → Ready to code immediately.

---

## 🚀 What This Does

**Core Function**: Bootstrap new projects with proper AI CLI setup, secrets from 1Password, and comprehensive development tools.

**Key Features**:
- ✅ **One-command setup** - Project ready in seconds
- 🔐 **Secure secret management** - 1Password integration, zero secrets in git
- 🤖 **Multi-AI support** - Claude, Gemini, Qwen CLI runners
- 📊 **Professional tooling** - Monitoring, testing, security, performance
- 🔌 **Optional integrations** - Archon task management, web dashboard

---

## 📖 Complete Documentation

### **🎯 Start Here**
- **[System Overview](docs/SYSTEM_OVERVIEW.md)** - What everything actually does (READ FIRST!)
- **[Quick Start Guide](docs/USAGE_GUIDE.md)** - Step-by-step workflows for all scenarios

### **📚 Detailed Guides**
- **[Archon Integration](docs/ARCHON_INTEGRATION.md)** - Task management and project separation
- **[API Reference](docs/API_REFERENCE.md)** - Complete tool documentation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Fix common problems
- **[Testing Philosophy](docs/TESTING_PHILOSOPHY.md)** - Automated validation approach

---

## 🏗️ Project Structure

```
oos/
├── 📄 bootstrap_enhanced.sh      # Main setup script (START HERE)
├── 📁 bin/                       # Management tools
│   ├── 🔍 diagnose.sh           # Fix problems automatically  
│   ├── 📊 health_monitor.sh     # Continuous monitoring
│   ├── 🧪 run_tests.sh          # Test everything
│   ├── 🛡️ security_audit.sh     # Security scanning
│   ├── ⚡ performance_monitor.sh # Performance profiling
│   ├── 📁 template_manager.sh   # Project templates
│   ├── 🔑 key_rotator.sh        # API key management
│   └── 🔌 mcp_manager.sh        # MCP server management
├── 📁 .agents/                   # AI CLI runners
│   └── runners/
│       ├── 🤖 run_claude.sh     # Claude Code integration
│       ├── 🤖 run_gemini.sh     # Gemini CLI integration  
│       └── 🤖 run_qwen.sh       # Qwen integration
├── 📁 dashboard/                 # Web monitoring interface
├── 📁 templates/                 # Project templates
├── 📁 tests/                     # Test suite
└── 📁 docs/                      # Complete documentation
```

---

## 🚀 Usage Examples

### **Simple Project Setup**
```bash
# Create new project with AI tools configured
./bootstrap_enhanced.sh my-project /path/to/my-project

# That's it! Ready to code with Claude, Gemini, or Qwen
cd /path/to/my-project
.agents/runners/run_claude.sh
```

### **Professional Development**
```bash
# Setup with monitoring and validation
./bootstrap_enhanced.sh --security-hardened my-project /path/to/project
./bin/health_monitor.sh daemon     # Start continuous monitoring  
./bin/run_tests.sh all             # Validate everything works
./bin/security_audit.sh scan --fix # Security compliance
```

### **Template-Based Projects**
```bash
# Use built-in templates
./bin/template_manager.sh list                    # See available templates
./bin/template_manager.sh create web-app my-app   # Create from template
./bin/template_manager.sh create cli-tool my-cli  # CLI application
./bin/template_manager.sh create api-service api  # REST API service
```

---

## 🔧 Management Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| **[diagnose.sh](docs/API_REFERENCE.md#diagnostics-system)** | Fix problems automatically | `./bin/diagnose.sh --self-heal` |
| **[health_monitor.sh](docs/API_REFERENCE.md#health-monitoring)** | Continuous system monitoring | `./bin/health_monitor.sh daemon` |
| **[security_audit.sh](docs/API_REFERENCE.md#security-auditing)** | Security scanning & compliance | `./bin/security_audit.sh scan --fix` |
| **[performance_monitor.sh](docs/API_REFERENCE.md#performance-monitoring)** | Performance profiling | `./bin/performance_monitor.sh profile script.sh` |
| **[run_tests.sh](docs/API_REFERENCE.md#testing-framework)** | Comprehensive testing | `./bin/run_tests.sh all` |
| **[key_rotator.sh](docs/API_REFERENCE.md#key-rotation)** | API key management | `./bin/key_rotator.sh validate` |
| 🧠 **[development_guide.sh](bin/development_guide.sh)** | **Auto-learning from development** | `echo 'insight' \| ./bin/development_guide.sh update` |

---

## 🤖 AI Integration

### **Supported AI CLIs**
- **[Claude Code](https://claude.ai/code)** - Anthropic's official CLI
- **Gemini CLI** - Google's AI assistant  
- **Qwen CLI** - Alibaba's AI model

### **Runner Scripts**
- **`.agents/runners/run_claude.sh`** - Claude with proper environment
- **`.agents/runners/run_gemini.sh`** - Gemini with secret management  
- **`.agents/runners/run_qwen.sh`** - Qwen integration

Each runner loads secrets from 1Password, sets up the environment, and launches the AI CLI with proper configuration.

---

## 🔐 Security Features

### **Secret Management**
- 🔐 **1Password integration** - Secrets never stored in git
- 🔄 **Automatic key rotation** - Smart failover for API keys  
- 🛡️ **Secret detection** - Prevent accidental commits
- 🔒 **Environment encryption** - Encrypt sensitive files

### **Security Scanning**
- 🔍 **Exposed secret detection** - Scan for leaked credentials
- 📋 **File permission validation** - Ensure secure access controls
- 📊 **Compliance reporting** - Generate security audit reports
- 🔧 **Auto-remediation** - Fix security issues automatically

---

## 🔌 Optional Integrations

### **Archon MCP Task Management**
Connect to [Archon MCP server](docs/ARCHON_INTEGRATION.md) for advanced project and task management:
- 📋 **Project isolation** - Separate tasks per project
- 📝 **Task tracking** - From todo → doing → review → done
- 📚 **Document management** - Specifications, designs, notes
- 📊 **Version control** - Track project evolution

### **Web Dashboard**
Real-time monitoring interface at `http://localhost:5000`:
- 📊 **System status** - Live health monitoring
- 🔍 **Performance metrics** - Resource usage and timing
- 🛡️ **Security alerts** - Real-time issue notifications  
- 📋 **Project management** - CRUD operations via web UI

---

## ❓ FAQ

<details>
<summary><strong>Do I need all these tools?</strong></summary>

**No!** Start with just:
- `bootstrap_enhanced.sh` (project setup)
- `bin/diagnose.sh` (when things break)

Add other tools as needed. See [System Overview](docs/SYSTEM_OVERVIEW.md) for guidance.
</details>

<details>
<summary><strong>Can I use this without Archon?</strong></summary>

**Yes!** OOS works completely independently. Archon is optional task management - see [Archon Integration](docs/ARCHON_INTEGRATION.md).
</details>

<details>
<summary><strong>What's the difference between bootstrap.sh and bootstrap_enhanced.sh?</strong></summary>

**Enhanced version** has error checking, rollback, validation, and comprehensive diagnostics. Use `bootstrap_enhanced.sh`.
</details>

<details>
<summary><strong>Is this overkill for personal projects?</strong></summary>

**Maybe!** For simple use, just run `bootstrap_enhanced.sh` and ignore everything else. The system is modular.
</details>

<details>
<summary><strong>How do I ensure project separation in Archon?</strong></summary>

Each project gets a unique `ARCHON_PROJECT_ID` in its `.env` file. See [Archon Integration Guide](docs/ARCHON_INTEGRATION.md).
</details>

---

## 🆘 Getting Help

### **Quick Fixes**
```bash
# System broken? Try auto-healing
./bin/diagnose.sh --self-heal

# Can't access 1Password?
eval "$(op signin)"

# Archon not connecting?
curl -I http://localhost:8051/mcp
```

### **Documentation**
- 🎯 **[System Overview](docs/SYSTEM_OVERVIEW.md)** - Understand what you have
- 📖 **[Usage Guide](docs/USAGE_GUIDE.md)** - Complete workflows  
- 🔧 **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Fix common problems
- 📚 **[API Reference](docs/API_REFERENCE.md)** - Complete tool docs

### **Support**
- 📋 **Issues**: [GitHub Issues](https://github.com/Khamel83/oos/issues)
- 🔍 **Diagnostics**: `./bin/diagnose.sh --collect-logs`
- 📊 **System Status**: `./bin/health_monitor.sh check`

---

## 🎯 What Makes OOS Different

**Traditional Setup**: Install tools → Configure environment → Setup secrets → Debug issues → Start coding

**OOS Setup**: `./bootstrap_enhanced.sh project-name /path` → Start coding

**Key Benefits**:
- ✅ **Zero manual configuration** - Everything automated
- 🔐 **Security by default** - Proper secret management
- 🤖 **AI-ready** - Pre-configured AI CLI integration  
- 📊 **Production tools** - Monitoring, testing, security built-in
- 🔧 **Self-healing** - Automatic problem detection and fixes

---

**Ready to get started?** → **[Quick Start Guide](docs/USAGE_GUIDE.md)**