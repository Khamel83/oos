# OOS - Organized Operational Setup

## CRITICAL: Archon Integration

**READ `docs/ARCHON_INTEGRATION.md` FIRST BEFORE RESPONDING TO ANY REQUEST**

This project REQUIRES explicit use of Archon tools. Do not proceed without understanding Archon integration.

Key rules:
1. Search Archon before answering documentation questions
2. Check Archon tasks before suggesting work
3. Update Archon tasks when work is completed

## 🎯 CRITICAL: Read OOS Guidelines First
- **Read [docs/TESTING_PHILOSOPHY.md](docs/TESTING_PHILOSOPHY.md)** - Apply these learnings to ALL development
- **Read [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md)** - Understand the architecture before changing it
- **Read .agents/agents.md** - General development practices

## 🧠 Development Philosophy for OOS
1. **Simple over Complex**: If it's hard to understand, it's probably wrong
2. **Self-Documenting**: Every tool should explain what it does and why
3. **Modular Design**: Users should be able to use just what they need
4. **Test-Driven**: If you can't test it automatically, reconsider the approach
5. **User-Centric**: Ask "will users understand this?" before adding features

## 🧪 Recursive User-Acceptance Testing (RUAT)

**MANDATORY: Every feature must pass real-world user scenarios before marking tasks "done".**

### Task Completion Requirements

A task is ONLY complete when:
1. ✅ Technical implementation works
2. ✅ Code is documented
3. ✅ Unit tests pass
4. ✅ **User scenarios pass** ← MANDATORY REQUIREMENT
5. ✅ Integration with other features verified
6. ✅ Archon task updated to "done"

### Running User Scenarios

Before marking any task "review" or "done":

```bash
# Test the feature from user perspective
./bin/test-user-scenarios [feature-name]

# Examples
./bin/test-user-scenarios help-me
./bin/test-user-scenarios start-coding
./bin/test-user-scenarios screenshot
```

If ANY scenario fails:
- Document the UX issue in ruat_failures.log
- Create new task to fix UX problem
- Do NOT mark original task complete
- Fix the user experience
- Re-test scenarios until they pass

### Creating Scenarios for New Features

Every new feature requires `tests/scenarios/[feature].scenarios`:

1. Document realistic user workflows
2. Include edge cases users encounter
3. Test error handling from user perspective
4. Validate integration with existing features
5. Check that feature is discoverable
6. Verify help/documentation is clear

### User-Centric Validation Checklist

For every feature, validate:
- [ ] User can discover the feature (documented, /help shows it)
- [ ] User understands how to use it (clear examples)
- [ ] User's most common use case works perfectly
- [ ] User's edge cases are handled gracefully
- [ ] Errors give helpful, actionable messages
- [ ] Feature integrates naturally with workflow
- [ ] No surprise behavior or confusion
- [ ] Works for both expert and novice users

### RUAT Integration with Archon Workflow

Updated task status flow:
```
todo → doing → technical-complete → ruat-validation → review → done
```

**New status: "technical-complete"** means code works but user scenarios not validated yet.

Task only moves to "review" after RUAT passes completely.

## 🚀 Consolidated Command Structure

**OOS now uses 10 consolidated commands instead of 45 individual commands.**

### Core Commands (Use These)

| Command | Purpose | Consolidates |
|---------|---------|--------------|
| `/dev` | Development environment | /dev-setup, /startup-check, /modules, /reload-commands |
| `/test` | Testing & validation | /test-debug, /test-connection, /test-user-scenarios |
| `/fix` | Code quality | /auto-fix, /optimize, /doc-check |
| `/think` | Problem solving | /brain-dump, /clarify, /solve, /meta-ai |
| `/workflow` | Process orchestration | /agentic-workflow, /complete-workflow, /idea-to-done |
| `/project` | Infrastructure | /create-project, /provision, /update-oos, /oos-refresh |
| `/op` | 1Password operations | All /op-* commands |
| `/archon` | Knowledge base | /archon-research, /archon-status |
| `/task` | Task management | /archon-task-start, /archon-complete |
| `/check` | System validation | /security-review, /context-stats |

### Command Usage

Each command has subcommands. Use `help` to discover them:

```bash
/dev help          # Shows: setup, check, modules, refresh
/test help         # Shows: debug, connection, scenarios
/fix help          # Shows: auto, optimize, docs
/think help        # Shows: dump, clarify, solve, meta
```

### Migration Guide

Run `/migrate-commands` or `./bin/migrate-commands.sh` for complete migration mapping.

**Benefits:**
- 78% fewer commands to remember (45 → 10)
- Logical grouping by function
- Consistent interface
- Better discoverability
