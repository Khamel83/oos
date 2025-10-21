# Context for OOS Task Memory System

## What We're Building

**OOS Task Memory System** - A beads-inspired, project-embedded task management system that gives AI agents context preservation across sessions while keeping tasks portable via git.

**One-Sentence Summary:** Local SQLite task database per project, synced via JSONL to git, with CLI and slash commands for humans and AI agents.

---

## Core Philosophy

These 5 principles guide EVERY implementation decision:

### 1. Simplicity over Complexity

**What it means:**
Use the simplest solution that works. SQLite over PostgreSQL. JSONL over complex serialization. No frameworks beyond CLI tool (Click).

**Why:**
Complex systems break. Simple systems last. We're building for decades, not months.

**Examples:**
- ✅ SQLite (built-in, no server) not PostgreSQL (server, complex)
- ✅ JSONL (one task per line) not nested JSON (complex parsing)
- ✅ Click (minimal CLI framework) not complex command system
- ✅ 9 task fields not 50 fields

### 2. Project-Embedded Memory

**What it means:**
Tasks live IN the project (`.oos/tasks.db`), not on external server. Each project is self-contained.

**Why:**
External servers go down, require network, don't travel with git. Project-embedded memory is portable, always available, offline-first.

**Examples:**
- ✅ `.oos/tasks.db` (in project) not Archon database (external)
- ✅ Relative paths not absolute paths
- ✅ No network calls for task operations
- ✅ Git clone = get tasks automatically

### 3. Git-Syncable by Design

**What it means:**
Tasks sync via git like code does. JSONL export is source of truth for git. SQLite is local cache.

**Why:**
Git is proven collaboration tool. Leveraging git means tasks work wherever code works.

**Examples:**
- ✅ `.oos/tasks/export.jsonl` committed to git
- ✅ `.oos/tasks.db` NOT committed (binary, merge conflicts)
- ✅ One task per line (line-based git diff)
- ✅ Timestamp-based merge (newer wins)

### 4. Agent-Friendly CLI

**What it means:**
AI agents can use CLI without ambiguity. JSON output for parsing. Predictable exit codes. Clear errors.

**Why:**
This tool is for AI-assisted development. If agents can't use it, we failed.

**Examples:**
- ✅ `--format json` for all commands
- ✅ Exit code 0=success, 1=user error, 2=system error
- ✅ Error messages actionable ("Title too short: need 5+ chars, got 4")
- ✅ JSON output parseable by agents

### 5. Modular and Optional

**What it means:**
Task system is optional. OOS works without it. No breaking changes to core OOS.

**Why:**
Not everyone needs tasks. Users should opt-in, not opt-out. Graceful degradation.

**Examples:**
- ✅ `tasks.enabled: false` disables system
- ✅ All code in `src/oos_task_system/` subdirectory
- ✅ Bootstrap skips tasks if disabled
- ✅ No dependency from core OOS to task system

---

## Why This Approach

### Decision 1: Why Local SQLite, Not Remote Database?

**Context:**
Need task storage that's fast, portable, and works offline.

**Options Considered:**
1. PostgreSQL - Full-featured, requires server, not portable
2. SQLite - Simple, serverless, portable
3. JSON files - Simple but no querying
4. YAML files - Human-readable but slow

**Decision:** SQLite + JSONL hybrid

**Rationale:**
- SQLite for fast queries (better than parsing JSON/YAML)
- JSONL for git sync (solves SQLite's binary format issue)
- Best of both worlds: fast local + git-friendly export
- Built into Python (no installation)
- Proven reliability (used in browsers, mobile apps, everywhere)

**Consequences:**
- ✅ Pro: Fast local queries
- ✅ Pro: No server required
- ✅ Pro: Can rebuild from JSONL if corrupted
- ⚠️ Con: Binary format (not git-friendly)
  - **Mitigated:** JSONL export after every change
- ⚠️ Con: Concurrent writes need handling
  - **Mitigated:** Single-user tool, retry logic for rare conflicts

### Decision 2: Why Hybrid Archon Integration, Not Replacement?

**Context:**
Archon provides excellent RAG/knowledge base but tasks aren't git-portable.

**Options Considered:**
1. Replace Archon completely - Lose RAG functionality
2. Archon-only - Tasks not portable, agent amnesia continues
3. Hybrid approach - Local for tasks, Archon for RAG

**Decision:** Hybrid (option 3)

**Rationale:**
- Archon RAG is valuable (document search, cross-project views)
- Local tasks solve portability problem
- Complementary, not competitive
- Optional one-way sync (local → Archon) for backup

**Consequences:**
- ✅ Pro: Keep Archon's RAG functionality
- ✅ Pro: Tasks portable via git
- ✅ Pro: Fast local operations
- ⚠️ Con: Two systems to maintain
  - **Mitigated:** Optional, can disable either

### Decision 3: Why JSONL, Not JSON or YAML?

**Context:**
Need text format for git sync that's both human-readable and machine-parseable.

**Options Considered:**
1. JSON (single array) - Not line-based, merge conflicts hard
2. YAML - Human-readable but multi-line, complex merge conflicts
3. JSONL - One object per line, simple merges
4. CSV - Simple but limited structure

**Decision:** JSONL (JSON Lines)

**Rationale:**
- One task per line = one change per line in git diff
- Git merge conflicts are line-based (easy to resolve)
- JSON parseable by all tools
- Compact (not as verbose as YAML)
- Proven format (used in data pipelines, ML datasets)

**Consequences:**
- ✅ Pro: Line-based git diff
- ✅ Pro: Easy merge conflict resolution
- ✅ Pro: Machine-parseable
- ⚠️ Con: Not as human-readable as YAML
  - **Mitigated:** CLI provides readable views, JSONL for git only

### Decision 4: Why Click Framework, Not argparse?

**Context:**
Need CLI framework for `oos task` commands.

**Options Considered:**
1. argparse (stdlib) - No dependencies but verbose
2. Click - Clean, composable, decorators
3. Typer - Modern but adds dependency
4. Custom parser - Full control but time-consuming

**Decision:** Click

**Rationale:**
- Clean decorator-based API
- Subcommand support (`oos task create`, `oos task list`)
- Good documentation
- Widely used, proven
- Minimal dependency (single package)

**Consequences:**
- ✅ Pro: Clean code, less boilerplate
- ✅ Pro: Great error messages
- ⚠️ Con: One external dependency
  - **Mitigated:** Click is stable, widely used

### Decision 5: Why Blocks/Blocked-By Only, Not Full DAG?

**Context:**
Need task dependencies for "what's ready to work on?"

**Options Considered:**
1. Full DAG (blocks, parent-child, related, discovered-from)
2. Simple blocks/blocked-by only
3. No dependencies

**Decision:** Simple blocks/blocked-by (option 2)

**Rationale:**
- Covers 90% of use cases (task A must finish before B)
- Simple to implement and understand
- Easy to visualize
- Can expand later if needed (Phase 2)

**Consequences:**
- ✅ Pro: Simple mental model
- ✅ Pro: Easy to implement
- ⚠️ Con: No parent-child (epics/subtasks)
  - **Mitigated:** Can add in v1.1 if users request

---

## Technical Constraints

### Target Environment
- OS: Linux, macOS, Windows (via WSL or native)
- Python: 3.9+ (for type hints, pathlib)
- SQLite: 3.31+ (CHECK constraints)
- No external services required

### Module Size Limits
- Each Python module < 300 lines
- If approaching limit, refactor into smaller modules
- Prefer functions over classes where possible

### Performance Requirements
- 1000 tasks: list command < 100ms
- 1000 tasks: ready command < 50ms
- 1000 tasks: export < 200ms
- 1000 tasks: import < 500ms

### Code Quality
- Type hints on all function signatures
- Docstrings on all public functions
- Unit tests for all business logic
- 90%+ test coverage

---

## What Exists (OOS Foundation)

This task system integrates with existing OOS:

**Existing OOS Components:**
- `scripts/bootstrap_enhanced.sh` - Project setup (we enhance this)
- `.oos/config.yaml` - Configuration (we add tasks section)
- `.oos/secrets/` - 1Password secrets (we don't touch)
- `bin/` - Utility scripts (we add `archon-keepalive.sh`)
- `.claude/commands/` - Slash commands (we add `task.md`)

**Integration Points:**
1. **Bootstrap** - Add task init to `scripts/bootstrap_enhanced.sh`
2. **Config** - Add `tasks:` section to `.oos/config.yaml`
3. **Slash Commands** - Create `.claude/commands/task.md`
4. **Start Coding** - Enhance `/start-coding` to show ready tasks
5. **Keep-Alive** - Add GitHub Actions workflow

**NO Changes To:**
- Secrets management (1Password integration)
- Environment variable handling
- Core bootstrap logic
- Archon MCP integration (only add keep-alive)

---

## Key Architectural Decisions

### 1. Separation of Concerns

```
src/oos_task_system/
├── models.py         # Task data class, validation
├── database.py       # SQLite operations (CRUD)
├── dependencies.py   # Graph logic, circular detection
├── jsonl_export.py   # Export to JSONL
├── jsonl_import.py   # Import from JSONL
├── validation.py     # Field validation rules
├── cli.py            # Click CLI commands
└── config.py         # Config loading
```

**Why:** Each module has single responsibility. Easy to test, modify, extend.

### 2. Database as Cache, JSONL as Truth

- SQLite = fast local cache for queries
- JSONL = source of truth for git
- Rebuild database from JSONL anytime

**Recovery:**
```bash
# Database corrupted?
rm .oos/tasks.db
oos task import .oos/tasks/export.jsonl
# Database rebuilt
```

### 3. Validation at Multiple Layers

1. **CLI Layer** - argparse/Click validates types
2. **Model Layer** - Python validates constraints
3. **Database Layer** - SQLite CHECK constraints

**Why:** Defense in depth. Catch errors early. Helpful error messages at each layer.

### 4. Timestamps for Conflict Resolution

When importing JSONL:
- Compare `updated` timestamps
- Newer timestamp wins
- If equal: local database wins (no change)

**Why:** Simple, deterministic, no complex merge logic needed.

### 5. Agent Context on `/start-coding`

When user runs `/start-coding`, show:
```
Ready to work on (3 tasks):
1. Implement auth endpoint (oldest)
2. Write unit tests
3. Update documentation

Suggested: Start with #1 (oldest ready task)
```

**Why:** AI agent has context, knows what to work on, no amnesia.

---

## Integration with Archon

### Three-Tier Architecture

**Tier 1: Archon (Cloud)**
- RAG/Knowledge Base - `/archon-research "topic"`
- Cross-Project Views - See all projects in web UI
- Project Registry - Central catalog
- **Keep-Alive** - GitHub Actions pings every 2 days

**Tier 2: Local Tasks (Git)**
- Project-embedded task database
- Git-syncable via JSONL
- Fast, offline, portable

**Tier 3: Optional Sync (Future)**
- One-way: local → Archon (v1.1)
- For backup and global visibility

### Archon Keep-Alive

**Problem:** Supabase free tier pauses after inactivity

**Solution:**
- GitHub Actions: `.github/workflows/archon-keepalive.yml`
- Pings Archon every 2 days (prevents pause)
- Local cron backup (optional)
- Manual trigger via workflow_dispatch

**Why:** Ensures RAG always accessible, no Supabase downtime.

---

## Testing Strategy

### Unit Tests (90%+ Coverage)

- `tests/test_models.py` - All validation rules
- `tests/test_database.py` - All CRUD operations
- `tests/test_dependencies.py` - Graph logic, circular detection
- `tests/test_jsonl_export_import.py` - Export, import, merge
- `tests/test_cli.py` - All CLI commands
- `tests/test_config.py` - Config loading

### Integration Tests

- `tests/test_integration_end_to_end.py`
  1. Bootstrap → Create → List → Complete → Git sync
  2. Git workflow (commit, pull, import, conflicts)
  3. Dependency workflow (block, unblock, ready)
  4. Error recovery (corrupt DB, rebuild from JSONL)

### Performance Tests

- 1000 tasks: all operations within time limits
- Memory usage < 100MB with 10,000 tasks
- Database size grows linearly (~1KB per task)

### Manual Tests

- Slash commands in Claude Code
- GitHub Actions workflow (manual trigger)
- Bootstrap on fresh project
- Documentation examples work

---

## Deployment Strategy

### For New Projects
```bash
oos bootstrap my-project
# Task system created automatically
oos task create "First task"
```

### For Existing Projects
```bash
cd existing-project
oos bootstrap --add-tasks
# Task system added to existing project
```

### For OOS Itself
```bash
# Install updated OOS
git pull origin main
pip install -e .
# Task system available for all future projects
```

---

## Success Criteria

When build is complete, user should be able to:

1. **Bootstrap new project**: Task system created automatically
2. **Create tasks via CLI**: `oos task create "title"`
3. **Create tasks via slash commands**: `/task create "title"` in Claude Code
4. **See ready work**: `oos task ready` shows unblocked tasks
5. **Git sync**: Commit `.oos/tasks/export.jsonl`, push, pull on another machine
6. **AI agent context**: AI sees tasks when starting work
7. **Archon stays alive**: No Supabase downtime
8. **Disable if needed**: `tasks.enabled: false` disables system

And critically:
- ✅ Existing OOS functionality NOT broken
- ✅ Simple to use (not complex)
- ✅ Fast (< 100ms for common operations)
- ✅ Reliable (rebuild from JSONL if corrupted)
- ✅ Documented (every command has examples)

---

## References

- **PRD:** See `PRD_OOS_TASK_MEMORY.md` for complete specification
- **beads:** Inspiration from https://github.com/steveyegge/beads
- **OOS Philosophy:** Simplicity, modularity, Unix philosophy
- **AI-Driven Project Builder:** Workflow from your document

---

*This context explains the "why" behind every architectural decision. When in doubt, refer to the 5 core principles. When those conflict, simplicity wins.*
