# Initial Prompt for OOS Task Memory System

Build the OOS Task Memory System following PRD_OOS_TASK_MEMORY.md.

## Core Philosophy

These 5 principles guide every decision:
1. **Simplicity over Complexity** - SQLite + JSONL, not complex systems
2. **Project-Embedded Memory** - Tasks live IN the project, not external
3. **Git-Syncable by Design** - JSONL export after every change
4. **Agent-Friendly CLI** - AI can read/write tasks easily
5. **Modular and Optional** - OOS works without tasks, no breaking changes

## Workflow

### Phase 0: Review & Approval (REQUIRED)

1. **Read all setup files:**
   - `PRD_OOS_TASK_MEMORY.md` - Complete specification
   - `CONTEXT.md` - Architecture decisions and reasoning
   - `IMPLEMENTATION_PLAN.md` - 11 phases, 40+ tasks
   - `.claude_code_rules` - What to never/always do

2. **Understand existing OOS structure:**
   ```bash
   # Review existing OOS codebase
   ls -la scripts/
   ls -la bin/
   ls -la .claude/commands/
   cat .oos/config.yaml  # If exists
   ```

3. **Show proposed integration:**
   ```
   src/oos_task_system/          # NEW - All task code here
   ├── __init__.py
   ├── models.py                 # Task data class
   ├── database.py               # SQLite CRUD
   ├── dependencies.py           # Graph logic
   ├── jsonl_export.py           # Export to JSONL
   ├── jsonl_import.py           # Import from JSONL
   ├── validation.py             # Field validation
   ├── cli.py                    # Click CLI
   └── config.py                 # Config loading

   .oos/tasks/                   # NEW - Created per project
   ├── tasks.db                  # SQLite (NOT committed)
   └── export.jsonl              # JSONL (committed to git)

   .claude/commands/
   └── task.md                   # NEW - Slash command

   .github/workflows/
   └── archon-keepalive.yml      # NEW - Keep Archon alive

   bin/
   └── archon-keepalive.sh       # NEW - Local cron backup

   scripts/
   └── bootstrap_enhanced.sh     # MODIFIED - Add task init

   tests/
   ├── test_task_models.py       # NEW - Model tests
   ├── test_task_database.py     # NEW - Database tests
   ├── test_task_dependencies.py # NEW - Graph tests
   ├── test_jsonl_export_import.py # NEW - Export/import tests
   ├── test_cli.py               # NEW - CLI tests
   └── test_integration_end_to_end.py # NEW - Integration tests
   ```

4. **Confirm approach:**
   - All new code in `src/oos_task_system/` subdirectory ✅
   - No breaking changes to existing OOS ✅
   - Tasks are optional (can disable) ✅
   - Philosophy principles followed ✅

5. **WAIT FOR APPROVAL**

---

### After Approval: Autonomous Execution

Once approved, proceed through all 11 phases in IMPLEMENTATION_PLAN.md:

**Phase 1:** Core Data Models & Database (5 tasks)
**Phase 2:** JSONL Export/Import System (5 tasks)
**Phase 3:** Dependency Graph Logic (5 tasks)
**Phase 4:** CLI Commands (CRUD) (8 tasks)
**Phase 5:** CLI Commands (Import/Export/Ready) (5 tasks)
**Phase 6:** Slash Command Integration (5 tasks)
**Phase 7:** Archon Keep-Alive System (5 tasks)
**Phase 8:** Bootstrap Integration (6 tasks)
**Phase 9:** Configuration System (5 tasks)
**Phase 10:** Integration Testing (5 tasks)
**Phase 11:** Documentation & Polish (5 tasks)

**For each task:**
1. Write complete, working code (no placeholders, no TODOs)
2. Write tests alongside code (not after)
3. Run tests and verify they pass
4. Ensure code follows .claude_code_rules
5. Ensure module size < 300 lines
6. Check against philosophy principles
7. Move to next task

**Every 5 tasks, show checkpoint:**
```
✅ Phase X: Tasks [N-M] complete

Directory tree:
[show relevant structure with line counts]

Test results:
✅ XX/XX tests passing
- test_models.py: 12/12 ✅
- test_database.py: 15/15 ✅

What works:
- [Feature A]: ✅
- [Feature B]: ✅
- [Feature C]: 🚧 in progress

Progress: XX% (N/42 total tasks)

Next 3 tasks:
1. [Task]
2. [Task]
3. [Task]

Continuing autonomously...
```

---

## Key Rules (from .claude_code_rules)

### NEVER:
- ❌ Write placeholder code or TODO comments
- ❌ Skip tests (test alongside implementation)
- ❌ Exceed 300 lines per module
- ❌ Violate philosophy principles
- ❌ Use absolute paths (use relative)
- ❌ Silent failures (explicit errors)
- ❌ Break existing OOS functionality

### ALWAYS:
- ✅ Write complete, fully-implemented code
- ✅ Test as you build (not after)
- ✅ Follow PRD specifications exactly
- ✅ Keep modules small and focused (< 300 lines)
- ✅ Use concrete examples from PRD
- ✅ Provide actionable error messages
- ✅ Check every 5 tasks (show checkpoint)
- ✅ Update documentation as you go

### Philosophy Check:
Before committing code, verify:
1. **Is it simple?** (not complex)
2. **Is it project-embedded?** (not external)
3. **Is it git-syncable?** (JSONL export works)
4. **Is it agent-friendly?** (clear CLI, JSON output)
5. **Is it modular?** (optional, no breaking changes)

If answer is "no" to any → refactor before moving on.

---

## Checkpoint Rhythm

Every 5 completed tasks:
- Show directory tree with line counts
- Show test results (all tests must pass)
- List what works
- Show progress percentage
- List next 3 tasks
- Continue autonomously

**Do NOT** batch multiple completions. Show checkpoint after every 5 tasks.

---

## Success Criteria - Stop When:

- ✅ All 11 phases complete (42+ tasks done)
- ✅ All tests passing (unit + integration)
- ✅ All CLI commands functional:
  * `oos task create "title"`
  * `oos task list`
  * `oos task show <id>`
  * `oos task update <id> --status doing`
  * `oos task complete <id>`
  * `oos task delete <id>`
  * `oos task ready`
  * `oos task import <file>`
  * `oos task export`
- ✅ Slash commands work in Claude Code:
  * `/task create "title"`
  * `/task list --ready`
  * `/task complete <id>`
- ✅ Bootstrap integration complete:
  * `oos bootstrap` creates `.oos/tasks/`
  * Creates SQLite database with schema
  * Creates empty JSONL export
  * Updates `.gitignore` correctly
- ✅ Archon keep-alive deployed:
  * `.github/workflows/archon-keepalive.yml` exists
  * `bin/archon-keepalive.sh` exists
  * Workflow pings every 2 days
- ✅ Documentation comprehensive:
  * README.md updated with task system
  * TASK_SYSTEM_GUIDE.md created
  * All examples work
  * Troubleshooting section complete
- ✅ Performance requirements met:
  * 1000 tasks: list < 100ms
  * 1000 tasks: ready < 50ms
  * 1000 tasks: export < 200ms
  * 1000 tasks: import < 500ms
- ✅ No TODO comments in code
- ✅ No modules exceed 300 lines
- ✅ No placeholders or incomplete implementations
- ✅ Philosophy principles enforced throughout
- ✅ Existing OOS functionality NOT broken

---

## When Complete

Show final report:
```
🎉 OOS Task Memory System - Build Complete

All phases implemented:
✅ Phase 1: Core Data Models & Database
✅ Phase 2: JSONL Export/Import System
✅ Phase 3: Dependency Graph Logic
✅ Phase 4-5: CLI Commands (8 commands)
✅ Phase 6: Slash Command Integration
✅ Phase 7: Archon Keep-Alive System
✅ Phase 8: Bootstrap Integration
✅ Phase 9: Configuration System
✅ Phase 10: Integration Testing
✅ Phase 11: Documentation & Polish

Final directory tree:
[show complete structure]

Test results:
✅ XX/XX tests passing (90%+ coverage)
- Unit tests: XX/XX ✅
- Integration tests: XX/XX ✅

What works:
✅ All CLI commands functional
✅ All slash commands work in Claude Code
✅ Git sync via JSONL export
✅ Dependency graph with circular detection
✅ Ready work detection for AI agents
✅ Archon keep-alive (prevents Supabase downtime)
✅ Bootstrap integration (automatic setup)
✅ Configuration system (tasks optional)

Performance:
✅ 1000 tasks: list in XXms (< 100ms required)
✅ 1000 tasks: ready in XXms (< 50ms required)
✅ 1000 tasks: export in XXms (< 200ms required)
✅ 1000 tasks: import in XXms (< 500ms required)

Philosophy compliance:
✅ Simplicity: SQLite + JSONL, minimal dependencies
✅ Project-Embedded: Tasks in `.oos/tasks/`
✅ Git-Syncable: JSONL export committed to git
✅ Agent-Friendly: JSON output, clear errors
✅ Modular: Optional, no breaking changes

Code quality:
✅ No TODO comments
✅ No modules > 300 lines
✅ All functions fully implemented
✅ 90%+ test coverage
✅ Type hints on all functions
✅ Docstrings on all public functions

Documentation:
✅ README.md updated
✅ TASK_SYSTEM_GUIDE.md created
✅ All examples tested
✅ Troubleshooting guide complete

Ready to use!

Installation (for new projects):
```bash
oos bootstrap my-project
cd my-project
oos task create "First task"
oos task list
```

Installation (for existing projects):
```bash
cd existing-project
oos bootstrap --add-tasks
oos task create "First task"
```

Using slash commands in Claude Code:
```
/task create "Implement auth"
/task ready
/task complete <id>
```

See TASK_SYSTEM_GUIDE.md for complete documentation.
```

---

## Start Now

Begin with Phase 0:
1. Read all setup files
2. Review OOS codebase structure
3. Show proposed integration
4. WAIT FOR MY APPROVAL

Do not proceed to Phase 1 until I approve the approach.

Once approved, execute all 11 phases autonomously, showing checkpoints every 5 tasks.

Let's build this! 🚀
