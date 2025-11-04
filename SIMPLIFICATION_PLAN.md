# OOS Simplification Plan - From Complex to Complicated

## The Problem Statement

**Current State:**
- 120 shell scripts
- 141 documentation files  
- 11 slash commands (down from 45!)
- Multiple ways to invoke the same thing
- Docs explain WHAT it is, not HOW to use it
- User experience: "always just not like working somehow"

**Root Issue:** Not complex architecture - confusing **usage patterns**

```bash
# Current confusion:
./bin/oos-task list              # Sometimes this
uv run python -m ...             # Sometimes this
/dev check                       # Sometimes this
./bin/claude-dev.sh check        # Wait, or this?
```

## Core Insight: Complicated vs Complex

**Complicated (GOOD):** Many simple pieces, each clear
- Linux tools: `ls`, `grep`, `sed` - each does one thing
- You can learn them one at a time
- Clear when to use which

**Complex (BAD):** Pieces interact in confusing ways
- Current OOS: Is `/dev` a command? A script? Both?
- When do I need `uv run`? When don't I?
- What works standalone? What needs setup?

## Simplification Strategy

### Principle 1: One Entry Point, Clear Pattern

**Before:**
```bash
./bin/oos-task list
/dev check
uv run python -m src.oos_task_system.cli list
./bin/claude-dev.sh check
```

**After:**
```bash
oos task list          # All commands follow: oos <noun> <verb>
oos dev check
oos project create
oos help               # Clear help for everything
```

### Principle 2: Three Clear Tiers

**Tier 1: CORE (Always Works, No Setup)**
- Project scaffolding
- Task tracking (local SQLite)
- Development workflows
- Code checks

**Tier 2: ENHANCED (Needs API Keys)**
- AI-powered features
- Advanced search
- Auto-completion

**Tier 3: ADVANCED (Needs External Services)**
- Archon integration
- Distributed computing
- 1Password integration

**Key:** System clearly tells you what tier you're in and what you can do.

### Principle 3: Usage-First Documentation

**Before (WHAT it is):**
> "OOS is a brain extension system with Archon integration providing systematic thinking environment..."

**After (HOW to use):**
```bash
# Start your first project (2 minutes)
oos project create my-app
cd my-app
oos dev setup

# Track what you're building (30 seconds)
oos task create "Build user auth"
oos task start

# Check your work (10 seconds)
oos test run
oos check security

# Done. That's 90% of daily usage.
```

## Detailed Implementation Plan

### Phase 1: Single CLI Entry Point

**Create: `bin/oos` (main entry point)**

```bash
#!/usr/bin/env bash
# Single entry point for ALL OOS functionality

case "$1" in
  task)    shift; oos_task "$@" ;;
  dev)     shift; oos_dev "$@" ;;
  test)    shift; oos_test "$@" ;;
  check)   shift; oos_check "$@" ;;
  fix)     shift; oos_fix "$@" ;;
  project) shift; oos_project "$@" ;;
  help)    shift; oos_help "$@" ;;

  # Enhanced tier (checks for requirements)
  ai)      shift; oos_ai "$@" ;;

  # Advanced tier (checks for services)
  archon)  shift; oos_archon "$@" ;;

  *)       oos_help ;;
esac
```

**Benefits:**
- One command to remember: `oos`
- Consistent pattern: `oos <area> <action>`
- Auto-completion friendly
- Clear error messages when tier requirements not met

**Changes:**
- Create `bin/oos` master script
- Refactor existing scripts to be called by it
- Remove duplicate wrappers
- Keep slash commands but make them call `oos` internally

### Phase 2: Tier Detection & Clear Messaging

**Create: `lib/oos-tier-detection.sh`**

```bash
detect_available_features() {
  echo "OOS Feature Detection"
  echo "===================="

  # Tier 1: Core (always available)
  echo "✅ CORE: Task tracking, project management, dev tools"

  # Tier 2: Enhanced
  if has_api_keys; then
    echo "✅ ENHANCED: AI features, advanced search"
  else
    echo "⚪ ENHANCED: Add API keys to enable (see: oos help enhanced)"
  fi

  # Tier 3: Advanced
  if archon_available; then
    echo "✅ ADVANCED: Archon knowledge base, distributed computing"
  else
    echo "⚪ ADVANCED: Archon not configured (see: oos help archon)"
  fi
}
```

**On first run:**
```bash
$ oos
Welcome to OOS!

Available features:
  ✅ CORE: Project management, task tracking, dev tools
  ⚪ ENHANCED: (Add API keys to enable)
  ⚪ ADVANCED: (External services not configured)

Try: oos project create my-app

Get help: oos help
Enable more: oos help setup
```

### Phase 3: Radical Documentation Simplification

**Replace 141 files with 5 core docs:**

**1. QUICKSTART.md (5 minutes to value)**
```markdown
# Start Using OOS (5 Minutes)

## Install
curl -fsSL https://oos.dev/install | bash

## Create Your First Project
oos project create my-app
cd my-app

## Track Your Work
oos task create "Build the thing"
oos task start

## Done. You're using OOS.

Next: Run `oos help` to see everything you can do.
```

**2. USAGE.md (Common tasks, exact commands)**
```markdown
# Common Tasks

## Starting a New Project
oos project create project-name
cd project-name
oos dev setup

## Daily Development
oos task list               # What am I working on?
oos task start <id>         # Start a task
oos dev check               # Environment healthy?
oos test run                # Run tests
oos check security          # Security scan

## When You Need Help
oos help                    # All commands
oos help <command>          # Specific command help
oos help setup              # Enable more features
```

**3. REFERENCE.md (Complete command list)**
```markdown
# Command Reference

## oos task
  list              List all tasks
  create <title>    Create new task
  start <id>        Start working on task
  done <id>         Mark task complete

## oos dev
  setup             Setup development environment
  check             Validate environment

[etc - comprehensive but scannable]
```

**4. SETUP.md (Enabling enhanced features)**
```markdown
# Setup Optional Features

## You Have: Core Features ✅
Already working: task tracking, project management, dev tools

## Enable: AI Features
1. Get API key from openrouter.ai
2. Add to .env: `OPENROUTER_API_KEY=your-key`
3. Run: `oos ai test`

Now you can: `oos ai analyze`, `oos ai commit-message`, etc.

## Enable: Archon Integration
[Clear steps for this optional advanced feature]
```

**5. ARCHITECTURE.md (For developers/contributors only)**
```markdown
# OOS Architecture

[Current detailed docs go here]
[Most users never need this]
```

**Archive everything else to `docs/archive/`**

### Phase 4: Consolidate Scripts

**Current mess: 120 scripts**

**After consolidation:**

```
bin/
  oos                    # Main entry point (new)
  oos-core/              # Core tier implementations
    task.sh
    dev.sh
    test.sh
    check.sh
    fix.sh
    project.sh
  oos-enhanced/          # Enhanced tier
    ai.sh
  oos-advanced/          # Advanced tier
    archon.sh
  oos-internal/          # Shared utilities
    detect-tier.sh
    install-deps.sh
    colors.sh
```

**Delete:**
- Duplicate wrappers
- Old migration scripts
- Unused setup scripts
- Scripts that just call other scripts

**Consolidate:**
- `claude-dev.sh` + `oos-dev.sh` + dev modules → `oos-core/dev.sh`
- All task scripts → `oos-core/task.sh` (wraps Python CLI)

### Phase 5: Fix Installation Once and For All

**Create: `install.sh` (actually simple)**

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Installing OOS..."

# Detect context
if [[ -f "pyproject.toml" ]] && grep -q "oos" pyproject.toml; then
  CONTEXT="oos-repo"
else
  CONTEXT="user-project"
fi

case "$CONTEXT" in
  oos-repo)
    echo "📦 OOS Repository: Full installation"
    install_oos_dev_environment
    ;;
  user-project)
    echo "🚀 User Project: Core features installation"
    install_oos_to_project
    ;;
esac

# Test installation
oos help > /dev/null && echo "✅ Installation successful!"

# Show what's available
oos status

echo ""
echo "Quick start:"
echo "  oos help              # See all commands"
echo "  oos project create    # Start a new project"
echo "  oos help setup        # Enable more features"
```

### Phase 6: Slash Commands Integration

**Keep slash commands (users like them) but simplify:**

**.claude/commands/dev.md:**
```markdown
---
description: "🔧 Development environment management"
allowed-tools: Bash
---

oos dev ${ARGUMENTS}
```

**That's it.** No complex scripts, just call the `oos` CLI.

All 11 slash commands become thin wrappers around `oos`.

### Phase 7: Usage Examples (Not Feature Lists)

**Create: `examples/` directory**

```
examples/
  01-new-project.md          # "I want to start a new project"
  02-track-tasks.md          # "I want to track my work"
  03-daily-workflow.md       # "What do I run each day?"
  04-enable-ai.md            # "I want AI features"
  05-team-setup.md           # "My team wants to use OOS"
```

**Each example:**
- Problem statement
- Exact commands to run
- What success looks like
- What to do if it fails

**Example format:**
```markdown
# I Want to Track My Tasks

## The Commands
\`\`\`bash
oos task create "Build authentication"
oos task create "Add database"
oos task start auth-task-id
# Work on task...
oos task done auth-task-id
\`\`\`

## What You'll See
[screenshot or output]

## Troubleshooting
- If "command not found": Installation failed, run install again
- If tasks don't persist: Database not initialized, run \`oos dev setup\`
```

## Implementation Checklist

**Phase 1: CLI Entry Point**
- [ ] Create \`bin/oos\` master script
- [ ] Implement command routing
- [ ] Add auto-completion support
- [ ] Test all commands work through new entry point

**Phase 2: Tier System**
- [ ] Create tier detection library
- [ ] Add "oos status" command (show available features)
- [ ] Clear messages when features unavailable
- [ ] Test degradation when features missing

**Phase 3: Documentation**
- [ ] Write QUICKSTART.md (5 min to value)
- [ ] Write USAGE.md (common tasks)
- [ ] Write REFERENCE.md (all commands)
- [ ] Write SETUP.md (optional features)
- [ ] Move current docs to ARCHITECTURE.md
- [ ] Archive old docs to docs/archive/

**Phase 4: Script Consolidation**
- [ ] Create oos-core/, oos-enhanced/, oos-advanced/ structure
- [ ] Consolidate duplicate scripts
- [ ] Delete unused scripts
- [ ] Update all internal calls

**Phase 5: Installation**
- [ ] Rewrite install.sh (context-aware)
- [ ] Add post-install verification
- [ ] Show feature availability after install
- [ ] Test both contexts (oos-repo and user-project)

**Phase 6: Slash Commands**
- [ ] Update all .claude/commands/*.md to call \`oos\`
- [ ] Remove complex logic from slash commands
- [ ] Test all slash commands work
- [ ] Verify Claude Code integration

**Phase 7: Usage Examples**
- [ ] Create examples/ directory
- [ ] Write 5 core usage examples
- [ ] Add troubleshooting to each
- [ ] Include expected output

**Phase 8: Testing & Validation**
- [ ] Test fresh install on new project
- [ ] Test each tier works independently
- [ ] Test upgrade from current version
- [ ] Get user feedback on clarity

## Success Metrics

**Before:**
- "Always just not like working somehow"
- User abandons after crashes
- Needs docs to do basic tasks
- Unclear what works vs needs setup

**After:**
- Install works first time
- \`oos help\` is sufficient for 80% of use cases
- Clear which features available
- Graceful degradation when things missing

**Validation:**
- New user can create project in 5 minutes without docs
- \`oos status\` clearly shows what's available
- Error messages tell user exactly what to do
- No "ModuleNotFoundError" crashes

## Migration Strategy

**For existing users:**

```bash
# Backup current setup
cp -r ~/.config/oos ~/.config/oos.backup

# Pull latest
git pull

# Run migration
oos migrate

# Verify
oos status
```

**For new users:**
Just run install, nothing to migrate.

## Timeline Estimate

- Phase 1 (CLI): 2-3 hours
- Phase 2 (Tiers): 1-2 hours
- Phase 3 (Docs): 3-4 hours
- Phase 4 (Scripts): 2-3 hours
- Phase 5 (Install): 1-2 hours
- Phase 6 (Slash): 1 hour
- Phase 7 (Examples): 2-3 hours
- Phase 8 (Testing): 2-3 hours

**Total: 14-21 hours of focused work**

**Can be done in phases, each independently valuable**

## Risk Assessment

**Low Risk:**
- Documentation changes (can revert easily)
- New \`oos\` CLI (additive, doesn't break existing)
- Script consolidation (can keep old ones temporarily)

**Medium Risk:**
- Changing slash commands (but simple fallback)
- Installation changes (but we can detect and migrate)

**Mitigation:**
- Keep old scripts during transition
- Version the new structure (oos v2)
- Provide rollback path
- Extensive testing before release

## Open Questions for Discussion

1. **Naming:** Keep "oos" or something more obvious like "ops" or "dev"?

2. **Tier 2/3 names:** "Enhanced" and "Advanced" clear enough?

3. **Breaking changes:** Okay to require users to use \`oos\` command instead of direct script calls?

4. **Slash commands:** Keep all 11 or reduce to core 5-6?

5. **Python CLI:** Keep as-is or rebuild to match bash patterns?

6. **Installation:** Single script or \`brew install oos\` style?

## What This Achieves

**Current OOS:**
- Powerful but confusing
- Rich features but hard to discover
- Works great once you know it
- High abandonment rate

**After Simplification:**
- Still powerful, now clear
- Features easy to discover
- Works great immediately
- High adoption rate

**Key Insight:**
Not reducing functionality - reducing **cognitive load**

User doesn't need to know:
- Which script to call
- When to use uv run
- What needs setup vs what works
- Where to find docs

They just need to know: \`oos <what-i-want-to-do>\`

---

## Summary for Approval

**Problem:** OOS is complicated (many pieces) but feels complex (confusing to use)

**Solution:**
1. Single \`oos\` CLI entry point
2. Three clear tiers (Core/Enhanced/Advanced)
3. Usage-first docs (how to do things, not what things are)
4. Radical script consolidation (120 → ~10)
5. Honest, helpful error messages

**Result:** Same power, 10x clearer to use

**Ready to approve and implement?**
