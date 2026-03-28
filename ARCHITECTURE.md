# OOS Architecture (For Developers)

This document is for developers working on OOS itself. **Users don't need to read this.**

## System Overview

OOS is a three-tier development environment system:

```
┌─────────────────────────────────────────┐
│  bin/oos (Main Entry Point)            │
│  - Routes commands to appropriate tier  │
│  - Checks tier availability             │
│  - Shows unified help                   │
└──────────┬──────────────────────────────┘
           │
    ┌──────┴──────────────────┐
    │                          │
    ▼                          ▼
┌─────────────┐    ┌──────────────────────┐
│  Core Tier  │    │  Enhanced Tier       │
│  (Always)   │    │  (Needs API Keys)    │
│             │    │                      │
│  - Tasks    │    │  - AI Features       │
│  - Dev      │    │  - Advanced Search   │
│  - Projects │    └──────────────────────┘
│  - Tests    │              │
│  - Fixes    │              ▼
│  - Checks   │    ┌──────────────────────┐
└─────────────┘    │  Advanced Tier       │
                   │  (Needs Archon)      │
                   │                      │
                   │  - Knowledge Base    │
                   │  - Distributed Comp  │
                   └──────────────────────┘
```

## Directory Structure

```
oos/
├── bin/
│   ├── oos                    # Main entry point
│   ├── oos-core/              # Core tier implementations
│   │   ├── task.sh
│   │   ├── dev.sh
│   │   ├── project.sh
│   │   ├── test.sh
│   │   ├── fix.sh
│   │   └── check.sh
│   ├── oos-enhanced/          # Enhanced tier
│   │   └── ai.sh
│   ├── oos-advanced/          # Advanced tier
│   │   └── archon.sh
│   └── oos-internal/          # Shared utilities
│
├── lib/
│   ├── oos-common.sh          # Shared functions, colors
│   └── oos-tier-detection.sh # Feature detection
│
├── src/
│   ├── oos_task_system/       # Python task system
│   ├── ai_provider.py         # AI integration
│   ├── learning_system.py     # Pattern learning
│   ├── token_optimization.py  # Context management
│   └── ...
│
├── .claude/
│   └── commands/              # Slash commands (thin wrappers)
│
├── .oos/
│   ├── tasks/                 # Task database
│   └── logs/                  # System logs
│
├── QUICKSTART.md              # 5-minute setup
├── USAGE.md                   # Common tasks
├── REFERENCE.md               # All commands
├── SETUP.md                   # Optional features
└── ARCHITECTURE.md            # This file
```

## Tier System

### Core Tier (lib/oos-tier-detection.sh)

Always available. No external dependencies.

**Detection:**
- Checks for OOS directories
- Ensures task database accessible

**Commands:**
- All in `bin/oos-core/`
- Bash scripts that wrap Python/existing tools
- Fail gracefully with helpful messages

### Enhanced Tier

Requires API keys for AI providers.

**Detection:**
```bash
# Checks .env for:
OPENROUTER_API_KEY=sk-*
OPENAI_API_KEY=sk-*
ANTHROPIC_API_KEY=sk-*
```

**Commands:**
- In `bin/oos-enhanced/`
- Wrap `src/ai_provider.py` and related

### Advanced Tier

Requires external Archon server.

**Detection:**
```bash
# Checks .env for ARCHON_URL
# Pings: ${ARCHON_URL}/api/health
```

**Commands:**
- In `bin/oos-advanced/`
- Wrap Archon MCP integration

## Entry Point Flow

```bash
# User types:
oos task create "My task"

# bin/oos:
1. Sources lib/oos-common.sh (functions, colors)
2. Sources lib/oos-tier-detection.sh (feature checks)
3. Parses command: "task"
4. Routes to: bin/oos-core/task.sh create "My task"

# bin/oos-core/task.sh:
1. Validates arguments
2. Calls: uv run python -m src.oos_task_system.cli create --title "My task"
3. Formats output
4. Returns exit code
```

## Adding New Commands

### Core Command

1. Create `bin/oos-core/newcmd.sh`
2. Follow pattern of existing scripts
3. Add case to `bin/oos` main switch
4. Update REFERENCE.md
5. Add tests

### Enhanced/Advanced Command

1. Create in appropriate tier directory
2. Use `oos_require_tier` to check availability
3. Provide helpful error if tier unavailable
4. Add to `bin/oos` switch with tier check

## Python Integration

### Task System

```python
# src/oos_task_system/
# - SQLite database at .oos/tasks/tasks.db
# - CLI in cli.py
# - Models in models.py
```

**Accessed via:**
```bash
uv run python -m src.oos_task_system.cli <command>
```

### AI Provider

```python
# src/ai_provider.py
# - Multi-provider abstraction
# - OpenRouter, OpenAI, Anthropic
# - Cost tracking
```

### Learning System

```python
# src/learning_system.py
# - Pattern detection
# - Usage learning
# - SQLite at ~/.oos/learning.db
```

## Slash Commands

Located in `.claude/commands/*.md`

**Pattern:**
```markdown
---
description: "Command description"
allowed-tools: Bash
---

oos <command> ${ARGUMENTS}
```

All slash commands are thin wrappers that call `oos` CLI.

## Testing

```bash
# Unit tests
oos test run

# Integration tests
oos test run tests/integration/

# User scenarios
oos test scenarios
```

## Installation

`install.sh` handles two contexts:

1. **OOS Repository:** Full dev environment
   - Runs `uv sync`
   - Installs all dependencies
   - Creates .env template

2. **User Project:** Core tools only
   - Downloads bash scripts
   - Downloads slash commands
   - No Python dependencies

## Configuration

All configuration in `.env`:

```bash
# Core (no config needed)

# Enhanced
OPENROUTER_API_KEY=...
OPENAI_API_KEY=...

# Advanced
ARCHON_URL=https://archon.khamel.com
ARCHON_API_KEY=...
```

## Extending OOS

### Adding a Feature

1. Determine tier (Core/Enhanced/Advanced)
2. Implement in appropriate location
3. Update tier detection if needed
4. Add command wrapper
5. Update documentation
6. Add tests

### Migration from Old System

Old scripts still exist in `bin/`. New `oos` CLI wraps or replaces them.

**Strategy:**
- Keep old scripts temporarily
- Redirect to new CLI where possible
- Deprecate over time

## Development Workflow

```bash
# Make changes
vim bin/oos-core/task.sh

# Test locally
./bin/oos task list

# Run tests
./bin/oos test run

# Update docs
vim REFERENCE.md

# Commit
git add -A
git commit -m "feat: description"
```

## Key Design Decisions

### Why Bash + Python?

- **Bash:** Fast, available everywhere, good for orchestration
- **Python:** Rich libraries, good for complex logic
- **Best of both:** Use right tool for each job

### Why Three Tiers?

- **Clarity:** User knows what works without setup
- **Graceful degradation:** Core always works
- **Progressive enhancement:** Enable features as needed

### Why Single Entry Point?

- **Discoverability:** One command to remember
- **Consistency:** Uniform interface
- **Auto-completion:** Easy to implement

### Why Not X?

**Why not Go/Rust single binary?**
- Need Python for AI/ML libraries
- Bash already installed everywhere
- Flexibility to change implementations

**Why not all Python?**
- Slower startup
- More dependencies
- Bash better for some tasks

## Troubleshooting Development

### Command not found

```bash
# Check PATH
echo $PATH

# Check executable
ls -la bin/oos
chmod +x bin/oos
```

### Tier detection wrong

```bash
# Debug tier detection
bash -x lib/oos-tier-detection.sh
oos_show_status
```

### Python errors

```bash
# Check environment
oos dev check

# Rebuild
rm -rf .venv
uv sync
```

## Contributing

See main README.md for contribution guidelines.

Key principles:
- Keep it simple
- Usage-first thinking
- Test everything
- Document as you go

---

**For user documentation, see:**
- [QUICKSTART.md](QUICKSTART.md)
- [USAGE.md](USAGE.md)
- [REFERENCE.md](REFERENCE.md)
