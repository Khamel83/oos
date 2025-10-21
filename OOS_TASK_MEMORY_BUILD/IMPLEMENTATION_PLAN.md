# Implementation Plan for OOS Task Memory System

## Philosophy

This build follows OOS philosophy:
1. **Simplicity over Complexity** - SQLite + JSONL, not complex systems
2. **Project-Embedded Memory** - Tasks live IN the project
3. **Git-Syncable by Design** - JSONL export is source of truth
4. **Agent-Friendly CLI** - AI can read/write tasks
5. **Modular and Optional** - OOS works without it

## Phase 0: Archive & Setup

**Duration:** First session, requires approval

**Tasks:**
1. Read all setup files (PRD, CONTEXT, IMPLEMENTATION_PLAN, .claude_code_rules)
2. Review OOS codebase structure (understand existing bootstrap, slash commands)
3. Show proposed directory structure for task system integration
4. Get approval from user before proceeding
5. Create `.oos/tasks/` directory structure if starting fresh

**Success Criteria:**
- All setup files read and understood
- OOS codebase structure understood
- Proposed integration plan approved by user
- No breaking changes to existing OOS functionality

**Approval Required:** YES - user must approve integration approach before coding

---

## Phase 1: Core Data Models & Database

**Duration:** ~4-6 hours

**Tasks:**
1. Create `src/oos_task_system/models.py` - Task data class with validation
2. Create `src/oos_task_system/database.py` - SQLite schema and CRUD operations
3. Create `src/oos_task_system/validation.py` - Field validation rules from PRD
4. Write unit tests: `tests/test_task_models.py` (all validation rules)
5. Write unit tests: `tests/test_task_database.py` (SQLite CRUD)

**Success Criteria:**
- Task model matches PRD specification exactly
- SQLite database created with schema from PRD (Section 2)
- All validation rules from PRD implemented (5-200 char title, status enum, etc.)
- Unit tests pass: 100% model coverage
- Database constraints enforced (CHECK clauses)

**Tests:**
- Title validation: 4 chars fail, 5 chars pass, 200 pass, 201 fail
- Description validation: 0-10000 chars
- Status enum validation: todo/doing/done/blocked pass, invalid fail
- UUID generation for task ID
- Timestamp auto-generation for created/updated

**Module Size Limit:** Each file < 300 lines

---

## Phase 2: JSONL Export/Import System

**Duration:** ~3-4 hours

**Tasks:**
1. Create `src/oos_task_system/jsonl_export.py` - Export all tasks to JSONL
2. Create `src/oos_task_system/jsonl_import.py` - Import tasks from JSONL
3. Implement timestamp-based merge strategy (newer wins)
4. Handle invalid JSON lines gracefully (skip, log, continue)
5. Write unit tests: `tests/test_jsonl_export_import.py`

**Success Criteria:**
- Export writes one task per line (compact JSON)
- Import merges by timestamp (PRD Section 3, FR-7)
- Invalid lines skipped with warnings
- Export triggered after every create/update/delete
- Unit tests pass: export, import, merge scenarios

**Tests:**
- Export all tasks to JSONL file
- Import from JSONL: new tasks inserted, existing updated
- Merge conflicts: newer timestamp wins
- Invalid JSON line: skip and continue
- Empty file: no-op

**Edge Cases:**
- Concurrent writes (retry with backoff)
- Corrupted JSONL (skip bad lines)
- Missing .oos/tasks/ directory (create on first export)

---

## Phase 3: Dependency Graph Logic

**Duration:** ~3-4 hours

**Tasks:**
1. Create `src/oos_task_system/dependencies.py` - Graph logic
2. Implement circular dependency detection (A→B→C→A)
3. Implement self-blocking detection (A→A)
4. Implement bidirectional sync (A blocks B: A.blocks=[B], B.blocked_by=[A])
5. Write unit tests: `tests/test_dependencies.py`

**Success Criteria:**
- Circular dependencies rejected with error message showing chain
- Self-blocking rejected
- Bidirectional sync maintained automatically
- Ready work detection: tasks with blocked_by=[] (PRD FR-5)
- Unit tests pass: all dependency scenarios

**Tests:**
- Add block: A blocks B (both updated)
- Remove block: A unblocks B (both updated)
- Circular: A→B→C→A rejected
- Self-block: A→A rejected
- Ready work: only unblocked tasks returned

---

## Phase 4: CLI Commands (CRUD)

**Duration:** ~5-7 hours

**Tasks:**
1. Create `src/oos_task_system/cli.py` - Click CLI framework
2. Implement `oos task create` - FR-1 from PRD
3. Implement `oos task list` - FR-2 from PRD
4. Implement `oos task show` - Display single task details
5. Implement `oos task update` - FR-3 from PRD
6. Implement `oos task complete` - FR-4 from PRD
7. Implement `oos task delete` - FR-6 from PRD
8. Write unit tests: `tests/test_cli.py` (all commands)

**Success Criteria:**
- All CLI commands match PRD specification (Section 6)
- Exit codes correct: 0=success, 1=user error, 2=system error
- `--format json` works for all commands
- Error messages actionable and specific
- Unit tests pass: every command with valid/invalid inputs

**Tests:**
- create: valid task, title too short, title too long
- list: all tasks, filter by status, filter by feature, --ready flag
- show: valid ID, invalid ID
- update: valid updates, circular dependency blocked
- complete: valid ID, already completed
- delete: with confirmation, with --force, with dependencies

**Module Size:** cli.py should stay < 300 lines (use subcommands if needed)

---

## Phase 5: CLI Commands (Import/Export/Ready)

**Duration:** ~3-4 hours

**Tasks:**
1. Implement `oos task import` - FR-7 from PRD
2. Implement `oos task export` - Force export
3. Implement `oos task ready` - FR-5 from PRD (show unblocked tasks)
4. Add `--format` support for all commands (table, json, yaml)
5. Write unit tests: `tests/test_cli_advanced.py`

**Success Criteria:**
- Import handles merge conflicts correctly
- Export regenerates JSONL on demand
- Ready shows only unblocked tasks, sorted oldest first
- All output formats work (table, json, yaml)
- Unit tests pass

**Tests:**
- import: new tasks, existing tasks, conflicts, invalid lines
- export: force regeneration of JSONL
- ready: show only unblocked, suggest oldest task
- Format output: table (default), json, yaml

---

## Phase 6: Slash Command Integration

**Duration:** ~2-3 hours

**Tasks:**
1. Create `.claude/commands/task.md` - Slash command definition
2. Document all `/task` subcommands with examples
3. Test slash commands in Claude Code
4. Update existing `/start-coding` to show ready tasks
5. Document integration in README

**Success Criteria:**
- `/task create "title"` works in Claude Code
- `/task list --ready` works in Claude Code
- `/task complete <id>` works in Claude Code
- `/start-coding` shows ready tasks from local database
- Documentation clear and complete

**Tests:**
- Manual testing in Claude Code
- Verify slash commands call CLI correctly
- Verify output formatting in Claude Code

---

## Phase 7: Archon Keep-Alive System

**Duration:** ~2-3 hours

**Tasks:**
1. Create `.github/workflows/archon-keepalive.yml` - GitHub Actions workflow
2. Create `bin/archon-keepalive.sh` - Local cron script
3. Test workflow runs manually (workflow_dispatch)
4. Document setup in README
5. Add keep-alive setup to bootstrap process

**Success Criteria:**
- GitHub Actions workflow pings every 2 days
- Local script pings Archon health and MCP endpoints
- Manual trigger works via workflow_dispatch
- Logs successful pings
- Bootstrap optionally sets up cron job

**Tests:**
- Manual trigger GitHub Actions workflow
- Run local script: verify HTTP 200 responses
- Check logs: verify ping recorded

**Files Created:**
- `.github/workflows/archon-keepalive.yml`
- `bin/archon-keepalive.sh`

---

## Phase 8: Bootstrap Integration

**Duration:** ~3-4 hours

**Tasks:**
1. Update `scripts/bootstrap_enhanced.sh` - Add task system init
2. Create `.oos/tasks.db` during bootstrap
3. Create `.oos/tasks/export.jsonl` during bootstrap
4. Add `.oos/tasks.db` to `.gitignore`
5. Ensure `.oos/tasks/export.jsonl` is NOT in `.gitignore`
6. Test bootstrap on new project

**Success Criteria:**
- `oos bootstrap` creates `.oos/tasks/` directory
- SQLite database initialized with schema
- Export JSONL created (empty initially)
- `.gitignore` updated correctly
- Bootstrap doesn't break if task system disabled

**Tests:**
- Bootstrap new project: verify `.oos/tasks/` created
- Verify `.gitignore` excludes `.oos/tasks.db`
- Verify `.gitignore` includes `.oos/tasks/export.jsonl`
- Bootstrap with `tasks.enabled: false`: skip task init

---

## Phase 9: Configuration System

**Duration:** ~2-3 hours

**Tasks:**
1. Update `.oos/config.yaml` schema - Add tasks section
2. Implement config loading in task system
3. Support `tasks.enabled: false` to disable system
4. Support custom paths for database and export
5. Write unit tests: `tests/test_config.py`

**Success Criteria:**
- Config matches PRD specification (Section 4)
- Tasks can be disabled via config
- Custom paths work
- Defaults used if config missing
- Unit tests pass

**Tests:**
- Load config: valid, missing, invalid
- Disabled tasks: commands return helpful message
- Custom paths: database and export in custom locations

---

## Phase 10: Integration Testing

**Duration:** ~4-5 hours

**Tasks:**
1. Write `tests/test_integration_end_to_end.py` - Full workflow tests
2. Test: Bootstrap → Create tasks → List → Complete → Git sync
3. Test: Git workflow (commit JSONL, pull, import)
4. Test: Dependency workflow (create, block, ready)
5. Test: Error recovery (corrupt database, rebuild from JSONL)

**Success Criteria:**
- All integration scenarios pass
- Git sync workflow verified
- Dependency graph workflow verified
- Error recovery workflow verified
- Performance: 1000 tasks < 100ms list time

**Scenarios:**
1. **End-to-end workflow:**
   - Bootstrap project
   - Create 5 tasks
   - Add dependencies (A blocks B)
   - Mark A complete
   - Verify B appears in ready list
   - Export to JSONL
   - Commit and push

2. **Git sync workflow:**
   - User A creates tasks, commits JSONL, pushes
   - User B pulls, imports JSONL
   - User B updates tasks, commits JSONL, pushes
   - User A pulls, imports JSONL
   - Verify both have same state

3. **Error recovery:**
   - Corrupt SQLite database
   - Run `oos task import .oos/tasks/export.jsonl`
   - Verify database rebuilt

**Performance Tests:**
- 1000 tasks: list < 100ms
- 1000 tasks: ready < 50ms
- 1000 tasks: export < 200ms
- 1000 tasks: import < 500ms

---

## Phase 11: Documentation & Polish

**Duration:** ~3-4 hours

**Tasks:**
1. Update main README.md - Add task system section
2. Create TASK_SYSTEM_GUIDE.md - Comprehensive user guide
3. Update CLAUDE.md - Document slash commands
4. Add examples to CLI `--help` text
5. Final code review: check against .claude_code_rules

**Success Criteria:**
- README clearly explains task system
- User guide has examples for every command
- CLAUDE.md updated with `/task` commands
- All `--help` text comprehensive
- Code follows all philosophy principles

**Documentation Sections:**
- Quick start guide
- CLI command reference
- Slash command reference
- Git sync workflow
- Troubleshooting
- Examples for common workflows

---

## Checkpoint Rhythm

Show progress report every 5 completed tasks:

**Report Format:**
```
✅ Phase X: Tasks [N-M] complete

Directory tree:
[show relevant structure]

Test results:
✅ XX/XX tests passing
- test_models.py: 12/12 ✅
- test_database.py: 15/15 ✅
- test_cli.py: 0/0 (not yet implemented)

What works:
- Task models: ✅
- SQLite CRUD: ✅
- JSONL export: 🚧 in progress

Progress: 25% (10/40 total tasks)

Next 3 tasks:
1. Implement JSONL import
2. Add timestamp merge logic
3. Write import tests

Continuing autonomously...
```

---

## Completion Criteria - Stop When:

- ✅ All 11 phases complete
- ✅ All tests passing (unit + integration)
- ✅ All CLI commands functional
- ✅ Slash commands work in Claude Code
- ✅ Bootstrap integration complete
- ✅ Archon keep-alive system deployed
- ✅ Documentation comprehensive
- ✅ Everything from PRD implemented
- ✅ No TODO comments in code
- ✅ No modules exceed 300 lines
- ✅ Philosophy principles enforced

---

## Risk Mitigation

**Risk 1: Breaking Existing OOS**
- Mitigation: Task system is completely optional
- Mitigation: All new code in `src/oos_task_system/` subdirectory
- Mitigation: Config flag `tasks.enabled: false` to disable

**Risk 2: Git Merge Conflicts in JSONL**
- Mitigation: One task per line (line-based conflicts easy to resolve)
- Mitigation: Timestamp-based merge on import
- Mitigation: Documentation on resolving conflicts

**Risk 3: Performance with Many Tasks**
- Mitigation: SQLite indexes on status, created, updated
- Mitigation: Performance tests in Phase 10
- Mitigation: Optimize if tests fail

**Risk 4: SQLite Database Corruption**
- Mitigation: JSONL export after every change
- Mitigation: Can rebuild from JSONL
- Mitigation: Document recovery procedure

---

## Success Metrics

When build is complete:
- ✅ Can create tasks via CLI
- ✅ Can create tasks via slash commands in Claude Code
- ✅ Tasks travel with git repo via JSONL
- ✅ AI agents can see ready work
- ✅ Archon stays alive (no Supabase downtime)
- ✅ Bootstrap creates task system automatically
- ✅ All tests pass (90%+ coverage)
- ✅ Documentation comprehensive
- ✅ No breaking changes to existing OOS

---

*This implementation plan breaks the PRD into 40+ specific, testable tasks across 11 phases. Each phase builds on the previous, ensuring incremental progress toward the complete system.*
