# OOS (Organized Operational Setup)

**Your systematic thinking environment** - a brain extension system for consistent, structured development workflows.

OOS transforms how you approach any coding work, project, or idea by providing a unified environment that connects:
- **Consistent Platform** - Reliable development environment everywhere
- **Archon Integration** - Systematic project management
- **Agentic Thinking** - Future-ready for AI-powered workflows

## Install

Run this in **any project directory** (new or existing):

```bash
bash <(curl -s https://raw.githubusercontent.com/Khamel83/oos/master/install.sh)
```

**Then restart Claude Code** to activate all slash commands.

**After restarting, run:**
```bash
/startup-check         # Validate and refresh commands automatically
/complete-workflow plan # See the systematic A→B→C→D workflow
```

## Use

```bash
/start-coding          # Start systematic development session
/complete-workflow     # Complete idea-to-completion workflow A→B→C→D
/idea-to-done          # Alias for complete workflow
/validate              # Run comprehensive OOS validation
/ruat                  # Recursive User-Acceptance Testing
/provision             # AI-powered infrastructure provisioning
/screenshot            # Take screenshot and analyze with Claude
/oos-refresh           # Auto-refresh slash commands and validate
/startup-check         # Startup health check (run automatically)
/help-me               # Smart context engineering help
/pre-commit            # Run systematic checks before committing
/smart-commit          # Generate intelligent commit messages
```

## What You Get

**Your Systematic Brain Environment:**
- **Consistent Mental Models** - Same thinking approach for every project
- **20+ slash commands** - Complete systematic workflow integration in Claude Code
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

### 1Password Integration
Long-term authentication without repeated signins:

```bash
./bin/setup-1password-service.sh
```

**Benefits:**
- ✅ Works for weeks/months automatically
- ✅ Works across all OOS installations
- ✅ Integrated with `/start-coding`

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

Both tools are automatically detected and configured when you run `/start-coding`.

## Documentation

- [Quick Start](QUICK_START.md) - 2 minute setup for your systematic environment
- [User Guide](USER_READY_SETUP.md) - What works right now
- [System Vision](OOS_2.0_VISION.md) - Brain extension capabilities
- [Personal Ops](docs/PERSONAL_OPS_VISION.md) - Systematic thinking workflows
- [Development Ethos](HUMAN_AI_DEVELOPMENT_ETHOS.md) - Human+AI partnership

## Why This Exists

You need a systematic way to approach any coding work, project, or idea with consistent mental models. OOS transforms scattered development approaches into a unified thinking environment that works everywhere.

## License

MIT