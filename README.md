# OOS (Organized Operational Setup)

**Your systematic thinking environment** - a brain extension system for consistent, structured development workflows.

OOS transforms how you approach any coding work, project, or idea by providing a unified environment that connects:
- **Consistent Platform** - Reliable development environment everywhere
- **Archon Integration** - Systematic project management
- **Agentic Thinking** - Future-ready for AI-powered workflows

---

## 🆘 New to OOS or Forgot How It Works?

**[📖 Start Here → Documentation Hub](DOCUMENTATION_HUB.md)**

**Quick links for forgetful humans:**
- **[What Even Is OOS?](GUIDES/WHAT_IS_OOS.md)** - The simple explanation
- **[5-Minute Quick Start](QUICK_SETUP_GUIDE.md)** - Copy-paste setup
- **[Emergency Refresher](GUIDES/EMERGENCY_REFRESHER.md)** - "I haven't used this in weeks"
- **[Quick Reference](QUICK_REFERENCE.md)** - One-page cheat sheet

**🚀 NEW: Full Stack AI Integration:**
- **[Current Status](CURRENT_STATUS.md)** - What's working now
- **[Full Stack Guide](docs/FULL_STACK_INTEGRATION.md)** - AI + RelayQ + Archon integration
- **[AI SDK](src/ai_provider.py)** - Multi-provider AI abstraction layer
- **[RelayQ Architecture](src/relayq_architecture.py)** - Distributed computing system

**🔐 NEW: Simple Secrets Management:**
- **[Final Simple Solution](docs/FINAL_SIMPLE_SOLUTION.md)** - Complete guide to the working security system
- **[GitHub Project Template](GITHUB_PROJECT_TEMPLATE.md)** - Template for future secure projects

**Quick links for AI Claude:**
- **[AI Reference](AI_REFERENCE.md)** - Technical implementation details

---

## Install - Universal Solution

**Works for both NEW and EXISTING projects** - one command fits all:

```bash
# NEW PROJECT: Create and setup in one step
cd ~/Documents  # or anywhere you want projects
oos create my-new-project

# EXISTING PROJECT: Add OOS to any current project
cd ~/path/to/existing/project
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash
```

**That's it. OOS is now ready.** 🎯

**Next steps (after restarting Claude Code):**
```bash
/dev check             # Validate and refresh commands automatically
/workflow complete     # See the systematic A→B→C→D workflow
```

### ✅ Update Compatibility
**OOS updates work seamlessly from any older version:**
```bash
# From any OOS installation, run:
/project update        # Auto-updates while preserving your work
```

**Guaranteed compatibility** - updates never break existing projects or configurations.

## Use - 11 Perfect Commands

**Your complete systematic development environment:**

```bash
# 🚀 Development Environment
/dev setup              # Start systematic development session
/dev check              # Validate development environment

# 🧪 Testing & Quality
/test scenarios         # Run user-acceptance testing
/fix auto               # Automatically fix code issues
/fix optimize           # Optimize for performance/tokens

# 🔄 Workflows & AI
/workflow complete      # Complete idea-to-completion workflow
/think clarify          # Clarify vague requirements and solve problems

# 🏗️ Projects & Infrastructure
/project create         # Create new systematic projects
/project update         # Update OOS from GitHub

# 🔐 Security & Authentication
/check security         # Run comprehensive security audit
/op status              # 1Password authentication

# 📚 Knowledge & Tasks
/archon research        # Search your knowledge base
/task start             # Start working on tasks

# ❓ Help & Discovery
/help                   # Get help and discover all commands
```

**That's it! 11 commands for everything you need.**

**🚀 Bonus: Full Stack AI Commands**
```bash
./bin/oos-full-stack "Your AI question here"                    # AI analysis
./bin/oos-full-stack "Analyze system" --command "df -h"         # AI + command execution
./bin/oos-full-stack "test" --test                             # Full integration demo
```

## What You Get

**Your Systematic Brain Environment:**
- **Consistent Mental Models** - Same thinking approach for every project
- **11 perfect slash commands** - Complete systematic workflow integration in Claude Code
- **AI SDK Integration** - Multi-provider AI with automatic fallback and cost tracking
- **RelayQ Architecture** - Distributed computing across MacMini, RPi4, and cloud nodes
- **Auto-Refresh System** - Commands stay current and validate themselves automatically
- **Project Management Layer** - Archon integration for structured work tracking
- **Quality Assurance** - Automated validation that supports your thinking
- **Bootstrap System** - Instantly create consistent thinking environments
- **Future-Ready Architecture** - Built for agentic thinking and AI collaboration

### 🔄 Auto-Refresh & Validation

OOS automatically maintains itself:

- **Startup Health Check** - `/startup-check` runs automatically to validate commands
- **Version Tracking** - Detects when OOS updates and refreshes commands
- **Rollback Protection** - Automatic backup and restore if updates fail
- **Validation Testing** - Every command is tested for functionality
- **Fuckup Detection** - Issues are caught and reported immediately

This ensures your slash commands always work or you get clear error messages about what's wrong.

### 🧠 How It Works as Your Brain Extension:

1. **Consistent Platform** - Same development environment, same mental models, everywhere
2. **Archon Integration** - Systematic project management that coordinates with your thinking
3. **Agentic Thinking Ready** - Future-proofed for AI-powered systematic workflows

## Commands

**Core Development:**
| Command | What it does |
|---------|--------------|
| `/start-coding` | Start systematic development session |
| `/modules [name]` | Run security/python/git modules |
| `/dev-setup` | Complete development environment validation |
| `/pre-commit` | Pre-commit validation workflow |
| `/update-oos` | Update your brain tools |
| `/create-project [template]` | Create new systematic project |

**AI-Powered Workflow:**
| Command | What it does |
|---------|--------------|
| `/help-me` | Smart context engineering help |
| `/optimize` | Optimize current context for token efficiency |
| `/auto-fix` | Automatically fix code consistency issues |
| `/smart-commit` | Generate intelligent commit messages |
| `/brain-dump` | Smart processing of rambling input |
| `/clarify` | Start clarification workflow |
| `/workflow` | Start structured workflow for complex tasks |

**Project Management:**
| Command | What it does |
|---------|--------------|
| `/archon-status` | Show current project status |
| `/archon-task-start` | Start working on tasks |
| `/archon-complete` | Mark tasks complete |
| `/archon-research` | Search knowledge base |

## Integrations

OOS includes automatic setup for development tools:

### Python Development Environment
Complete agentic Python development setup with modern tooling:

**Package Management:**
- **uv** - Unified Python package manager for fast, reliable dependency management
- **Python 3.12** with automatic environment management
- **Lock files** for reproducible builds across all environments

**Code Quality:**
- **Ruff** - Lightning-fast linting and formatting (replaces Black, isort, Flake8)
- **MyPy** - Static type checking for Python
- **Pre-commit hooks** - Automated quality checks before every commit

**Development Experience:**
- **VS Code Dev Containers** - Consistent development environment with Docker
- **GitHub Actions CI/CD** - Automated testing on Python 3.10, 3.11, 3.12
- **Pytest** with async support and coverage reporting
- **GitHub Copilot ready** configuration

**Quick Setup:**
```bash
# Complete agentic Python environment setup (paste entire block)
curl -LsSf https://astral.sh/uv/install.sh | sh && \
source $HOME/.cargo/env && \
uv init --python 3.12 . && \
uv add --dev pytest pytest-cov pytest-xdist ruff mypy pre-commit && \
uv sync && uv run pre-commit install
```

**Key Commands:**
```bash
uv sync                    # Install/update dependencies
uv run pytest            # Run tests with coverage
uv run ruff check .       # Lint code
uv run ruff format .      # Format code
uv run mypy src/          # Type check
uv run pre-commit run --all-files  # Run all quality checks
```

### 🔐 Simple Secrets Management (NEW!)
**When 1Password fails - use this simple system that actually works:**

```bash
./bin/setup-simple-security.sh
```

**Perfect for:**
- ✅ **AI agents** - Non-interactive secret access
- ✅ **Simple projects** - No complex interfaces
- ✅ **Reliable setup** - Works when 1Password doesn't

**Quick Start:**
```bash
# 1. Install the simple security system
./bin/setup-simple-security.sh

# 2. Add your API keys to .env file
nano .env
# Add your actual API keys here

# 3. Test it works
python3 bin/get-secrets.py list

# 4. Use in any new project
./bin/setup-new-project.sh ~/my-new-project
```

**AI Agent Integration:**
```python
from get_secrets import SimpleSecrets
secrets = SimpleSecrets()
api_key = secrets.get('OPENROUTER_API_KEY')
```

**GitHub Template Ready:**
- [**GITHUB_PROJECT_TEMPLATE.md**](GITHUB_PROJECT_TEMPLATE.md) - Complete template for future projects
- [**README_TEMPLATE.md**](README_TEMPLATE.md) - Clean README for new projects

### 1Password Integration
Long-term authentication without repeated signins:

```bash
./bin/setup-1password-service.sh
```

**Benefits:**
- ✅ Works for weeks/months automatically
- ✅ Works across all OOS installations
- ✅ Integrated with `/start-coding`

### 🤖 AI SDK Integration (NEW!)
**Multi-provider AI abstraction layer with fallback and load balancing:**

```bash
# Test AI integration
python3 src/ai_provider.py

# Use in your code
from src.ai_provider import ask_ai, get_ai_manager

response = await ask_ai("Your question here")
print(response)
```

**Features:**
- ✅ **Multiple Providers**: OpenRouter, OpenAI, Anthropic support
- ✅ **Automatic Fallback**: If one provider fails, tries others
- ✅ **Cost Estimation**: Track usage and costs across providers
- ✅ **Health Monitoring**: Real-time provider status checking
- ✅ **Model Presets**: Fast, balanced, and quality configurations

**Supported Models:**
- `nvidia/nemotron-nano-12b-v2-vl:free` - Free tier
- `amazon/nova-premier-v1` - Balanced performance
- `perplexity/sonar-pro-search` - Quality with search

### 🏗️ RelayQ Architecture (NEW!)
**Distributed computing system for MacMini, RPi4, and cloud nodes:**

```bash
# Test RelayQ functionality
python3 src/relayq_architecture.py

# Deploy tasks to nodes
from src.relayq_architecture import get_relayq_manager, DeploymentTask

manager = get_relayq_manager()
task = DeploymentTask(
    task_id="ai-training",
    command="python train_model.py",
    target_nodes=["macmini-server"],
    requirements=["ai-training", "compute"]
)
result = await manager.deploy_task(task)
```

**Node Types:**
- **MacMini**: Heavy compute, storage, AI training
- **RPi4**: Edge processing, IoT, sensor data
- **OCIVM**: Development, testing, orchestration

**Features:**
- ✅ **Auto Node Selection**: Chooses best node based on capabilities
- ✅ **Health Monitoring**: Real-time node status tracking
- ✅ **Distributed Tasks**: Run tasks across multiple nodes
- ✅ **SSH Management**: Secure remote execution
- ✅ **Load Balancing**: Distributes work based on node load

### 🔄 Full Stack Integration
**Complete AI + RelayQ + Archon workflow:**

```bash
# Run the full stack demo
./bin/oos-full-stack "Analyze system performance" --command "htop"
./bin/oos-full-stack "test" --test
```

**What It Does:**
1. **AI Analysis**: Processes your request with multiple AI providers
2. **Command Execution**: Runs system commands via RelayQ nodes
3. **Archon Sync**: Records results and updates project status
4. **Intelligent Routing**: Automatically selects best resources

### Archon Project Management
Task tracking and project coordination:

```bash
./bin/setup-archon.sh --setup
```

**Benefits:**
- ✅ Task tracking and management
- ✅ Project status visibility
- ✅ Knowledge base search
- ✅ Integrated with `/start-coding`

All tools are automatically detected and configured when you run `/start-coding`.

## 📚 Documentation

**🚀 NEW & IMPROVED - Start Here:**

**[📖 Documentation Hub](DOCUMENTATION_HUB.md)** - **START HERE** - Your complete guide to all documentation

**👋 For Beginners & Forgetful Users:**
- [**What Even Is OOS?**](GUIDES/WHAT_IS_OOS.md) - Simple explanation
- [**5-Minute Quick Start**](GUIDES/QUICK_START.md) - Copy-paste setup
- [**Emergency Refresher**](GUIDES/EMERGENCY_REFRESHER.md) - "I forgot everything"
- [**Quick Reference**](QUICK_REFERENCE.md) - One-page cheat sheet

**📋 Task System Guides:**
- [**Task System Basics**](GUIDES/TASK_SYSTEM_SIMPLE.md) - Just the essentials
- [**First Project Walkthrough**](GUIDES/FIRST_PROJECT.md) - Learn by doing
- [**Complete Task System**](GUIDES/TASK_SYSTEM_COMPLETE.md) - Become an expert
- [**Simple Troubleshooting**](GUIDES/TROUBLESHOOTING_SIMPLE.md) - When stuff breaks

**🛠️ Advanced Documentation:**
- [Complete Task System Guide](docs/TASK_SYSTEM_GUIDE.md) - Technical details
- [CLI Reference](docs/CLI_REFERENCE.md) - All commands
- [JSONL Import/Export](docs/JSONL_EXPORT_IMPORT_GUIDE.md) - Data management
- [Advanced Usage](docs/ADVANCED_USAGE_GUIDE.md) - Power user features
- [System Overview](docs/SYSTEM_OVERVIEW.md) - Architecture details

## Why This Exists

You need a systematic way to approach any coding work, project, or idea with consistent mental models. OOS transforms scattered development approaches into a unified thinking environment that works everywhere.

## License

MIT