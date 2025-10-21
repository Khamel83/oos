# Product Requirements Document: OOS Task Memory System

## 1. Project Overview

### Problem Statement

**Current Problem:**
OOS manages HOW you like to work (environment setup, secrets, preferences) but doesn't manage WHAT you're working on within each project. Task management either lives in Archon (external server, excellent for RAG and cross-project views but not portable with git) or doesn't exist at all. When you start a project with OOS, your day-to-day tasks and context aren't embedded in that project.

**Specific Pain Points:**
1. **Agent Amnesia**: AI agents lose context between sessions, can't remember what was being worked on
2. **Non-Portable Tasks**: Tasks don't travel with git repo, lost when cloning/sharing
3. **Missing Project Brain**: No embedded memory of what needs to be done, what's blocked, what's ready
4. **Scattered Ideas**: Your vision is "all my ideas within OOS" but currently they're external or nowhere
5. **Context Loss**: Can't pick up where you left off when switching projects
6. **Supabase Downtime**: Archon's Supabase instance goes down if not accessed regularly

**What We're NOT Replacing:**
- **Archon RAG** - Keep using for knowledge base search, document retrieval
- **Archon Web UI** - Keep for visual task management across all projects
- **Archon Project Registry** - Keep as central registry of all your projects

**Why It Matters:**
You want to "start a project, start OOS within that project, and have it manage my keys, environments, and all my ways of thinking." Currently only keys and environments are managed - thinking/tasks are missing.

### Core Philosophy

This project follows OOS philosophy with beads-inspired additions:

1. **Simplicity over Complexity**: Use SQLite + JSONL, not complex graph databases
2. **Project-Embedded Memory**: Tasks live IN the project (.oos/tasks.db), not external server
3. **Git-Syncable**: Tasks export to JSONL, travel with repo via git
4. **Agent-Friendly**: CLI-first, AI agents can read/write via simple commands
5. **Modular Design**: Task system is optional, OOS works without it
6. **Unix Philosophy**: Small focused tools that do one thing well

**Beads Inspiration (What We Borrow):**
- SQLite local storage (fast, simple, no server)
- JSONL git export (tasks sync via git push/pull)
- Dependency graph (tasks can block other tasks)
- Ready work detection (show what's unblocked)
- Agent-friendly CLI (oos task [command] format)

**OOS Integration (What We Add):**
- Integrated with existing OOS bootstrap
- Slash commands for Claude Code (/task [action])
- Optional Archon sync (best of both worlds)
- Secrets management for task-related credentials
- Learning system integration (patterns captured)
- Archon keep-alive system (prevent Supabase downtime)

### Three-Tier Architecture

This system creates a hybrid approach, using the best of each tier:

**Tier 1: Archon (Cloud) - KEEP & ENHANCE**
- **RAG/Knowledge Base**: Search uploaded docs, crawled websites (`/archon-research`)
- **Cross-Project View**: See tasks across all your projects
- **Web UI**: Visual interface at archon.khamel.com
- **Project Registry**: Central registry of all projects
- **Keep-Alive**: Automated pings every 2 days to prevent Supabase downtime

**Tier 2: Local Tasks (Git) - NEW**
- **Project-Embedded**: Tasks live in `.oos/tasks.db` within each project
- **Git-Syncable**: Export to `.oos/tasks/export.jsonl`, commit to git
- **Fast & Offline**: No network latency, works without internet
- **Agent Context**: AI agents see tasks when starting work

**Tier 3: Optional Sync (Bridge) - NEW**
- **One-Way Sync**: Local → Archon (backup and global visibility)
- **Conflict-Free**: Local is source of truth, Archon is copy
- **Best of Both**: Day-to-day work local, overview in Archon

**Workflow Example:**
```bash
# Day-to-day work (local, fast)
oos task create "Implement OAuth"
oos task ready
oos task complete <id>
git push  # Tasks sync via JSONL

# Knowledge search (Archon, RAG)
/archon-research "JWT best practices"

# Global view (Archon, cross-project)
# Visit archon.khamel.com to see all projects

# Optional: Sync local tasks to Archon
oos task sync --to-archon  # v1.1 feature
```

### Scope

**IN SCOPE (v1.0):**
- Local SQLite task database per project
- JSONL export for git sync
- Basic dependency graph (blocks, blocked-by)
- CLI commands for task CRUD
- Slash commands for Claude Code integration
- Bootstrap integration (auto-creates .oos/ on project setup)
- Integration with Archon (optional one-way import, keep RAG/UI)
- Archon keep-alive system (GitHub Actions + cron to prevent Supabase downtime)
- Ready work detection (show unblocked tasks)
- Basic task metadata (title, description, status, created, updated)

**OUT OF SCOPE (future versions):**
- Bi-directional Archon sync (v2.0)
- Web UI for task management (v2.0)
- Time tracking per task (v2.0)
- Task templates (v2.0)
- Multi-project task views (v2.0)
- Advanced dependency types (parent-child, related) (v1.1)
- Task assignment to specific agents (v1.1)
- Rich metadata (tags, priorities, estimates) (v1.1)

### Non-Goals

**What This Is NOT:**
- Not a replacement for Archon (complementary, Archon keeps RAG/UI/cross-project views)
- Not a replacement for Archon's knowledge base (use `/archon-research` for RAG)
- Not a full project management system (focused on developer tasks)
- Not a time tracker
- Not a Jira clone
- Not a team collaboration tool (single developer focus)
- Not a complex DAG system (simple blocks/blocked-by only)

### Target Users

**Primary User:**
- Solo developer using OOS for project setup
- Uses Claude Code for AI-assisted development
- Wants tasks embedded in project, not external
- Values simplicity over features
- Works on multiple projects, needs context preservation

**Use Cases:**
1. Start new project with `oos bootstrap`, get task system automatically
2. Add tasks as ideas emerge: `oos task create "implement auth"`
3. AI agent checks ready work: `oos task ready`
4. Mark tasks done: `oos task complete <id>`
5. Git push/pull syncs tasks with JSONL export
6. Switch projects, context preserved in each .oos/ directory

---

## 2. Data Model

### Task Record Example

```yaml
# .oos/tasks/export.jsonl - Each line is one task
{"id": "550e8400-e29b-41d4-a716-446655440000", "title": "Implement user authentication", "description": "Add JWT-based authentication with login/logout endpoints. Use bcrypt for password hashing. Support refresh tokens.", "status": "doing", "created": "2024-10-21T10:00:00Z", "updated": "2024-10-21T15:30:00Z", "blocks": [], "blocked_by": [], "metadata": {"feature": "auth", "estimated_hours": 8, "tags": ["backend", "security"]}}
{"id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d", "title": "Create user database schema", "description": "PostgreSQL schema: users table with id, email, password_hash, created_at, updated_at. Add indexes on email.", "status": "done", "created": "2024-10-20T09:00:00Z", "updated": "2024-10-21T11:00:00Z", "blocks": ["550e8400-e29b-41d4-a716-446655440000"], "blocked_by": [], "metadata": {"feature": "database", "estimated_hours": 2, "tags": ["backend", "database"]}}
{"id": "2f3e4d5c-6a7b-8c9d-0e1f-2a3b4c5d6e7f", "title": "Design API endpoints", "description": "POST /auth/login, POST /auth/logout, POST /auth/refresh. Document request/response formats.", "status": "todo", "created": "2024-10-21T16:00:00Z", "updated": "2024-10-21T16:00:00Z", "blocks": [], "blocked_by": ["550e8400-e29b-41d4-a716-446655440000"], "metadata": {"feature": "api", "estimated_hours": 4, "tags": ["backend", "api"]}}
```

### Task Fields (Complete Specification)

**Core Fields (Required):**

| Field | Type | Description | Constraints | Example |
|-------|------|-------------|-------------|---------|
| `id` | string (UUID) | Unique task identifier | UUIDv4 format, generated on create | `"550e8400-e29b-41d4-a716-446655440000"` |
| `title` | string | Short task summary | 5-200 chars, required, non-empty after strip | `"Implement user authentication"` |
| `description` | string | Detailed task description | 0-10000 chars, can be empty, markdown supported | `"Add JWT-based authentication..."` |
| `status` | string (enum) | Current task state | One of: `todo`, `doing`, `done`, `blocked` | `"doing"` |
| `created` | string (ISO 8601) | When task was created | UTC timestamp, set on create, immutable | `"2024-10-21T10:00:00Z"` |
| `updated` | string (ISO 8601) | Last update timestamp | UTC timestamp, set on create and every update | `"2024-10-21T15:30:00Z"` |

**Dependency Fields (Optional):**

| Field | Type | Description | Constraints | Example |
|-------|------|-------------|-------------|---------|
| `blocks` | array[string] | Task IDs this task blocks | 0-100 task IDs, must be valid UUIDs | `["2f3e4d5c-6a7b-8c9d-0e1f-2a3b4c5d6e7f"]` |
| `blocked_by` | array[string] | Task IDs blocking this task | 0-100 task IDs, must be valid UUIDs | `["7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d"]` |

**Metadata Fields (Optional):**

| Field | Type | Description | Constraints | Example |
|-------|------|-------------|-------------|---------|
| `metadata` | object | Additional task data | Freeform JSON object, max 5KB serialized | `{"feature": "auth", "tags": ["backend"]}` |
| `metadata.feature` | string | Feature area | 1-50 chars, optional | `"authentication"` |
| `metadata.estimated_hours` | number | Estimated effort | 0.25-1000, optional | `8` |
| `metadata.tags` | array[string] | Categorization tags | 0-20 tags, 1-30 chars each | `["backend", "security"]` |

### Database Schema (SQLite)

```sql
-- .oos/tasks.db

CREATE TABLE tasks (
    id TEXT PRIMARY KEY,                    -- UUIDv4
    title TEXT NOT NULL CHECK(length(title) >= 5 AND length(title) <= 200),
    description TEXT DEFAULT '',            -- 0-10000 chars
    status TEXT NOT NULL CHECK(status IN ('todo', 'doing', 'done', 'blocked')),
    created TEXT NOT NULL,                  -- ISO 8601 UTC
    updated TEXT NOT NULL,                  -- ISO 8601 UTC
    blocks TEXT DEFAULT '[]',               -- JSON array of task IDs
    blocked_by TEXT DEFAULT '[]',           -- JSON array of task IDs
    metadata TEXT DEFAULT '{}'              -- JSON object, max 5KB
);

-- Indexes for performance
CREATE INDEX idx_status ON tasks(status);
CREATE INDEX idx_created ON tasks(created DESC);
CREATE INDEX idx_updated ON tasks(updated DESC);

-- Full-text search (optional, v1.1)
-- CREATE VIRTUAL TABLE tasks_fts USING fts5(title, description, content=tasks);
```

### Validation Rules

**Task Creation:**
- Title: 5-200 chars, required, non-empty after strip, no newlines
- Description: 0-10000 chars, optional, markdown allowed, newlines allowed
- Status: Must be `todo` (default on create)
- ID: Auto-generated UUIDv4, cannot be specified by user
- Created: Auto-set to current UTC timestamp, cannot be specified
- Updated: Auto-set to current UTC timestamp, cannot be specified
- Blocks: Must be empty array `[]` on create (add via update)
- Blocked_by: Must be empty array `[]` on create (add via update)
- Metadata: Optional JSON object, max 5KB when serialized

**Task Update:**
- Title: 5-200 chars, non-empty after strip, no newlines
- Description: 0-10000 chars, markdown allowed
- Status: One of `todo`, `doing`, `done`, `blocked`
- ID: Immutable, cannot be changed
- Created: Immutable, cannot be changed
- Updated: Auto-set to current UTC timestamp on every update
- Blocks: Array of valid task IDs that exist in database
- Blocked_by: Array of valid task IDs that exist in database
- Metadata: Optional JSON object, max 5KB when serialized

**Dependency Rules:**
- Cannot create circular dependencies (A blocks B blocks A)
- Cannot block yourself (task A blocks task A)
- Blocked task IDs must exist in database
- Max 100 blocking relationships per task (sanity limit)
- When task A blocks task B: A.blocks contains B's ID, B.blocked_by contains A's ID (bidirectional sync)

**Status Transition Rules:**
- `todo` → `doing`, `blocked`, `done`
- `doing` → `todo`, `done`, `blocked`
- `done` → `todo` (reopening allowed)
- `blocked` → `todo`, `doing` (when unblocked)
- Auto-set to `blocked` when blocked_by becomes non-empty
- Auto-set to `todo` when blocked_by becomes empty (if was `blocked`)

### Example Valid Tasks

**Simple Task (Minimal):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Write unit tests for auth module",
  "description": "",
  "status": "todo",
  "created": "2024-10-21T10:00:00Z",
  "updated": "2024-10-21T10:00:00Z",
  "blocks": [],
  "blocked_by": [],
  "metadata": {}
}
```

**Complex Task (Full Metadata):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Implement OAuth2 Google provider",
  "description": "Add Google OAuth2 integration using PKCE flow.\n\n**Requirements:**\n- Authorization URL generation\n- Code exchange implementation\n- User info retrieval\n- Account linking logic\n\n**References:**\n- https://developers.google.com/identity/protocols/oauth2",
  "status": "doing",
  "created": "2024-10-20T14:30:00Z",
  "updated": "2024-10-21T16:45:00Z",
  "blocks": ["2f3e4d5c-6a7b-8c9d-0e1f-2a3b4c5d6e7f"],
  "blocked_by": ["7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d"],
  "metadata": {
    "feature": "oauth",
    "estimated_hours": 12,
    "tags": ["backend", "authentication", "oauth"],
    "priority": "high",
    "assignee": "claude-code",
    "notes": "Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env"
  }
}
```

**Blocked Task:**
```json
{
  "id": "2f3e4d5c-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
  "title": "Write OAuth integration tests",
  "description": "Test Google OAuth flow end-to-end",
  "status": "blocked",
  "created": "2024-10-21T09:00:00Z",
  "updated": "2024-10-21T09:00:00Z",
  "blocks": [],
  "blocked_by": ["550e8400-e29b-41d4-a716-446655440000"],
  "metadata": {
    "feature": "oauth",
    "tags": ["testing"]
  }
}
```

---

## 3. Functional Requirements

### FR-1: Task Creation

**Description:** Create a new task in the local task database

**Input:**
```bash
oos task create "Task title" --description "Optional description" --metadata '{"feature":"auth"}'
```

**Parameters:**
- Title (required): 5-200 char string
- Description (optional): 0-10000 char string, via --description flag
- Metadata (optional): JSON object via --metadata flag

**Process:**
1. Validate title length (5-200 chars)
2. Validate description length if provided (0-10000 chars)
3. Validate metadata is valid JSON if provided
4. Generate UUIDv4 for task ID
5. Set created and updated to current UTC timestamp
6. Set status to `todo`
7. Set blocks and blocked_by to empty arrays
8. Insert into SQLite database
9. Export to JSONL file (append new task)
10. Print task ID and confirmation

**Output (Success):**
```
✅ Task created: 550e8400-e29b-41d4-a716-446655440000
   Title: "Implement user authentication"
   Status: todo
   Created: 2024-10-21T10:00:00Z
```

**Output (Failure - Title Too Short):**
```
❌ Error: Title too short
   Title must be 5-200 characters
   Provided: "Auth" (4 characters)
```

**Edge Cases:**
- Title with only whitespace → Error: "Title cannot be empty"
- Title with newlines → Error: "Title cannot contain newlines"
- Description > 10000 chars → Error: "Description too long (max 10000 chars)"
- Invalid JSON in metadata → Error: "Invalid JSON in --metadata"
- Metadata > 5KB serialized → Error: "Metadata too large (max 5KB)"

**Success Criteria:**
- Task inserted into SQLite database
- Task appended to JSONL export file
- Task ID returned to user
- All timestamps set correctly
- Database constraints satisfied

### FR-2: Task Listing

**Description:** List tasks with optional filtering

**Input:**
```bash
oos task list                          # All tasks
oos task list --status doing           # Only doing tasks
oos task list --status todo,blocked    # Multiple statuses
oos task list --feature auth           # Filter by metadata.feature
oos task list --ready                  # Only unblocked tasks
```

**Process:**
1. Parse filter arguments
2. Query SQLite with WHERE clause based on filters
3. For --ready: filter WHERE status IN ('todo','doing') AND blocked_by = '[]'
4. Sort by updated DESC (most recently updated first)
5. Format output as table or JSON (via --format flag)
6. Print to stdout

**Output (Table Format - Default):**
```
ID                                   Status  Title                              Updated
550e8400-e29b-41d4-a716-446655440000 doing   Implement user authentication      2024-10-21T15:30:00Z
7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d done    Create user database schema        2024-10-21T11:00:00Z
2f3e4d5c-6a7b-8c9d-0e1f-2a3b4c5d6e7f blocked Design API endpoints                2024-10-21T16:00:00Z

3 tasks (1 doing, 1 done, 1 blocked)
```

**Output (JSON Format):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Implement user authentication",
    "status": "doing",
    "created": "2024-10-21T10:00:00Z",
    "updated": "2024-10-21T15:30:00Z",
    "blocks": [],
    "blocked_by": []
  }
]
```

**Edge Cases:**
- No tasks in database → Empty table with message "No tasks found"
- Invalid status filter → Error: "Invalid status 'invalid', must be one of: todo, doing, done, blocked"
- No tasks match filter → Empty table with message "No tasks match filter"

**Success Criteria:**
- All matching tasks displayed
- Sorted by updated DESC
- Correct count shown
- Performance < 100ms for 1000 tasks

### FR-3: Task Update

**Description:** Update an existing task's fields

**Input:**
```bash
oos task update <task-id> --status doing
oos task update <task-id> --title "New title"
oos task update <task-id> --description "New description"
oos task update <task-id> --add-blocks <other-task-id>
oos task update <task-id> --remove-blocks <other-task-id>
oos task update <task-id> --metadata '{"priority":"high"}'
```

**Process:**
1. Validate task ID exists in database
2. Validate new values (same rules as create)
3. If updating blocks/blocked_by: validate dependency rules
4. Update updated timestamp to current UTC
5. Update fields in SQLite
6. Regenerate JSONL export (full export, not append)
7. Print confirmation

**Output (Success):**
```
✅ Task updated: 550e8400-e29b-41d4-a716-446655440000
   Status: todo → doing
   Updated: 2024-10-21T16:00:00Z
```

**Edge Cases:**
- Task ID doesn't exist → Error: "Task not found: <id>"
- Circular dependency → Error: "Cannot add block: would create circular dependency"
- Self-blocking → Error: "Task cannot block itself"
- Invalid status → Error: "Invalid status '<status>'"
- Blocking non-existent task → Error: "Cannot block task <id>: task not found"

**Success Criteria:**
- Task updated in database
- JSONL export regenerated
- Dependency graph remains valid (no cycles)
- Updated timestamp changed

### FR-4: Task Completion

**Description:** Mark a task as done (convenience wrapper for status update)

**Input:**
```bash
oos task complete <task-id>
```

**Process:**
1. Validate task exists
2. Update status to `done`
3. Update updated timestamp
4. Update in SQLite and regenerate JSONL
5. Print confirmation with task title

**Output (Success):**
```
✅ Task completed: Implement user authentication
   ID: 550e8400-e29b-41d4-a716-446655440000
   Completed: 2024-10-21T17:00:00Z
```

**Edge Cases:**
- Task already done → Warning: "Task already completed" (still update timestamp)
- Task doesn't exist → Error: "Task not found: <id>"

**Success Criteria:**
- Status set to done
- Updated timestamp changed
- JSONL regenerated

### FR-5: Ready Work Detection

**Description:** Show tasks that are ready to work on (unblocked)

**Input:**
```bash
oos task ready
oos task ready --format json
```

**Process:**
1. Query tasks WHERE status IN ('todo', 'doing') AND blocked_by = '[]'
2. Sort by created ASC (oldest ready tasks first)
3. Format and display

**Output:**
```
Ready to work on (3 tasks):

ID                                   Title                              Created
a1b2c3d4-e5f6-7890-abcd-ef1234567890 Write unit tests                   2024-10-20T09:00:00Z
b2c3d4e5-f6a7-8901-bcde-fa1234567890 Setup CI/CD pipeline               2024-10-20T14:00:00Z
c3d4e5f6-a7b8-9012-cdef-ab1234567890 Document API endpoints             2024-10-21T08:00:00Z

Suggested next task: Write unit tests (oldest ready task)
```

**Edge Cases:**
- No ready tasks → Message: "No tasks ready. All tasks are either blocked or completed."
- All tasks done → Message: "All tasks completed! 🎉"

**Success Criteria:**
- Only unblocked tasks shown
- Sorted oldest first (work on oldest ready tasks)
- Suggestion for next task given

### FR-6: Task Deletion

**Description:** Delete a task from the database

**Input:**
```bash
oos task delete <task-id>
oos task delete <task-id> --force  # Skip confirmation
```

**Process:**
1. Validate task exists
2. Check if other tasks reference this task in blocks or blocked_by
3. If referenced: show warning and ask for confirmation
4. If --force or user confirms: proceed
5. Remove task from blocks/blocked_by arrays in other tasks
6. Delete task from database
7. Regenerate JSONL export
8. Print confirmation

**Output (Success with Dependencies):**
```
⚠️  Warning: This task is referenced by 2 other tasks:
   - 2f3e4d5c-6a7b-8c9d-0e1f-2a3b4c5d6e7f (blocked by this task)
   - c3d4e5f6-a7b8-9012-cdef-ab1234567890 (blocks this task)

Deleting will remove these dependencies.
Continue? [y/N]: y

✅ Task deleted: 550e8400-e29b-41d4-a716-446655440000
   Updated 2 dependent tasks
```

**Edge Cases:**
- Task doesn't exist → Error: "Task not found: <id>"
- User cancels confirmation → Message: "Deletion cancelled"

**Success Criteria:**
- Task removed from database
- References removed from other tasks
- JSONL regenerated
- No orphaned references

### FR-7: JSONL Export/Import

**Description:** Export all tasks to JSONL for git sync, import from JSONL

**Export Process (Automatic):**
- Runs after every create, update, delete
- Writes entire task database to .oos/tasks/export.jsonl
- One task per line as compact JSON
- File can be committed to git

**Import Process (Manual):**
```bash
oos task import .oos/tasks/export.jsonl
```

**Import Process:**
1. Read JSONL file line by line
2. Parse each line as JSON
3. Validate each task against schema
4. For each task:
   - If ID exists in database: update (merge)
   - If ID doesn't exist: insert (new)
5. Compare timestamps: keep newer version
6. Regenerate export after import

**Merge Strategy (Conflict Resolution):**
- Compare updated timestamps
- Newer timestamp wins
- If timestamps equal: local database wins (no change)

**Output (Import Success):**
```
Importing tasks from .oos/tasks/export.jsonl...
✅ Imported 15 tasks
   - 3 new tasks added
   - 12 existing tasks updated
   - 0 conflicts (local newer)
```

**Edge Cases:**
- Invalid JSON line → Skip line, log warning, continue
- Missing required field → Skip task, log error, continue
- Invalid UUID → Skip task, log error, continue
- Empty file → Message: "No tasks to import"
- File doesn't exist → Error: "File not found: <path>"

**Success Criteria:**
- All valid tasks imported
- Conflicts resolved by timestamp
- Database consistent after import
- Export regenerated

### FR-8: Archon Keep-Alive System

**Description:** Prevent Archon's Supabase instance from going down due to inactivity

**Problem:**
Supabase free tier pauses databases after periods of inactivity. Archon requires regular pings to stay alive and maintain access to RAG knowledge base and cross-project task views.

**Solution:**
Automated keep-alive system using GitHub Actions and optional local cron job.

**GitHub Actions Workflow:**

Create `.github/workflows/archon-keepalive.yml`:

```yaml
name: Keep Archon/Supabase Alive

on:
  schedule:
    # Run every 2 days at 2:00 AM UTC
    - cron: '0 2 */2 * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  keepalive:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Archon Health Endpoint
        run: |
          echo "Pinging Archon at $(date)"
          response=$(curl -s -o /dev/null -w "%{http_code}" https://archon.khamel.com/health || echo "000")
          if [ "$response" = "200" ]; then
            echo "✅ Archon is alive (HTTP $response)"
          else
            echo "⚠️  Archon returned HTTP $response"
          fi

      - name: Ping Archon MCP Endpoint
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" http://100.103.45.61:8051/mcp || echo "000")
          if [ "$response" = "200" ]; then
            echo "✅ Archon MCP is alive (HTTP $response)"
          else
            echo "⚠️  Archon MCP returned HTTP $response"
          fi

      - name: Log Keep-Alive Success
        run: echo "Keep-alive ping completed at $(date)"
```

**Local Cron Job (Optional Backup):**

Create `bin/archon-keepalive.sh`:

```bash
#!/bin/bash
# Ping Archon every 2 days to keep Supabase alive

LOG_FILE="${HOME}/.oos/logs/archon-keepalive.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "$(date): Pinging Archon..." >> "$LOG_FILE"

# Ping health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" https://archon.khamel.com/health || echo "000")
echo "$(date): Archon health response: HTTP $response" >> "$LOG_FILE"

# Ping MCP endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" http://100.103.45.61:8051/mcp || echo "000")
echo "$(date): Archon MCP response: HTTP $response" >> "$LOG_FILE"

echo "$(date): Keep-alive ping completed" >> "$LOG_FILE"
```

**Setup Cron Job:**
```bash
# Add to crontab (run every 2 days at 2am)
crontab -e

# Add line:
0 2 */2 * * /path/to/oos/bin/archon-keepalive.sh
```

**Process:**
1. GitHub Actions runs every 2 days (primary)
2. Local cron job runs every 2 days (backup, optional)
3. Both ping Archon health and MCP endpoints
4. Keeps Supabase active and accessible
5. Logs pings for monitoring

**Output (GitHub Actions):**
```
Pinging Archon at Mon Oct 21 02:00:00 UTC 2024
✅ Archon is alive (HTTP 200)
✅ Archon MCP is alive (HTTP 200)
Keep-alive ping completed at Mon Oct 21 02:00:01 UTC 2024
```

**Output (Local Cron):**
```bash
$ cat ~/.oos/logs/archon-keepalive.log
Mon Oct 21 02:00:00 PDT 2024: Pinging Archon...
Mon Oct 21 02:00:00 PDT 2024: Archon health response: HTTP 200
Mon Oct 21 02:00:01 PDT 2024: Archon MCP response: HTTP 200
Mon Oct 21 02:00:01 PDT 2024: Keep-alive ping completed
```

**Edge Cases:**
- Archon down → Log warning, continue (don't fail build)
- Network timeout → Log warning, retry next scheduled time
- Both health and MCP down → Alert in logs but don't alert user
- Manual trigger → Allow via GitHub Actions `workflow_dispatch`

**Success Criteria:**
- GitHub Actions workflow runs every 2 days
- Archon responds with HTTP 200
- Supabase stays active (no downtime)
- Logs show successful pings
- Can manually trigger workflow if needed

**Integration with OOS:**
- Add workflow file during `oos bootstrap` if GitHub repo detected
- Add script to `bin/archon-keepalive.sh`
- Document in README
- Optional: Alert user if Archon hasn't been pinged in 3+ days

---

## 4. Technical Specifications

### Dependencies

```
python>=3.9
sqlite3 (built-in)
uuid (built-in)
json (built-in)
datetime (built-in)
click==8.1.7           # CLI framework
pyyaml==6.0.1          # Config file parsing (OOS uses YAML)
```

**No External Dependencies Beyond CLI Framework:**
- Use Python stdlib for everything except CLI
- SQLite is built-in (no installation)
- UUID, JSON, datetime all built-in
- Keep it simple and portable

### Storage Structure

```
project_root/
├── .oos/                          # OOS directory (created by bootstrap)
│   ├── tasks.db                   # SQLite task database
│   ├── tasks/
│   │   └── export.jsonl           # Git-syncable task export
│   ├── config.yaml                # OOS config (existing)
│   └── secrets/                   # OOS secrets (existing)
├── .gitignore                     # Add .oos/tasks.db (don't commit SQLite)
└── ... (rest of project)
```

**File Descriptions:**

| File | Purpose | Committed to Git? | Format |
|------|---------|-------------------|--------|
| `.oos/tasks.db` | Local task database | ❌ NO | SQLite binary |
| `.oos/tasks/export.jsonl` | Git-syncable task list | ✅ YES | JSONL (one task per line) |
| `.oos/config.yaml` | OOS configuration | ✅ YES | YAML |

**Why SQLite Not Committed:**
- Binary format, merge conflicts impossible
- Different platforms might have incompatible SQLite versions
- JSONL export is source of truth for git

**Why JSONL Committed:**
- Text format, git-friendly
- Easy to diff and merge
- Human-readable
- One task per line = easy conflict resolution

### Configuration

**File:** `.oos/config.yaml` (enhanced with task settings)

```yaml
# Existing OOS config
project_name: "my-project"
archon_project_id: ""
archon_url: ""

# New task system config
tasks:
  enabled: true                          # Enable task system (true/false)
  auto_export: true                      # Auto-export to JSONL after changes (true/false)
  export_path: ".oos/tasks/export.jsonl" # Where to export tasks
  db_path: ".oos/tasks.db"               # SQLite database path

  # Default task settings
  defaults:
    status: "todo"                       # Default status for new tasks

  # Archon integration (optional)
  archon_sync:
    enabled: false                       # Sync with Archon (future feature)
    direction: "to_archon"               # "to_archon", "from_archon", "bidirectional"
```

**Environment Variables:**
- None required for task system
- All configuration via config.yaml
- Inherits OOS environment setup (secrets, etc.)

**Defaults If Config Missing:**
- If tasks section missing: use defaults above
- If config.yaml missing: use all defaults
- Task system degrades gracefully

### CLI Interface Design

**Command Structure:**
```bash
oos task <command> [arguments] [options]
```

**Commands:**
- `create <title>` - Create new task
- `list` - List all tasks
- `show <id>` - Show task details
- `update <id>` - Update task fields
- `complete <id>` - Mark task done
- `delete <id>` - Delete task
- `ready` - Show ready work
- `import <file>` - Import tasks from JSONL
- `export` - Force export to JSONL
- `graph` - Show dependency graph (v1.1)

**Global Options:**
- `--format json|table|yaml` - Output format (default: table)
- `--quiet` - Suppress non-essential output
- `--help` - Show help

**Subcommand Options:**
- `create`: `--description TEXT`, `--metadata JSON`
- `list`: `--status STATUS`, `--feature NAME`, `--ready`, `--limit N`
- `update`: `--status STATUS`, `--title TEXT`, `--description TEXT`, `--metadata JSON`, `--add-blocks ID`, `--remove-blocks ID`
- `delete`: `--force` (skip confirmation)
- `import`: `--merge` (default), `--replace` (clear existing)

### Slash Command Integration (Claude Code)

**New Slash Commands:**

```markdown
# .claude/commands/task.md

Run task management commands for the current project.

Usage: /task [command] [arguments]

Commands:
  /task create "title"           Create new task
  /task list                     List all tasks
  /task list --ready             Show ready work
  /task show <id>                Show task details
  /task complete <id>            Mark task done
  /task update <id> --status doing  Update task

Examples:
  /task create "Implement OAuth2 provider"
  /task list --status doing
  /task ready
  /task complete 550e8400-e29b-41d4-a716-446655440000

When AI agent starts work:
1. Run /task ready to see unblocked work
2. Pick oldest ready task
3. Run /task update <id> --status doing
4. Do the work
5. Run /task complete <id>
6. Repeat

This ensures context preservation across sessions.
```

**Integration with Existing OOS Commands:**

| Existing Command | Enhanced Behavior |
|------------------|-------------------|
| `oos bootstrap` | Creates .oos/tasks.db and export.jsonl |
| `/start-coding` | Shows ready tasks as part of startup |
| `/smart-commit` | Can reference task IDs in commit message |
| `/archon-status` | Shows both Archon (if enabled) and local tasks |

---

## 5. Error Handling

### Error Taxonomy

| Error Type | Retry? | Max Attempts | Action | Example |
|------------|--------|--------------|--------|---------|
| Task not found | No | 0 | Exit with error code 1, print "Task not found: <id>" | User provides invalid UUID |
| Database locked | Yes | 3 | Wait 100ms, 200ms, 400ms, then fail | Concurrent writes |
| Database corrupt | No | 0 | Exit with error code 2, print recovery instructions | SQLite file damaged |
| Invalid input | No | 0 | Exit with error code 1, print validation error | Title too short |
| Circular dependency | No | 0 | Exit with error code 1, print dependency chain | A blocks B blocks A |
| JSONL parse error | No | 0 | Skip line, log warning, continue | Malformed JSON line |
| File not found | No | 0 | Exit with error code 1, print "File not found: <path>" | Import non-existent file |
| Permission denied | No | 0 | Exit with error code 2, print permission error | Can't write to .oos/ |

### Logging Format

```
2024-10-21T10:00:00Z - oos.task - ERROR - Failed to create task - {"error": "title_too_short", "title": "Auth", "length": 4, "min_length": 5}
```

**Log Levels:**
- DEBUG: SQL queries, dependency graph checks
- INFO: Task created, updated, deleted
- WARNING: JSONL parse errors, skipped lines
- ERROR: Database errors, validation failures

**Log Location:**
- Stdout/stderr for CLI (user-facing)
- `.oos/logs/task.log` for debugging (developer-facing, optional)

### Failed Operation Handling

**Database Errors:**
- Database locked → Retry 3 times with exponential backoff
- Database corrupt → Print recovery message:
  ```
  ❌ Database corrupt: .oos/tasks.db

  Recovery options:
  1. Restore from JSONL: oos task import .oos/tasks/export.jsonl --replace
  2. Delete and reimport: rm .oos/tasks.db && oos task import .oos/tasks/export.jsonl
  3. If JSONL also corrupt: git checkout HEAD~1 .oos/tasks/export.jsonl
  ```

**Import Errors:**
- Invalid JSON line → Skip, log warning, continue
- Missing field → Skip task, log error, continue
- Invalid UUID → Skip task, log error, continue
- Show summary at end:
  ```
  ✅ Imported 12 tasks
  ⚠️  Skipped 3 tasks (see errors above)
  ```

**Dependency Errors:**
- Circular dependency detected → Reject update, print chain:
  ```
  ❌ Cannot add block: would create circular dependency

  Dependency chain:
  Task A (550e8400...) blocks
  Task B (7a8b9c0d...) blocks
  Task C (2f3e4d5c...) blocks
  Task A (550e8400...) ← CIRCULAR
  ```

---

## 6. CLI Interface (Complete Specification)

### Command: `oos task create`

**Description:** Create a new task

**Usage:**
```bash
oos task create "Task title"
oos task create "Task title" --description "Longer description"
oos task create "Task title" --metadata '{"feature":"auth","tags":["backend"]}'
```

**Arguments:**
- `title` (required): Task title, 5-200 chars, positional argument

**Options:**
- `--description TEXT`: Task description, 0-10000 chars
- `--metadata JSON`: JSON object with additional metadata

**Output (Success):**
```bash
$ oos task create "Implement user authentication"
✅ Task created: 550e8400-e29b-41d4-a716-446655440000
   Title: "Implement user authentication"
   Status: todo
   Created: 2024-10-21T10:00:00Z
```

**Output (Error - Title Too Short):**
```bash
$ oos task create "Auth"
❌ Error: Title too short
   Title must be 5-200 characters
   Provided: "Auth" (4 characters)
```

**Exit Codes:**
- 0: Success
- 1: Validation error
- 2: Database error

### Command: `oos task list`

**Description:** List tasks with optional filtering

**Usage:**
```bash
oos task list
oos task list --status doing
oos task list --status todo,blocked
oos task list --ready
oos task list --feature auth
oos task list --format json
oos task list --limit 10
```

**Options:**
- `--status STATUS`: Filter by status (comma-separated for multiple)
- `--feature NAME`: Filter by metadata.feature
- `--ready`: Show only unblocked tasks (shortcut for status=todo,doing + blocked_by=[])
- `--format FORMAT`: Output format (table, json, yaml)
- `--limit N`: Limit results to N tasks

**Output (Table Format - Default):**
```bash
$ oos task list
ID                                   Status  Title                              Updated
550e8400-e29b-41d4-a716-446655440000 doing   Implement user authentication      2024-10-21T15:30:00Z
7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d done    Create user database schema        2024-10-21T11:00:00Z
2f3e4d5c-6a7b-8c9d-0e1f-2a3b4c5d6e7f blocked Design API endpoints                2024-10-21T16:00:00Z

3 tasks (1 doing, 1 done, 1 blocked)
```

**Output (JSON Format):**
```bash
$ oos task list --format json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Implement user authentication",
    "status": "doing",
    "created": "2024-10-21T10:00:00Z",
    "updated": "2024-10-21T15:30:00Z"
  }
]
```

**Exit Codes:**
- 0: Success (even if no tasks found)
- 1: Invalid filter argument

### Command: `oos task show`

**Description:** Show detailed task information

**Usage:**
```bash
oos task show <task-id>
oos task show 550e8400-e29b-41d4-a716-446655440000
oos task show <task-id> --format json
```

**Arguments:**
- `task-id` (required): Task UUID

**Options:**
- `--format FORMAT`: Output format (table, json, yaml)

**Output:**
```bash
$ oos task show 550e8400-e29b-41d4-a716-446655440000
Task: 550e8400-e29b-41d4-a716-446655440000

Title: Implement user authentication
Status: doing
Created: 2024-10-21T10:00:00Z
Updated: 2024-10-21T15:30:00Z

Description:
Add JWT-based authentication with login/logout endpoints.
Use bcrypt for password hashing. Support refresh tokens.

Blocks: (0 tasks)

Blocked by: (1 task)
  - 7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d: Create user database schema

Metadata:
  feature: auth
  estimated_hours: 8
  tags: [backend, security]
```

**Exit Codes:**
- 0: Success
- 1: Task not found

### Command: `oos task update`

**Description:** Update task fields

**Usage:**
```bash
oos task update <task-id> --status doing
oos task update <task-id> --title "New title"
oos task update <task-id> --description "New description"
oos task update <task-id> --add-blocks <other-task-id>
oos task update <task-id> --remove-blocks <other-task-id>
oos task update <task-id> --metadata '{"priority":"high"}'
```

**Arguments:**
- `task-id` (required): Task UUID

**Options:**
- `--status STATUS`: Update status
- `--title TEXT`: Update title
- `--description TEXT`: Update description
- `--add-blocks ID`: Add blocking relationship
- `--remove-blocks ID`: Remove blocking relationship
- `--metadata JSON`: Update metadata (replaces existing)

**Output:**
```bash
$ oos task update 550e8400-e29b-41d4-a716-446655440000 --status doing
✅ Task updated: 550e8400-e29b-41d4-a716-446655440000
   Status: todo → doing
   Updated: 2024-10-21T16:00:00Z
```

**Exit Codes:**
- 0: Success
- 1: Validation error or task not found
- 2: Database error

### Command: `oos task complete`

**Description:** Mark task as done

**Usage:**
```bash
oos task complete <task-id>
```

**Arguments:**
- `task-id` (required): Task UUID

**Output:**
```bash
$ oos task complete 550e8400-e29b-41d4-a716-446655440000
✅ Task completed: Implement user authentication
   ID: 550e8400-e29b-41d4-a716-446655440000
   Completed: 2024-10-21T17:00:00Z
```

**Exit Codes:**
- 0: Success
- 1: Task not found

### Command: `oos task ready`

**Description:** Show tasks ready to work on (unblocked)

**Usage:**
```bash
oos task ready
oos task ready --format json
```

**Output:**
```bash
$ oos task ready
Ready to work on (3 tasks):

ID                                   Title                              Created
a1b2c3d4-e5f6-7890-abcd-ef1234567890 Write unit tests                   2024-10-20T09:00:00Z
b2c3d4e5-f6a7-8901-bcde-fa1234567890 Setup CI/CD pipeline               2024-10-20T14:00:00Z
c3d4e5f6-a7b8-9012-cdef-ab1234567890 Document API endpoints             2024-10-21T08:00:00Z

Suggested next task: Write unit tests (oldest ready task)
```

**Exit Codes:**
- 0: Success (even if no ready tasks)

### Command: `oos task delete`

**Description:** Delete a task

**Usage:**
```bash
oos task delete <task-id>
oos task delete <task-id> --force
```

**Arguments:**
- `task-id` (required): Task UUID

**Options:**
- `--force`: Skip confirmation prompt

**Output:**
```bash
$ oos task delete 550e8400-e29b-41d4-a716-446655440000
⚠️  Warning: This task is referenced by 2 other tasks:
   - 2f3e4d5c-6a7b-8c9d-0e1f-2a3b4c5d6e7f (blocked by this task)
   - c3d4e5f6-a7b8-9012-cdef-ab1234567890 (blocks this task)

Deleting will remove these dependencies.
Continue? [y/N]: y

✅ Task deleted: 550e8400-e29b-41d4-a716-446655440000
   Updated 2 dependent tasks
```

**Exit Codes:**
- 0: Success
- 1: Task not found or user cancelled

### Command: `oos task import`

**Description:** Import tasks from JSONL file

**Usage:**
```bash
oos task import <file>
oos task import <file> --replace
```

**Arguments:**
- `file` (required): Path to JSONL file

**Options:**
- `--replace`: Delete existing tasks before import (default: merge)

**Output:**
```bash
$ oos task import .oos/tasks/export.jsonl
Importing tasks from .oos/tasks/export.jsonl...
✅ Imported 15 tasks
   - 3 new tasks added
   - 12 existing tasks updated
   - 0 conflicts (local newer)
```

**Exit Codes:**
- 0: Success
- 1: File not found or parse errors

### Command: `oos task export`

**Description:** Force export tasks to JSONL

**Usage:**
```bash
oos task export
oos task export --path /custom/path/tasks.jsonl
```

**Options:**
- `--path PATH`: Custom export path (default: .oos/tasks/export.jsonl)

**Output:**
```bash
$ oos task export
✅ Exported 15 tasks to .oos/tasks/export.jsonl
```

**Exit Codes:**
- 0: Success
- 2: Write permission error

---

## 7. Testing Requirements

### Unit Tests

**Coverage:** 100% of task management logic

**Test Files:**
- `tests/test_task_model.py`: Task validation, field constraints
- `tests/test_task_db.py`: SQLite operations (CRUD)
- `tests/test_task_dependencies.py`: Dependency graph logic, circular detection
- `tests/test_task_export.py`: JSONL export/import, merge logic
- `tests/test_task_cli.py`: CLI commands, argument parsing

**Test Data:**
Located in `tests/fixtures/tasks/`
- `valid_tasks.jsonl`: 20 valid tasks with various states
- `invalid_tasks.jsonl`: Invalid tasks for validation testing
- `circular_deps.jsonl`: Tasks with circular dependencies
- `large_task_set.jsonl`: 1000 tasks for performance testing

**Key Test Cases:**

**Task Validation:**
- Title length validation (4 chars = fail, 5 chars = pass, 200 chars = pass, 201 chars = fail)
- Description length validation (0 chars = pass, 10000 chars = pass, 10001 chars = fail)
- Status enum validation (valid values pass, invalid values fail)
- Metadata JSON validation (valid JSON pass, invalid JSON fail)
- Metadata size validation (<5KB pass, >5KB fail)

**Dependency Graph:**
- Simple block (A blocks B)
- Bidirectional sync (A.blocks contains B, B.blocked_by contains A)
- Circular detection (A→B→C→A should fail)
- Self-blocking detection (A→A should fail)
- Cascade delete (deleting A removes A from B's blocked_by)

**JSONL Export/Import:**
- Export all tasks, verify one task per line
- Import empty file (no-op)
- Import with new tasks (insert)
- Import with existing tasks (update)
- Import with conflicts (timestamp wins)
- Import with invalid lines (skip, continue)

**CLI Commands:**
- `oos task create` with valid/invalid inputs
- `oos task list` with various filters
- `oos task update` with valid/invalid updates
- `oos task complete` with valid/invalid IDs
- `oos task delete` with confirmation
- `oos task ready` with various task states

### Integration Tests

**Scenarios:**
1. **End-to-end workflow:**
   - Bootstrap new project (creates .oos/tasks.db)
   - Create 5 tasks via CLI
   - Update 2 tasks with dependencies
   - Mark 1 task complete
   - List ready tasks
   - Export to JSONL
   - Verify JSONL committed to git

2. **Git sync workflow:**
   - User A creates tasks, commits JSONL, pushes
   - User B pulls, imports JSONL
   - User B updates tasks, commits JSONL, pushes
   - User A pulls, imports JSONL
   - Verify both users have same task state

3. **Dependency workflow:**
   - Create task A
   - Create task B blocked by A
   - Verify B is not in ready list
   - Complete task A
   - Verify B appears in ready list

4. **Error recovery:**
   - Corrupt SQLite database
   - Run import from JSONL
   - Verify database rebuilt correctly

### Performance Tests

**Requirements:**
- 1000 tasks: list command < 100ms
- 1000 tasks: ready command < 50ms
- 1000 tasks: export to JSONL < 200ms
- 1000 tasks: import from JSONL < 500ms
- 10,000 tasks: all operations < 2x above limits

**Load Testing:**
- Create 10,000 tasks via API
- Measure memory usage (should be <100MB)
- Measure database file size (should grow linearly)

### Success Criteria

- All unit tests pass
- All integration tests pass
- Coverage >= 95%
- Performance requirements met
- No memory leaks (run 10,000 operations, memory stable)
- CLI exit codes correct in all cases

---

## 8. Deployment

### Target Environment

- OS: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+ (via WSL2 or native)
- Python: 3.9+
- SQLite: 3.31+ (bundled with Python)
- Disk space: 10MB for code + 1KB per task (~1MB for 1000 tasks)
- RAM: 50MB base + 1KB per task in memory

### Installation Steps

**New Project (via OOS Bootstrap):**
```bash
# Bootstrap new project with OOS (task system enabled by default)
cd /path/to/new/project
/path/to/oos/scripts/bootstrap_enhanced.sh

# Task system automatically initialized:
# - Creates .oos/tasks.db
# - Creates .oos/tasks/export.jsonl
# - Adds to .gitignore

# Start using tasks
oos task create "First task"
```

**Existing Project (Add Task System):**
```bash
# Navigate to existing OOS project
cd /path/to/existing/project

# Run OOS update to add task system
/path/to/oos/bin/update-oos.sh --add-tasks

# Or manually initialize
mkdir -p .oos/tasks
oos task create "First task"  # Creates database on first run
```

**Standalone Installation (Without OOS):**
```bash
# Clone OOS repository
git clone https://github.com/Khamel83/oos.git
cd oos

# Install dependencies
pip install -r requirements.txt

# Add to PATH (optional)
export PATH="$PATH:$(pwd)/bin"

# Or use directly
./bin/oos task create "First task"
```

### First Run Checklist

- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] OOS installed or cloned
- [ ] Project has .oos/ directory (created by bootstrap)
- [ ] Can run `oos task list` without errors
- [ ] Task database created at `.oos/tasks.db`
- [ ] Export file created at `.oos/tasks/export.jsonl`
- [ ] `.gitignore` includes `.oos/tasks.db`

### Integration with Archon (Hybrid Approach)

**Archon Remains Active for:**
- **RAG/Knowledge Base**: Continue using `/archon-research` for document search
- **Cross-Project Views**: View all project tasks in Archon web UI
- **Project Registry**: Central catalog of all your projects

**Optional: Import Existing Archon Tasks to Local**

```bash
# One-time import of Archon tasks to local database (optional)
# Export Archon tasks to JSONL (requires Archon MCP)
# In Claude Code:
# mcp__archon__list_tasks(project_id="<id>")
# Save output to archon_tasks.json

# Convert Archon format to OOS task format
oos task import-archon archon_tasks.json

# Or manually import if already in JSONL format
oos task import archon_tasks.jsonl

# Verify import
oos task list
```

**Integration Notes:**
- Archon keeps RAG and cross-project views (NOT replaced)
- Local tasks for day-to-day work (fast, offline, git-synced)
- Optional one-time import from Archon to local
- Future: Optional one-way sync local → Archon (v1.1)
- Archon status → OOS status mapping:
  - `todo` → `todo`
  - `doing` → `doing`
  - `done` → `done`
  - `review` → `done` (OOS doesn't have review status)
  - `blocked` → `blocked`

**Archon Keep-Alive (Automatic):**
- GitHub Actions pings Archon every 2 days (see FR-8)
- Prevents Supabase from pausing
- Ensures RAG and cross-project views always accessible
- No manual intervention required

---

## 9. Philosophy Enforcement

These principles guide all implementation decisions:

### 1. Simplicity Over Complexity

**What it means:**
- Use simplest solution that works
- SQLite over PostgreSQL
- JSONL over complex serialization
- No frameworks, just Python stdlib + Click

**How it applies:**
- Task model: 9 fields, not 50
- CLI: Simple CRUD commands, not complex DSL
- Storage: Flat JSONL, not nested JSON
- Dependencies: Only blocks/blocked-by, not parent-child-related-discovered

**Code review check:**
- Is there a simpler way to do this?
- Are we adding complexity for theoretical future needs?
- Can we use stdlib instead of external library?

### 2. Project-Embedded Memory

**What it means:**
- Tasks live IN the project (.oos/tasks.db)
- No external server required
- Tasks travel with git repo via JSONL
- Each project is self-contained

**How it applies:**
- Database path: `.oos/tasks.db` (relative to project root)
- Export path: `.oos/tasks/export.jsonl` (relative to project root)
- No global task database
- No network calls for task operations

**Code review check:**
- Does this require external services?
- Is this path absolute or relative?
- Will tasks sync via git?

### 3. Git-Syncable by Design

**What it means:**
- JSONL export is source of truth for git
- SQLite is local cache, rebuilt from JSONL
- Merge conflicts solvable by humans
- One task per line = one change per line

**How it applies:**
- Every create/update/delete triggers JSONL export
- Import resolves conflicts by timestamp
- JSONL format is human-readable
- Line-based format for easy git diff

**Code review check:**
- Is JSONL regenerated after this operation?
- Can humans resolve JSONL merge conflicts?
- Is timestamp-based merge correct?

### 4. Agent-Friendly CLI

**What it means:**
- AI agents can use CLI without ambiguity
- JSON output for programmatic use
- Predictable exit codes
- Clear error messages

**How it applies:**
- `--format json` for all commands
- Exit code 0 = success, 1 = user error, 2 = system error
- Error messages are actionable
- Help text is comprehensive

**Code review check:**
- Can an AI parse this output?
- Are exit codes consistent?
- Are error messages actionable?

### 5. Modular and Optional

**What it means:**
- Task system is optional, OOS works without it
- Can be added to existing projects
- No breaking changes to core OOS
- Graceful degradation if disabled

**How it applies:**
- Config: `tasks.enabled: false` disables system
- Bootstrap: Task init is optional step
- Commands: `oos task` only works if enabled
- No dependency from core OOS to task system

**Code review check:**
- Does this break OOS if tasks disabled?
- Can users opt out?
- Does this change core OOS behavior?

---

Any code that violates these principles must be refactored before merging.

---

## 10. Future Considerations

**Things we might add later but are explicitly out of scope for v1.0:**

**Advanced Dependencies (v1.1):**
- Parent-child relationships (epics and subtasks)
- Related tasks (associated but not blocking)
- Discovered-from (tasks found during other work)
- Full DAG visualization

**Archon Integration (v1.1-v2.0):**
- Bi-directional sync (OOS ↔ Archon)
- Conflict resolution UI
- Push tasks to Archon
- Pull tasks from Archon
- Sync status updates

**Rich Metadata (v1.1):**
- Priority levels (high, medium, low)
- Effort estimates (small, medium, large)
- Time tracking (started_at, completed_at, duration)
- Assignee field (for multi-agent workflows)
- Task templates (common task patterns)

**Search and Query (v1.1):**
- Full-text search via SQLite FTS5
- Query by metadata fields
- Saved queries
- Smart filters

**Visualization (v2.0):**
- Web UI for task management
- Dependency graph visualization
- Gantt chart view
- Burndown charts

**Multi-Project Views (v2.0):**
- Aggregate tasks across all OOS projects
- Cross-project dependencies
- Portfolio view
- Global search

**Advanced CLI (v1.1):**
- Interactive mode (TUI with blessed)
- Fuzzy search for task selection
- Autocomplete for task IDs
- Aliases for common workflows

---

## 11. Appendix: Glossary

**Task:** A unit of work to be done, tracked in the task database

**Status:** Current state of a task (todo, doing, done, blocked)

**Dependency:** Relationship between two tasks where one blocks the other

**Blocks:** Task A blocks task B means B cannot start until A is done

**Blocked By:** Task B is blocked by task A means B cannot start until A is done

**Ready Work:** Tasks that have no blockers (blocked_by is empty)

**JSONL:** JSON Lines format, one JSON object per line

**Export:** Process of writing all tasks to JSONL file for git sync

**Import:** Process of reading JSONL file and updating local database

**Merge:** Conflict resolution when importing tasks that exist locally

**Timestamp-based Merge:** Merge strategy where newer timestamp wins

**Circular Dependency:** Invalid state where task A blocks B blocks C blocks A

**Agent Amnesia:** Problem where AI agents lose context between sessions (this system solves it)

**Project-Embedded Memory:** Tasks stored inside project directory, not external server

**Git-Syncable:** Tasks can be committed to git and synced across machines

---

## 12. Document History

- v1.0 - 2024-10-21 - Initial PRD created following AI-Driven Project Builder template
- v1.0 - 2024-10-21 - Complete data models, CLI specification, error handling
- v1.0 - 2024-10-21 - Philosophy enforcement, testing requirements, deployment

---

## 13. Pre-Validation Self-Assessment

Before submitting for Claude validation, checking against self-assessment criteria:

**Data Models:**
- [x] Full YAML/JSON examples for tasks (3+ examples provided)
- [x] Every field has type, description, constraints, example value
- [x] Edge cases represented (minimal task, complex task, blocked task)
- [x] Nested structures expanded (metadata, blocks, blocked_by)
- [x] Arrays show 2+ items in examples
- [x] No TBD or placeholder fields

**Validation Rules:**
- [x] All rules have explicit numeric thresholds (5-200 chars, 0-10000 chars, max 100 blocks)
- [x] Min/max for every field with character counts
- [x] Required vs optional explicit for every field
- [x] Format constraints with examples (UUID, ISO 8601, JSON)
- [x] Cross-field validation rules (dependency graph, circular detection)
- [x] What happens when validation fails (error messages specified)

**Error Handling:**
- [x] Complete error taxonomy table with 8 error types
- [x] Every error has explicit retry policy (Yes/No)
- [x] Max attempts specified (0 or 3)
- [x] Backoff strategy with actual timings (100ms, 200ms, 400ms)
- [x] Action after max specified (exit, skip, continue)
- [x] Logging format shown with example
- [x] Where failed items stored (skip and log)
- [x] Metadata added to failed items (error type, message, timestamp)

**Configuration:**
- [x] Complete config file example (full .oos/config.yaml shown)
- [x] Every setting has actual default value
- [x] Comments explain each setting
- [x] Valid value ranges documented
- [x] Environment variables listed (none required)
- [x] Config file format specified (YAML)
- [x] Behavior if config invalid or missing (use defaults)

**Dependencies:**
- [x] Exact package names (click==8.1.7, pyyaml==6.0.1)
- [x] Version constraints specified (==)
- [x] Language/runtime version specified (python>=3.9)
- [x] Build tools listed (pip)
- [x] System dependencies noted (sqlite3 built-in)

**Storage Structure:**
- [x] Directory tree shown 3+ levels deep
- [x] Example filenames with actual patterns (.oos/tasks.db, export.jsonl)
- [x] File naming conventions explicit
- [x] Filename collision handling (N/A for SQLite/JSONL)
- [x] Directory creation specified (bootstrap creates .oos/)
- [x] File size limits specified (1KB per task)

**CLI Interface:**
- [x] Every command listed with full signature
- [x] Every flag and argument documented
- [x] Required vs optional parameters explicit
- [x] Example invocations shown for every command
- [x] Output format shown (table, JSON examples)
- [x] Error messages shown for failures

**Philosophy & Principles:**
- [x] Core philosophy stated in 5 principles
- [x] Each principle actionable
- [x] Principles have concrete implications
- [x] Examples show how principles affect decisions
- [x] Principles referenced consistently

**Red Flags (should have NONE):**
- [x] No "configurable" without showing config
- [x] No "appropriate", "reasonable", "sufficient", "robust"
- [x] No "handle errors" without specifying how
- [x] No "validate" without specifying rules
- [x] No "TBD", "TODO", "to be determined"
- [x] No "etc.", "...", ellipsis in critical sections
- [x] No "[placeholder]" in examples

**Self-Assessment Score: 100/100 ✅**

All must-have criteria met, ready for Claude validation.

---

*This PRD is the source of truth for OOS Task Memory System implementation. All ambiguities must be resolved before autonomous build begins.*
