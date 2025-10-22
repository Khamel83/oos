# OOS Task System - Complete Guide

## Overview

The OOS Task Memory System is a comprehensive, project-embedded task management solution designed specifically for the OOS ecosystem. It provides persistent task memory with git synchronization, dependency tracking, and agent-friendly interfaces.

## Philosophy

### 1. Project-Embedded Memory
- Tasks live within your project directory (`.oos/tasks/`)
- No external databases or cloud services required
- Full ownership and control of your data

### 2. Git-Syncable by Design
- JSONL export format optimized for git diffing
- Line-based JSON prevents merge conflicts
- Automatic backup and version control integration

### 3. Dependency-Aware Planning
- Track task dependencies and blockers
- Automatic ready/blocked task identification
- Critical path analysis for project planning

### 4. Agent-Friendly Interface
- JSON output for easy parsing by AI agents
- Comprehensive CLI commands
- Programmatic API for automation

### 5. Modular and Optional
- All functionality is optional and can be disabled
- Zero external dependencies beyond SQLite
- Integrates seamlessly with existing OOS workflows

## Quick Start

### Installation

The task system is included with OOS. Enable it by creating a new project or adding to existing one:

```bash
# Create new project with task system enabled
oos bootstrap my-project --enable-tasks

# Add task system to existing project
mkdir -p .oos/tasks
oos task init
```

### Basic Usage

```python
from src.oos_task_system import Task, TaskDatabase

# Initialize database
db = TaskDatabase(".oos/tasks/tasks.db")

# Create tasks
task1 = Task(
    title="Implement user authentication",
    description="Add login and registration functionality",
    priority="high",
    tags=["security", "backend"]
)
db.create_task(task1)

task2 = Task(
    title="Write authentication tests",
    depends_on=[task1.id],  # Depends on task1
    priority="medium"
)
db.create_task(task2)

# Find ready tasks (no pending dependencies)
ready_tasks = db.get_ready_tasks()
print(f"Ready to work on: {[t.title for t in ready_tasks]}")

# Export to git
db.export_tasks("tasks.jsonl")
```

### CLI Usage

```bash
# Create new task
oos task create "Implement feature" --description "Add new functionality" --priority high

# List tasks
oos task list --status todo --assignee alice

# Show task details
oos task show abc123

# Update task
oos task update abc123 --status doing

# Complete task
oos task complete abc123

# Export tasks
oos task export all --output tasks.jsonl

# Import tasks
oos task import tasks.jsonl --resolution merge

# Show ready tasks
oos task ready
```

## Core Concepts

### Task Lifecycle

Tasks follow the RUAT-compliant status flow:

```
todo → doing → technical-complete → ruat-validation → review → done
```

Additional statuses:
- **blocked**: Task cannot proceed due to dependencies
- **cancelled**: Task cancelled and will not be completed

### Dependencies

Tasks can depend on other tasks:

```python
# Create dependency
feature_task = Task(title="Add user profile", depends_on=["auth_task"])
db.create_task(feature_task)

# Check if task is ready to work on
if feature_task.is_ready():
    print("Ready to start")
else:
    print(f"Blocked by: {feature_task.depends_on}")
```

### Priority Levels

- **urgent**: Critical for current release
- **high**: Important for current sprint
- **medium**: Normal priority
- **low**: Nice to have, lower priority

### Tags and Context

```python
task = Task(
    title="Fix database connection",
    tags=["bug", "database", "urgent"],
    context={
        "project": "web-app",
        "sprint": 3,
        "issue_id": "PROJ-123",
        "reported_by": "alice"
    }
)
```

## Advanced Features

### Dependency Analysis

```python
from src.oos_task_system import DependencyGraph

# Analyze dependency relationships
tasks = db.list_tasks()
graph = DependencyGraph(tasks)

# Find critical path
critical_path = graph.get_critical_path()
print(f"Critical path: {' → '.join(critical_path)}")

# Check for circular dependencies
cycles = graph.detect_cycles()
if cycles:
    print(f"Warning: Circular dependencies found: {cycles}")

# Get impact analysis
impact = graph.get_impact_analysis("task123")
print(f"Task {task123} affects: {impact['directly_affected']}")
```

### Validation

```python
from src.oos_task_system import TaskValidator

validator = TaskValidator()

# Validate task
result = validator.validate_task(task, strict=True)
if not result.is_valid:
    print(f"Validation errors: {result.errors}")
    print(f"Warnings: {result.warnings}")

# Validate individual field
field_result = validator.validate_field("title", "Valid Title")
if not field_result.is_valid:
    print(f"Title invalid: {field_result.errors}")
```

### Export/Import

```python
# Export with filters
result = db.export_tasks(
    "urgent_tasks.jsonl",
    status_filter=[TaskStatus.TODO],
    tag_filter=["urgent"],
    compress=True
)

# Import with conflict resolution
result = db.import_tasks(
    "imported_tasks.jsonl",
    conflict_resolution="merge",
    validate=True,
    dry_run=False
)

# Sync with remote file
result = db.sync_tasks(
    "remote_tasks.jsonl",
    conflict_resolution="merge"
)
```

## Integration with OOS

### Bootstrap Integration

When creating a new project with `oos bootstrap`, the task system is automatically initialized:

```bash
my-project/
├── .oos/
│   ├── tasks/
│   │   ├── tasks.db          # SQLite database (gitignored)
│   │   └── export.jsonl      # JSONL export (committed)
│   └── config.yaml           # Project configuration
├── src/
└── README.md
```

### CLI Commands

The task system provides 10 consolidated commands:

| Command | Purpose | Example |
|---------|---------|---------|
| `/task create <title>` | Create new task | `/task create "Fix bug"` |
| `/task list [--status]` | List tasks | `/task list --status todo` |
| `/task show <id>` | Show task details | `/task show abc123` |
| `/task update <id>` | Update task | `/task update abc123 --status doing` |
| `/task complete <id>` | Complete task | `/task complete abc123` |
| `/task ready` | Show ready tasks | `/task ready` |
| `/task export <file>` | Export tasks | `/task export backup.jsonl` |
| `/task import <file>` | Import tasks | `/task import backup.jsonl` |
| `/task sync <file>` | Sync with file | `/task sync remote.jsonl` |
| `/task delete <id>` | Delete task | `/task delete abc123` |

### Archon Integration

The task system integrates with Archon for knowledge management:

```python
# Export tasks to Archon
graph = DependencyGraph(db.list_tasks())
critical_tasks = graph.get_critical_path()

for task_id in critical_tasks:
    task = db.get_task(task_id)
    # Add to Archon knowledge base
    archon.add_task_insight(task)
```

## Best Practices

### Task Management

1. **Descriptive Titles**: Use clear, actionable task titles
2. **Granular Tasks**: Break large work into smaller, manageable tasks
3. **Dependency Management**: Keep dependency chains reasonable (max 5-6 levels)
4. **Regular Updates**: Update task status as work progresses
5. **Documentation**: Use descriptions and context for important decisions

### Git Workflow

1. **Commit JSONL**: Export and commit JSONL files regularly
2. **Review Changes**: Review task changes in pull requests
3. **Branch Management**: Use branches for major task reorganization
4. **Conflict Resolution**: Use `merge` strategy for collaborative editing

### Team Collaboration

1. **Assignee Management**: Clearly assign tasks to team members
2. **Priority Alignment**: Align priorities across team
3. **Tag Standards**: Use consistent tagging conventions
4. **Regular Sync**: Sync tasks frequently to avoid conflicts

### Performance

1. **Database Size**: Keep task database under 10,000 tasks for optimal performance
2. **Export Filtering**: Use filters for large exports
3. **Compression**: Use compressed exports for backups
4. **Regular Cleanup**: Archive completed tasks periodically

## Troubleshooting

### Common Issues

1. **Database Locks**: Ensure only one process accesses the database at a time
2. **Git Conflicts**: Use JSONL format and line-based merging to minimize conflicts
3. **Dependency Cycles**: Use `DependencyGraph.detect_cycles()` to find and resolve cycles
4. **Import Failures**: Validate JSONL files before importing

### Performance Issues

1. **Slow Queries**: Use proper indexes and filtering
2. **Large Exports**: Use compression and incremental exports
3. **Memory Usage**: Process large datasets in batches

### Data Recovery

1. **Lost Tasks**: Use git history to restore previous JSONL exports
2. **Database Corruption**: Restore from most recent JSONL export
3. **Accidental Deletion**: Check git history for deleted tasks

## API Reference

### Core Classes

- **Task**: Task data model with validation and serialization
- **TaskDatabase**: SQLite database interface with CRUD operations
- **DependencyGraph**: Dependency analysis and graph operations
- **TaskValidator**: Field validation and business rule enforcement
- **TaskExporter**: JSONL export with filtering and formatting
- **TaskImporter**: JSONL import with conflict resolution

### Database Operations

```python
# CRUD operations
task = db.create_task(task)
task = db.get_task(task_id)
task = db.update_task(task)
success = db.delete_task(task_id)

# Query operations
tasks = db.list_tasks(status=TaskStatus.TODO, assignee="alice")
ready_tasks = db.get_ready_tasks()
blocked_tasks = db.get_blocked_tasks()

# Export/Import
result = db.export_tasks("output.jsonl")
result = db.import_tasks("input.jsonl")
result = db.sync_tasks("sync.jsonl")
```

### Dependency Analysis

```python
# Graph operations
graph = DependencyGraph(tasks)
cycles = graph.detect_cycles()
sorted_tasks = graph.topological_sort()
critical_path = graph.get_critical_path()

# Task relationships
blocking_tasks = graph.get_blocking_tasks(task_id)
impact = graph.get_impact_analysis(task_id)
ready_tasks = graph.get_ready_tasks()
```

### Validation

```python
# Task validation
validator = TaskValidator()
result = validator.validate_task(task, strict=True)

# Field validation
result = validator.validate_field("title", "Valid Title")

# Constraints
constraints = validator.get_field_constraints()
```

## Configuration

### Environment Variables

```bash
# Enable/disable task system
OOS_TASKS_ENABLED=true

# Database location
OOS_TASKS_DB_PATH=".oos/tasks/tasks.db"

# Default conflict resolution
OOS_TASKS_DEFAULT_RESOLUTION="merge"

# Validation strictness
OOS_TASKS_STRICT_VALIDATION=false
```

### Project Configuration

```yaml
# .oos/config.yaml
tasks:
  enabled: true
  auto_export: true
  export_format: "jsonl"
  default_priority: "medium"
  validation:
    strict: false
    required_fields: ["title"]
    max_dependencies: 10
```

## Migration Guide

### From Existing Task Systems

1. **Export Current Tasks**: Export from existing system to JSON/CSV
2. **Transform Data**: Convert to OOS task format
3. **Import**: Use `TaskImporter` with appropriate conflict resolution
4. **Validate**: Run validation to ensure data integrity

### Legacy OOS Tasks

If you have existing tasks in `.oos/tasks.json`:

```python
# Migration script
import json
from src.oos_task_system import TaskDatabase

# Load legacy tasks
with open('.oos/tasks.json') as f:
    legacy_tasks = json.load(f)

# Initialize new database
db = TaskDatabase('.oos/tasks/tasks.db')

# Migrate tasks
for legacy_task in legacy_tasks:
    task = Task.from_dict(legacy_task)
    db.create_task(task)

# Export to new format
db.export_tasks('.oos/tasks/export.jsonl')
```

## Contributing

### Development Setup

```bash
# Clone repository
git clone <oos-repo>
cd oos

# Install dependencies
uv sync

# Run tests
pytest tests/test_task_*.py

# Run specific test file
pytest tests/test_task_models.py -v
```

### Code Style

- Follow PEP 8 for Python code
- Use type hints for all public methods
- Write comprehensive tests for new features
- Document public APIs with docstrings

### Testing

- Unit tests for all core functionality
- Integration tests for export/import workflows
- Performance tests for large datasets
- Error handling tests for edge cases

## Support

### Documentation

- **API Reference**: Detailed method documentation
- **JSONL Guide**: Export/import best practices
- **CLI Reference**: Command-line usage examples
- **Architecture Guide**: System design and internals

### Community

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share experiences
- **Contributing**: Guidelines for contributing code

### Troubleshooting

- **FAQ**: Common questions and solutions
- **Known Issues**: Current limitations and workarounds
- **Migration Guides**: Help with upgrading from older versions