# How to Use These Setup Files - OOS Task Memory System

## What You Have

This directory contains all files needed for Stage 3 (Autonomous Build) of the AI-Driven Project Builder workflow:

```
OOS_TASK_MEMORY_BUILD/
├── PRD_OOS_TASK_MEMORY.md          # Complete specification (source of truth)
├── IMPLEMENTATION_PLAN.md           # 11 phases, 42+ tasks
├── CONTEXT.md                       # Architecture decisions & reasoning
├── .claude_code_rules               # Development rules & philosophy enforcement
├── INITIAL_PROMPT.md                # What to paste into Claude Code
└── README_TRANSFER.md               # This file (how to use everything)
```

**PRD Status:** ✅ 100% ready (self-assessment passed, all criteria met)

**What This Builds:**
- Local SQLite task database (`.oos/tasks.db`)
- Git-syncable JSONL export (`.oos/tasks/export.jsonl`)
- 8 CLI commands (`oos task create/list/show/update/complete/delete/ready/import/export`)
- Slash commands for Claude Code (`/task [command]`)
- Dependency graph (tasks can block other tasks)
- Ready work detection (show unblocked tasks)
- Archon keep-alive system (GitHub Actions + cron)
- Bootstrap integration (automatic setup)

---

## Stage 3: Autonomous Build

### Step 1: You're Already in the Right Place

Files are already in `/home/user/oos/OOS_TASK_MEMORY_BUILD/`

No transfer needed - Claude Code is already running in `/home/user/oos/`

### Step 2: Start Claude Code

```bash
# Already running! You're in Claude Code now.
```

### Step 3: Paste Initial Prompt

1. Open `INITIAL_PROMPT.md` in your editor
2. Copy the **entire contents**
3. Paste into this Claude Code conversation
4. Press Enter

**What happens next:**

**Phase 0 (Requires Your Approval):**
1. Claude Code reads all setup files
2. Reviews existing OOS codebase structure
3. Shows proposed integration approach
4. **WAITS FOR YOUR APPROVAL**

**You review and either:**
- Approve: "Approved. Proceed with autonomous build."
- Request changes: "Change X to Y, then proceed."

**After Your Approval:**
- Claude Code executes all 11 phases autonomously
- Shows checkpoint every 5 tasks
- Builds complete system matching PRD
- Stops when all success criteria met

---

## What to Expect During Build

### Timeline
- **Duration:** 2-4 days of autonomous building
- **Active time:** ~30 minutes (Phase 0 approval + final review)
- **Calendar time:** Claude Code runs mostly unattended

### Checkpoints Every 5 Tasks

You'll see progress reports like this:
```
✅ Phase 2: Tasks 6-10 complete

Directory tree:
src/oos_task_system/
├── models.py (142 lines)
├── database.py (198 lines)
├── validation.py (87 lines)
├── jsonl_export.py (156 lines)
├── jsonl_import.py (172 lines)

Test results:
✅ 47/47 tests passing
- test_models.py: 12/12 ✅
- test_database.py: 15/15 ✅
- test_jsonl_export_import.py: 20/20 ✅

What works:
- Task models ✅
- SQLite CRUD ✅
- Validation rules ✅
- JSONL export ✅
- JSONL import ✅

Progress: 24% (10/42 tasks)

Next 3 tasks:
1. Implement dependency graph logic
2. Add circular dependency detection
3. Write dependency tests

Continuing autonomously...
```

### When Claude Code Asks Questions

Claude Code will only ask if:
- PRD is ambiguous for a specific case
- Security decision needed
- External credentials required
- Unavoidable blocker encountered

Answer the question and it continues.

---

## Checking Progress Anytime

You can interrupt and ask:

```
What's the current progress? Show tree and test results.
```

Claude Code will respond without losing its place.

Or check files directly:
```bash
# See what's been created
ls -la src/oos_task_system/

# Check tests
pytest tests/test_task_*.py

# See line counts
wc -l src/oos_task_system/*.py
```

---

## When Build Completes

Claude Code stops and shows final report:

```
🎉 OOS Task Memory System - Build Complete

All phases implemented:
✅ Phase 1-11: All tasks complete
✅ 90%+ test coverage
✅ All CLI commands functional
✅ All slash commands work
✅ Documentation comprehensive

Ready to use!

Try it:
  oos task create "My first task"
  oos task list
  /task ready
```

---

## After Build Completes

### Test the System

```bash
# Create a test project
cd /tmp
/home/user/oos/scripts/bootstrap_enhanced.sh test-project

# Use the task system
cd test-project
oos task create "Implement feature X"
oos task create "Write tests for X"
oos task list
oos task ready

# Try git sync
git add .oos/tasks/export.jsonl
git commit -m "Add tasks"
```

### Try Slash Commands

In Claude Code:
```
/task create "Test slash command"
/task list --ready
/task show <id>
```

### Review Documentation

```bash
# User guide
cat TASK_SYSTEM_GUIDE.md

# Main README
cat README.md | grep -A 20 "Task System"

# Examples
cat TASK_SYSTEM_GUIDE.md | grep -A 10 "Examples"
```

---

## Troubleshooting

### If Build Gets Stuck

**Symptom:** No checkpoint for extended period

**Check:**
```bash
# What's Claude Code working on?
# Just ask in conversation:
"What's the current status? What are you working on?"
```

**If truly stuck:**
1. Check last commit to see progress
2. Ask Claude Code what's blocking
3. Provide input if waiting for decision
4. Continue from where it stopped

### If Tests Are Failing

**Symptom:** Checkpoint shows failing tests

**Action:**
```
STOP. No new features until all tests pass.
Show me the failing test output.
```

Claude Code will fix tests before continuing.

### If Philosophy Violated

**Symptom:** Code doesn't match principles

**Action:**
```
This violates [principle name] because [reason].
The code should [what it should do instead].
Refactor and continue.
```

Claude Code will refactor to match philosophy.

---

## Success Criteria Checklist

Build is complete when:

**Functionality:**
- [ ] Can create tasks via CLI: `oos task create "title"`
- [ ] Can create tasks via slash command: `/task create "title"`
- [ ] Can list tasks: `oos task list`
- [ ] Can show ready work: `oos task ready`
- [ ] Can complete tasks: `oos task complete <id>`
- [ ] Tasks sync via git: commit `.oos/tasks/export.jsonl`
- [ ] Bootstrap creates task system: `oos bootstrap` creates `.oos/tasks/`

**Quality:**
- [ ] All tests passing (unit + integration)
- [ ] 90%+ test coverage
- [ ] No TODO comments
- [ ] No modules > 300 lines
- [ ] Performance requirements met (1000 tasks < 100ms list)

**Philosophy:**
- [ ] Simplicity: SQLite + JSONL (no complex systems)
- [ ] Project-Embedded: Tasks in `.oos/tasks/`
- [ ] Git-Syncable: JSONL committed, SQLite not committed
- [ ] Agent-Friendly: JSON output, clear errors
- [ ] Modular: Can disable with `tasks.enabled: false`

**Documentation:**
- [ ] README.md updated with task system section
- [ ] TASK_SYSTEM_GUIDE.md created with examples
- [ ] All commands have `--help` text
- [ ] Troubleshooting guide complete

**Integration:**
- [ ] Bootstrap integration works
- [ ] Slash commands work in Claude Code
- [ ] Archon keep-alive deployed (GitHub Actions workflow)
- [ ] No breaking changes to existing OOS

If all checkboxes checked: **Build is complete** ✅

---

## Next Steps After Build

### 1. Use It for 1-2 Weeks

Start using the task system in real projects:
```bash
oos bootstrap my-real-project
cd my-real-project
oos task create "Real task"
```

Note what works, what doesn't, what's missing.

### 2. Document Phase 2 Requirements

After real usage, you'll know what you need for Phase 2:
- What preferences you wish were captured
- What patterns you repeat across projects
- What decisions you make repeatedly

Use that data to design Phase 2 (Preferences & Patterns System).

### 3. Phase 2 PRD

Create Phase 2 PRD following same template:
- Data models for preferences
- Data models for patterns
- CLI commands for pattern management
- Bootstrap templates
- Complete specification

Then run autonomous build for Phase 2.

---

## Files Reference

### PRD_OOS_TASK_MEMORY.md
**Purpose:** Complete specification (source of truth)
**When to read:** When Claude Code asks "what does PRD say about X?"

### IMPLEMENTATION_PLAN.md
**Purpose:** 11 phases, 42+ tasks breakdown
**When to read:** To understand progress, phases, task order

### CONTEXT.md
**Purpose:** Architecture decisions and reasoning
**When to read:** To understand "why" behind decisions

### .claude_code_rules
**Purpose:** What to never/always do, philosophy enforcement
**When to read:** When reviewing code quality, checking compliance

### INITIAL_PROMPT.md
**Purpose:** Kickoff autonomous build
**When to paste:** Right now (Step 3 above)

### README_TRANSFER.md
**Purpose:** This file - how to use everything
**When to read:** You're reading it now!

---

## Summary

**What:** Autonomous build of OOS Task Memory System
**How:** Paste INITIAL_PROMPT.md into Claude Code, approve Phase 0, let it run
**Duration:** 2-4 days mostly unattended
**Result:** Complete task management system matching PRD

**Next Action:** Open `INITIAL_PROMPT.md`, copy entire contents, paste into this conversation.

Let's build this! 🚀
