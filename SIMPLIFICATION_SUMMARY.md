# OOS Simplification - Executive Summary

## The Core Problem

**You said it best:** "always just not like working somehow"

**Why?** Not architectural complexity - **usage complexity**

```bash
# Today - Which is right?
./bin/oos-task list
uv run python -m ...
/dev check
```

User has to know: Which script? When uv run? What needs setup?

## The Solution: Three Simple Changes

### 1. One Entry Point

**Before:** 120 scripts, multiple invocation patterns
**After:** One command - `oos`

```bash
oos task list          # Clear pattern
oos dev check          # Always the same
oos project create     # Easy to remember
```

### 2. Three Clear Tiers

**CORE (always works):** Tasks, projects, dev tools
**ENHANCED (needs API key):** AI features
**ADVANCED (needs services):** Archon, distributed compute

System tells you what you have: `oos status`

### 3. Usage-First Docs

**Before:** "OOS is a brain extension system with..."
**After:** 

```bash
oos project create my-app    # 2 min
oos task create "Build it"   # 30 sec
oos test run                 # 10 sec
```

Five docs replace 141:
- QUICKSTART.md (5 min to working)
- USAGE.md (common tasks)
- REFERENCE.md (all commands)
- SETUP.md (optional features)
- ARCHITECTURE.md (developers only)

## What Changes for Users

### Install Experience

**Before:**
```bash
./install.sh
# "✅ Installation Complete!"
oos task list
# ModuleNotFoundError: No module named 'click'
# WTF?
```

**After:**
```bash
./install.sh
# Installation complete
# Testing... ✅ All core features work
oos status
# ✅ CORE: Ready to use
# ⚪ ENHANCED: Run 'oos help setup' to enable
```

### Daily Usage

**Before:** Memorize which script, remember uv run, read docs
**After:** `oos <what-i-want>` and it either works or tells you what's missing

### Error Messages

**Before:**
```
ModuleNotFoundError: No module named 'click'
```

**After:**
```
❌ This feature needs Python dependencies
Run: oos setup core
Or: curl ... | bash (fresh install)
```

## Implementation

**8 Phases:**
1. Single CLI entry point → `bin/oos`
2. Tier detection → `oos status`
3. 5 clear docs (archive the rest)
4. Consolidate 120 scripts → ~10
5. Fix installation (actually works)
6. Simplify slash commands
7. Usage examples (not feature lists)
8. Test everything

**Timeline:** 14-21 hours
**Risk:** Low (additive changes, can rollback)

## Success Looks Like

**User installs OOS:**
```bash
curl -fsSL https://oos.dev/install | bash
✅ Installation successful!

Available features:
  ✅ CORE: Task tracking, project management, dev tools
  ⚪ ENHANCED: Run 'oos help setup' to enable
  
Try: oos project create my-first-project
```

**User creates project:**
```bash
oos project create my-app
cd my-app
oos dev setup
✅ Project ready!

Quick commands:
  oos task create "title"    # Track work
  oos test run               # Run tests
  oos help                   # Get help
```

**User enables AI (optional):**
```bash
oos help setup
# Shows: Get API key from openrouter.ai
# Add to .env: OPENROUTER_API_KEY=...

# User adds key

oos status
✅ CORE: Ready
✅ ENHANCED: AI features enabled
⚪ ADVANCED: Archon not configured

oos ai analyze "my code"
# AI analysis works!
```

## What We're NOT Changing

- ✅ All current features stay
- ✅ Slash commands still work
- ✅ Existing projects continue working
- ✅ Archon/AI integration preserved

**We're only changing:** How users access and discover features

## Questions for You

1. **Name:** Keep `oos` or switch to something like `dev` or `proj`?

2. **Tier names:** "Core/Enhanced/Advanced" clear enough?

3. **Breaking changes:** Okay if old `./bin/oos-task` style stops working?

4. **Slash commands:** Keep all 11 or just core 6 (dev, test, fix, task, project, help)?

5. **Priority:** What's most painful right now - install? docs? invocation?

## Bottom Line

**Same power, 10x easier to use.**

**Key change:** User doesn't need to understand OOS architecture.
**They just need:** `oos <task-they-want-to-do>`

Everything else is details.

---

**Ready to approve and implement?**

Or want to discuss/modify the approach first?
