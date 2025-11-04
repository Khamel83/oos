# OOS Task System CLI Reference

## Overview

The OOS Task System provides a comprehensive command-line interface for task management, dependency tracking, and data synchronization. Built with Click, it offers intuitive commands for all task operations.

## Installation

The CLI is included with the OOS Task System. No additional installation required.

## Quick Start

```bash
# Initialize task system (if not already done)
mkdir -p .oos/tasks
python -m src.oos_task_system.cli --help

# Create your first task
python -m src.oos_task_system.cli create "Implement user authentication"

# List all tasks
python -m src.oos_task_system.cli list

# Show ready tasks
python -m src.oos_task_system.cli ready
```

## Global Options

### `--db-path`
Specify the database file path.

```bash
python -m src.oos_task_system.cli --db-path /custom/path/tasks.db <command>
```

**Default**: `.oos/tasks/tasks.db`

## Commands

### Task Management

#### `create` - Create a new task

Creates a new task with specified properties.

```bash
python -m src.oos_task_system.cli create <title> [options]
```

**Arguments:**
- `title`: Task title (required)

**Options:**
- `--description, -d`: Task description
- `--status, -s`: Initial status (todo, doing, technical-complete, ruat-validation, review, done, blocked, cancelled) [default: todo]
- `--priority, -p`: Priority level (low, medium, high, urgent) [default: medium]
- `--assignee, -a`: Task assignee
- `--tags, -t`: Comma-separated tags
- `--depends-on`: Comma-separated task IDs this task depends on
- `--context`: Context as key=value pairs (comma-separated)
- `--estimated-hours`: Estimated hours for completion
- `--due-date`: Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM)
- `--json`: Output as JSON

**Examples:**
```bash
# Basic task
python -m src.oos_task_system.cli create "Fix login bug"

# Full-featured task
python -m src.oos_task_system.cli create "Implement OAuth2" \
  --description "Add OAuth2 authentication with Google and GitHub" \
  --status todo \
  --priority high \
  --assignee alice \
  --tags "auth,security,frontend" \
  --depends-on "task123,task124" \
  --context "project=web-app,sprint=3,story_id=PROJ-456" \
  --estimated-hours 8 \
  --due-date "2024-01-15"

# JSON output
python -m src.oos_task_system.cli create "API endpoint" --json
```

#### `list` - List tasks

Lists tasks with optional filtering and sorting.

```bash
python -m src.oos_task_system.cli list [options]
```

**Options:**
- `--status, -s`: Filter by status
- `--assignee, -a`: Filter by assignee
- `--tags, -t`: Filter by tags (comma-separated, OR logic)
- `--priority, -p`: Filter by priority
- `--ready`: Show only ready tasks (no pending dependencies)
- `--blocked`: Show only blocked tasks
- `--limit, -n`: Limit number of results
- `--sort`: Sort field (created, updated, title, priority, status) [default: created]
- `--reverse`: Reverse sort order
- `--json`: Output as JSON
- `--count`: Show only count

**Examples:**
```bash
# List all tasks
python -m src.oos_task_system.cli list

# Filter by status and assignee
python -m src.oos_task_system.cli list --status todo --assignee alice

# Filter by tags
python -m src.oos_task_system.cli list --tags "urgent,backend"

# Show ready tasks only
python -m src.oos_task_system.cli list --ready

# Sort by priority (highest first)
python -m src.oos_task_system.cli list --sort priority --reverse

# Limit results
python -m src.oos_task_system.cli list --limit 10

# JSON output
python -m src.oos_task_system.cli list --status doing --json

# Count only
python -m src.oos_task_system.cli list --status done --count
```

#### `show` - Show task details

Displays detailed information about a specific task.

```bash
python -m src.oos_task_system.cli show <task_id> [options]
```

**Arguments:**
- `task_id`: Task identifier (partial or full ID)

**Options:**
- `--json`: Output as JSON

**Examples:**
```bash
# Show task details
python -m src.oos_task_system.cli show abc12345

# JSON output
python -m src.oos_task_system.cli show abc12345 --json
```

#### `update` - Update existing task

Modifies properties of an existing task.

```bash
python -m src.oos_task_system.cli update <task_id> [options]
```

**Arguments:**
- `task_id`: Task identifier

**Options:**
- `--title`: New task title
- `--description, -d`: New task description
- `--status, -s`: New task status
- `--priority, -p`: New task priority
- `--assignee, -a`: New task assignee
- `--add-tags`: Tags to add (comma-separated)
- `--remove-tags`: Tags to remove (comma-separated)
- `--add-dependencies`: Dependencies to add (comma-separated)
- `--remove-dependencies`: Dependencies to remove (comma-separated)
- `--estimated-hours`: New estimated hours
- `--actual-hours`: Add actual hours
- `--json`: Output as JSON

**Examples:**
```bash
# Update title and status
python -m src.oos_task_system.cli update abc12345 --title "New title" --status doing

# Add tags and dependencies
python -m src.oos_task_system.cli update abc12345 --add-tags "urgent,bug" --add-dependencies "def67890"

# Add actual hours worked
python -m src.oos_task_system.cli update abc12345 --actual-hours 2.5

# Remove completed dependency
python -m src.oos_task_system.cli update abc12345 --remove-dependencies "oldtask123"
```

#### `complete` - Mark task as complete

Quickly marks a task as done with current timestamp.

```bash
python -m src.oos_task_system.cli complete <task_id>
```

**Arguments:**
- `task_id`: Task identifier

**Examples:**
```bash
python -m src.oos_task_system.cli complete abc12345
```

#### `delete` - Delete a task

Removes a task from the database.

```bash
python -m src.oos_task_system.cli delete <task_id> [options]
```

**Arguments:**
- `task_id`: Task identifier

**Options:**
- `--confirm`: Skip confirmation prompt

**Examples:**
```bash
# Delete with confirmation
python -m src.oos_task_system.cli delete abc12345

# Delete without confirmation
python -m src.oos_task_system.cli delete abc12345 --confirm
```

### Dependency Management

#### `ready` - Show ready tasks

Lists tasks that are ready to work on (no pending dependencies).

```bash
python -m src.oos_task_system.cli ready [options]
```

**Options:**
- `--json`: Output as JSON
- `--limit, -n`: Limit number of results

**Examples:**
```bash
# Show all ready tasks
python -m src.oos_task_system.cli ready

# Limit to top 5 ready tasks
python -m src.oos_task_system.cli ready --limit 5

# JSON output
python -m src.oos_task_system.cli ready --json
```

#### `blocked` - Show blocked tasks

Displays tasks that are blocked by dependencies.

```bash
python -m src.oos_task_system.cli blocked [options]
```

**Options:**
- `--json`: Output as JSON

**Examples:**
```bash
# Show blocked tasks
python -m src.oos_task_system.cli blocked

# JSON output
python -m src.oos_task_system.cli blocked --json
```

### Data Management

#### `export` - Export tasks to JSONL

Exports tasks to JSONL file for backup or sharing.

```bash
python -m src.oos_task_system.cli export [options]
```

**Options:**
- `--output, -o`: Output file path [default: tasks.jsonl]
- `--compress`: Compress output with gzip
- `--status`: Filter by status (can be used multiple times)
- `--assignee, -a`: Filter by assignee
- `--tags, -t`: Filter by tags (comma-separated)
- `--sort`: Sort field (created, updated, title, priority, status) [default: created]
- `--reverse`: Reverse sort order
- `--exclude-fields`: Fields to exclude (comma-separated)

**Examples:**
```bash
# Export all tasks
python -m src.oos_task_system.cli export --output backup.jsonl

# Export only TODO tasks
python -m src.oos_task_system.cli export --status todo --output todo-tasks.jsonl

# Export with compression
python -m src.oos_task_system.cli export --compress --output backup.jsonl.gz

# Export filtered by assignee and priority
python -m src.oos_task_system.cli export --assignee alice --priority high --output alice-high.jsonl

# Export excluding sensitive fields
python -m src.oos_task_system.cli export --exclude-fields "context,actual_hours" --output public-tasks.jsonl
```

#### `import-tasks` - Import tasks from JSONL

Imports tasks from JSONL file with conflict resolution.

```bash
python -m src.oos_task_system.cli import-tasks <input_file> [options]
```

**Arguments:**
- `input_file`: Path to JSONL file to import

**Options:**
- `--resolution`: Conflict resolution strategy (skip, overwrite, merge, create-new) [default: skip]
- `--dry-run`: Preview import without making changes
- `--validate`: Validate tasks before importing [default: true]
- `--strict`: Use strict validation

**Examples:**
```bash
# Import with validation
python -m src.oos_task_system.cli import-tasks backup.jsonl

# Preview import
python -m src.oos_task_system.cli import-tasks backup.jsonl --dry-run

# Import with merge conflict resolution
python -m src.oos_task_system.cli import-tasks backup.jsonl --resolution merge

# Import without validation
python -m src.oos_task_system.cli import-tasks backup.jsonl --no-validate
```

#### `sync` - Synchronize with JSONL file

Performs two-way sync with JSONL file (export current state, then import).

```bash
python -m src.oos_task_system.cli sync <jsonl_file> [options]
```

**Arguments:**
- `jsonl_file`: Path to JSONL file to sync with

**Options:**
- `--resolution`: Conflict resolution strategy (skip, overwrite, merge, create-new) [default: merge]

**Examples:**
```bash
# Sync with remote file
python -m src.oos_task_system.cli sync remote-tasks.jsonl

# Sync with overwrite strategy
python -m src.oos_task_system.cli sync remote-tasks.jsonl --resolution overwrite
```

### Utilities

#### `stats` - Show database statistics

Displays statistics about the task database.

```bash
python -m src.oos_task_system.cli stats
```

**Examples:**
```bash
python -m src.oos_task_system.cli stats
```

**Sample Output:**
```
📊 Task Database Statistics
  Database: .oos/tasks/tasks.db
  Total tasks: 15
  File size: 24576 bytes

  Status breakdown:
    ⏳ todo: 8
    🚀 doing: 3
    ✨ done: 4
```

#### `validate` - Validate task(s)

Validates task data against schema and business rules.

```bash
python -m src.oos_task_system.cli validate [task_id] [options]
```

**Arguments:**
- `task_id`: Specific task ID to validate (optional)

**Options:**
- `--all-tasks`: Validate all tasks in database

**Examples:**
```bash
# Validate specific task
python -m src.oos_task_system.cli validate abc12345

# Validate all tasks
python -m src.oos_task_system.cli validate --all-tasks
```

## Output Formats

### Standard Output

Most commands use emoji icons and formatted text:

```
⏳ 🟡 abc12345: Implement user authentication (@alice)
✨ 🔴 def67890: Fix critical security issue
🚀 🟠 ghi90123: Write API documentation
```

### JSON Output

All commands support `--json` flag for machine-readable output:

```json
{
  "id": "abc12345",
  "title": "Implement user authentication",
  "description": "Add login and registration functionality",
  "status": "doing",
  "priority": "medium",
  "assignee": "alice",
  "tags": ["auth", "security"],
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-02T15:30:00"
}
```

## Status Icons

| Status | Icon |
|--------|------|
| TODO | ⏳ |
| DOING | 🚀 |
| Technical Complete | ✅ |
| RUAT Validation | 🧪 |
| Review | 👀 |
| Done | ✨ |
| Blocked | 🚫 |
| Cancelled | ❌ |

## Priority Icons

| Priority | Icon |
|----------|------|
| Low | 🔵 |
| Medium | 🟡 |
| High | 🟠 |
| Urgent | 🔴 |

## Advanced Usage

### Scripting Integration

The CLI is designed for easy scripting:

```bash
#!/bin/bash

# Get ready tasks as JSON
READY_TASKS=$(python -m src.oos_task_system.cli ready --json)

# Process each ready task
echo "$READY_TASKS" | jq -r '.[].id' | while read task_id; do
    echo "Processing task: $task_id"
    # Add your task processing logic here
done

# Export daily backup
DATE=$(date +%Y%m%d)
python -m src.oos_task_system.cli export --output "backup/tasks-$DATE.jsonl" --compress
```

### Git Integration

Add to your git workflow:

```bash
#!/bin/bash

# Pre-commit hook: Export tasks
python -m src.oos_task_system.cli export --output .oos/tasks/export.jsonl
git add .oos/tasks/export.jsonl

# Post-merge hook: Sync with remote
if [ -f .oos/tasks/remote.jsonl ]; then
    python -m src.oos_task_system.cli sync .oos/tasks/remote.jsonl
fi
```

### Aliases

Create convenient aliases:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias tasks='python -m src.oos_task_system.cli'
alias todo='tasks list --status todo'
alias doing='tasks list --status doing'
alias ready='tasks ready'
alias tshow='tasks show'
alias tdone='tasks complete'
alias tcreate='tasks create'
```

### Filtering Examples

Complex filtering combinations:

```bash
# High priority TODO tasks assigned to me, sorted by priority
python -m src.oos_task_system.cli list \
  --status todo \
  --priority high \
  --assignee $(whoami) \
  --sort priority \
  --reverse

# Tasks with specific tags, limit 5
python -m src.oos_task_system.cli list \
  --tags "bug,urgent" \
  --limit 5

# Tasks created in last week (requires date filtering in list command)
python -m src.oos_task_system.cli list \
  --sort created \
  --reverse \
  --limit 20
```

## Error Handling

The CLI provides clear error messages:

```bash
$ python -m src.oos_task_system.cli show nonexistent
Error: Task nonexistent not found

$ python -m src.oos_task_system.cli create
Error: Missing argument 'TITLE'

$ python -m src.oos_task_system.cli create "Test" --due-date invalid
Error: Invalid due date format: invalid
```

## Environment Variables

Configure behavior with environment variables:

```bash
# Default database path
export OOS_TASKS_DB_PATH="/custom/path/tasks.db"

# Default conflict resolution
export OOS_TASKS_DEFAULT_RESOLUTION="merge"

# Enable strict validation by default
export OOS_TASKS_STRICT_VALIDATION="true"
```

## Performance Tips

1. **Use filtering**: Reduce output with `--limit` and status filters
2. **JSON for parsing**: Use `--json` for script processing
3. **Compression**: Use `--compress` for large exports
4. **Batch operations**: Use export/import for bulk operations

## Troubleshooting

### Common Issues

1. **Database not found**:
   ```bash
   mkdir -p .oos/tasks
   python -m src.oos_task_system.cli stats
   ```

2. **Permission denied**:
   ```bash
   chmod 755 .oos/tasks
   ```

3. **Import conflicts**:
   ```bash
   python -m src.oos_task_system.cli import-tasks file.jsonl --dry-run
   ```

### Debug Mode

Enable debug output:

```bash
# Set debug environment variable
export OOS_TASKS_DEBUG=1

# Run command with verbose output
python -m src.oos_task_system.cli list --debug
```

## Integration with Other Tools

### VS Code Integration

Add to `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "List ready tasks",
            "type": "shell",
            "command": "python",
            "args": [
                "-m", "src.oos_task_system.cli", "ready"
            ],
            "group": "build"
        }
    ]
}
```

### GitHub Actions

```yaml
name: Task Backup
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Export tasks
        run: |
          python -m src.oos_task_system.cli export --output backup.jsonl --compress
      - name: Commit backup
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add backup.jsonl.gz
          git commit -m "Daily task backup" || true
          git push
```

This reference covers all CLI functionality. For detailed API documentation, see the [Task System Guide](TASK_SYSTEM_GUIDE.md).