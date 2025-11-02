# OOS Changelog

## [1.1.0] - 2024-11-02

### 🔐 Simple Secrets Management System
**When 1Password fails - this actually works**

#### ✨ Features
- **Simple .env-based Security**: Text-file secrets management that works reliably
- **AI Agent Integration**: Non-interactive secret access for AI agents
- **GitHub Project Template**: Complete template for future secure projects
- **Automated Security**: Pre-commit hooks and git protection against API key exposure
- **Project Copy System**: Easy secrets sharing between projects

#### 🔧 Tools Added
- `bin/setup-simple-security.sh` - Install the simple security system
- `bin/get-secrets.py` - AI agent secrets client
- `bin/setup-new-project.sh` - Copy secrets to new projects
- `GITHUB_PROJECT_TEMPLATE.md` - Complete GitHub repository template
- `README_TEMPLATE.md` - Clean README template for new projects

#### 🛡️ Security Benefits
- **No more API key commits** - .env files are automatically protected
- **AI agent ready** - Simple Python interface for non-interactive access
- **Zero complexity** - Just edit text files, no complex interfaces
- **Industry standard** - Uses GitGuardian and detect-secrets best practices

#### 📚 Documentation
- `docs/FINAL_SIMPLE_SOLUTION.md` - Complete solution guide
- Updated README.md with simple secrets management section
- GitHub project template for easy future project setup

### 🤖 AI SDK Integration
- **Multi-provider AI abstraction** - OpenRouter, OpenAI, Anthropic support
- **Automatic fallback system** - If one provider fails, tries others automatically
- **Cost estimation and tracking** - Monitor usage across providers
- **Health monitoring** - Real-time provider status checking
- **Model presets** - Fast, balanced, and quality configurations
- **Supported models** - Including free tier options and premium models

### 🏗️ RelayQ Architecture
- **Distributed computing system** - MacMini, RPi4, and cloud node support
- **Intelligent node selection** - Auto-selects best node based on capabilities
- **Health monitoring** - Real-time node status and load tracking
- **Distributed task execution** - Run tasks across multiple nodes
- **SSH management** - Secure remote execution with key-based auth
- **Load balancing** - Distributes work based on node capabilities and load

### 🔄 Full Stack Integration
- **Complete workflow** - AI + RelayQ + Archon working together
- **Command-line interface** - `./bin/oos-full-stack` for easy access
- **Intelligent routing** - Automatically selects best resources for tasks
- **Real-time synchronization** - Results sync to Archon automatically

### 🔧 Bug Fixes
- **Fixed deprecation warnings** - Removed deprecated model references from slash commands
- **Clean command execution** - All `/fix` commands now work without warnings
- **Improved ZAI integration** - Proper GLM model configuration

## [1.0.0] - 2024-09-27

### 🎉 Initial Production Release

#### ✨ Features
- **Universal Search System**: 4 free search engines (DuckDuckGo, Wikipedia, GitHub, Stack Overflow)
- **Perplexity Pro Integration**: Optional enhanced search with cost controls
- **Google Search Cost Fixer**: Universal tool to replace expensive Google APIs
- **Smart Slash Commands**: 8 productivity commands for Claude Code
- **Universal Installer**: One-command installation for any project
- **Cost Management**: Built-in usage tracking and safety controls
- **Project Detection**: Automatic detection of Node.js, Python, Rust, Go, etc.

#### 🔧 Tools Included
- `oos search "query"` - Command-line search
- `/smart-commit` - Generate commit messages
- `/optimize` - Optimize context for tokens
- `/help-me` - Smart context engineering
- `/auto-fix` - Fix code consistency
- `/clarify` - Clarify vague requests
- `/workflow` - Structured workflows
- `/doc-check` - Documentation completeness

#### 💰 Cost Benefits
- **Google Search Replacement**: $87/month → $0.00/month
- **Perplexity Pro**: $5/month for enhanced search (optional)
- **Token Optimization**: Up to 40% context reduction

#### 🎯 Supported Projects
- Any Git repository
- Node.js, Python, Rust, Go, PHP, Ruby, Java projects
- Claude Code integrated projects
- Existing OOS installations

#### 🛡️ Security Features
- No API keys required for basic functionality
- Secure credential management
- Cost limit enforcement
- Usage monitoring and alerts

### 🔧 Technical Details
- Drop-in replacement for expensive APIs
- Modular architecture - use what you need
- Self-documenting tools and commands
- Comprehensive error handling
- Automatic conflict resolution

### 📦 Installation
```bash
curl -sSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash
```

### 🎯 What's Next
- Domain setup: `install.oos.dev`
- Package manager integration
- Advanced workflow automation
- Enterprise features