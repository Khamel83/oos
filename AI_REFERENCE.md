# AI Claude Reference - OOS Task System

**FOR CLAUDE AI ONLY** - This is detailed technical documentation for AI Claude implementation.

## 🎯 Purpose

This document provides Claude with the technical details needed to:
- Implement task system functionality
- Make informed decisions about task system usage
- Debug and troubleshoot task system issues
- Guide humans to appropriate simple documentation

## 📚 Claude's Documentation Hierarchy

**READ THIS FIRST** (Technical Details):
- `docs/TASK_SYSTEM_GUIDE.md` - Complete system overview
- `docs/JSONL_EXPORT_IMPORT_GUIDE.md` - Export/import reference
- `docs/CLI_REFERENCE.md` - Command reference
- `src/oos_task_system/__init__.py` - API interface

**FOR HUMANS** (Simple Guides):
- `GUIDES/5MinuteQuickStart.md` - Quick setup
- `GUIDES/EmergencyRefresher.md` - When they forget
- `GUIDES/QuickReference.md` - Daily commands

## 🏗️ Task System Architecture

### Core Components

**1. Models (`src/oos_task_system/models.py`)**
```python
# Task data structure
Task(
    id: str,                    # Auto-generated 8-char UUID
    title: str,                 # Required, max 200 chars
    description: str,           # Optional, max 5000 chars
    status: TaskStatus,         # Enum: todo → doing → technical-complete → ruat-validation → review → done
    priority: TaskPriority,     # Enum: low → medium → high → urgent
    tags: List[str],            # List of strings, max 20 items
    depends_on: List[str],      # List of task IDs
    blocks: List[str],          # Auto-populated dependency reverse mapping
    assignee: Optional[str],    # Optional assignee
    created_at: datetime,       # Auto-generated
    updated_at: datetime,       # Auto-updated
    completed_at: Optional[datetime],  # Set when marked complete
    due_date: Optional[datetime],      # Optional due date
    estimated_hours: Optional[float],   # Optional estimate
    actual_hours: Optional[float],      # Optional actual time
    context: Dict[str, Any]     # Flexible metadata
)
```

**2. Database (`src/oos_task_system/database.py`)**
```python
# Database operations
class TaskDatabase:
    def create_task(task: Task) -> Task
    def get_task(task_id: str) -> Optional[Task]
    def update_task(task: Task) -> Task
    def delete_task(task_id: str) -> bool
    def list_tasks(filters) -> List[Task]
    def get_ready_tasks() -> List[Task]      # No pending dependencies
    def get_blocked_tasks() -> List[Task]    # Has pending dependencies
    def export_tasks(path, **options) -> Dict
    def import_tasks(path, **options) -> Dict
    def sync_tasks(path, resolution) -> Dict
```

**3. Dependencies (`src/oos_task_system/dependencies.py`)**
```python
class DependencyGraph:
    def detect_cycles() -> List[List[str]]     # Find circular dependencies
    def topological_sort() -> List[str]         # Dependency order
    def get_ready_tasks() -> List[str]          # Tasks ready to work on
    def get_blocked_tasks() -> List[str]        # Tasks blocked by dependencies
    def get_critical_path() -> List[str]        # Longest dependency chain
    def get_impact_analysis(task_id) -> Dict     # What changes affect
```

**4. Validation (`src/oos_task_system/validation.py`)**
```python
class TaskValidator:
    def validate_task(task: Task, strict: bool) -> ValidationResult
    def validate_field(field: str, value: Any) -> ValidationResult
    def get_field_constraints() -> Dict          # All validation rules
```

**5. Export/Import (`src/oos_task_system/jsonl_export.py`, `jsonl_import.py`)**
```python
class TaskExporter:
    def export_all_tasks(path, **options) -> Dict
    def export_filtered_tasks(path, filters, **options) -> Dict
    def export_incremental(path, since, **options) -> Dict
    def export_by_project(dir, project_field, **options) -> Dict

class TaskImporter:
    def import_tasks(path, resolution, **options) -> ImportResult
    def import_incremental(path, since, **options) -> ImportResult
    def import_from_multiple_files(paths, **options) -> ImportResult
    def validate_import_file(path) -> Tuple[bool, List[str]]
```

**6. CLI (`src/oos_task_system/cli.py`)**
```python
# 16 CLI commands
cli.commands = {
    'create', 'list', 'show', 'update', 'delete', 'complete',
    'ready', 'blocked', 'export', 'import-tasks', 'sync',
    'stats', 'validate'
}
```

## 🔧 Implementation Patterns

### Task Creation Pattern
```python
from src.oos_task_system import Task, TaskDatabase

# Initialize database
db = TaskDatabase(".oos/tasks/tasks.db")

# Create task with validation
task = Task(
    title="Implement feature",
    description="Add new functionality",
    priority=TaskPriority.HIGH,
    tags=["backend", "api"],
    depends_on=["task123"],
    context={"project": "web-app", "story_id": "PROJ-456"}
)

# Validate before creating
validator = TaskValidator()
result = validator.validate_task(task)
if not result.is_valid:
    raise Exception(f"Validation failed: {result.errors}")

db.create_task(task)
```

### Dependency Management Pattern
```python
from src.oos_task_system import DependencyGraph

# Analyze dependencies
tasks = db.list_tasks()
graph = DependencyGraph(tasks)

# Check for cycles
cycles = graph.detect_cycles()
if cycles:
    raise Exception(f"Circular dependency: {cycles}")

# Get work order
sorted_tasks = graph.topological_sort()
ready_tasks = graph.get_ready_tasks()
```

### Export/Import Pattern
```python
# Export with filtering
from src.oos_task_system import TaskExporter

exporter = TaskExporter(db)
result = exporter.export_filtered_tasks(
    "backup.jsonl",
    status_filter=[TaskStatus.TODO, TaskStatus.DOING],
    assignee_filter="alice",
    compress=True
)

# Import with conflict resolution
from src.oos_task_system import TaskImporter, ConflictResolution

importer = TaskImporter(db)
result = importer.import_tasks(
    "import.jsonl",
    conflict_resolution=ConflictResolution.MERGE,
    validate=True,
    dry_run=False
)
```

### CLI Integration Pattern
```python
# In CLI commands, use local imports to avoid circular dependencies
def export_command():
    from .jsonl_export import TaskExporter
    exporter = TaskExporter(db)
    return exporter.export_all_tasks(path)
```

## 🗄️ Database Schema

### Tasks Table
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'todo',
    priority TEXT DEFAULT 'medium',
    tags TEXT DEFAULT '[]',
    assignee TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT,
    due_date TEXT,
    estimated_hours REAL,
    actual_hours REAL,
    context TEXT DEFAULT '{}'
);
```

### Task Dependencies Table
```sql
CREATE TABLE task_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    depends_on_id TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_id) REFERENCES tasks (id) ON DELETE CASCADE,
    UNIQUE (task_id, depends_on_id)
);
```

### Indexes
```sql
CREATE INDEX idx_tasks_status ON tasks (status);
CREATE INDEX idx_tasks_created_at ON tasks (created_at);
CREATE INDEX idx_tasks_assignee ON tasks (assignee);
CREATE INDEX idx_dependencies_task ON task_dependencies (task_id);
CREATE INDEX idx_dependencies_depends ON task_dependencies (depends_on_id);
```

## 📝 JSONL Format

### Export Format
```json
{"__metadata__": {"version": "1.0", "exported_at": "2024-01-01T12:00:00", "total_tasks": 2}}
{"id": "abc123", "title": "Task 1", "status": "todo", "priority": "medium", "created_at": "2024-01-01T10:00:00", "updated_at": "2024-01-01T10:00:00", "__exported_at__": "2024-01-01T12:00:00"}
{"id": "def456", "title": "Task 2", "status": "doing", "priority": "high", "depends_on": ["abc123"], "created_at": "2024-01-01T11:00:00", "updated_at": "2024-01-01T11:30:00", "__exported_at__": "2024-01-01T12:00:00"}
```

### Import Handling
- Skip `__metadata__` lines
- Remove `__exported_at__` from task data
- Validate all fields before import
- Handle missing fields with defaults
- Convert string enums back to enum objects

## 🔍 Debugging Patterns

### Common Issues
1. **Circular Dependencies**: Use `DependencyGraph.detect_cycles()`
2. **Import Failures**: Check JSONL format, validate each line
3. **Database Locks**: Ensure single process access
4. **Priority Ordering**: Use SQL CASE statements for proper sorting

### Debug Commands
```bash
# Check database stats
python -m src.oos_task_system.cli stats

# Validate all tasks
python -m src/oos_task_system.cli validate --all-tasks

# Export/import round-trip test
python -m src.oos_task_system.cli export test.jsonl
python -m src.oos_task_system.cli import-tasks test.jsonl --dry-run

# Check dependencies
python -c "
from src.oos_task_system import TaskDatabase, DependencyGraph
db = TaskDatabase('.oos/tasks/tasks.db')
tasks = db.list_tasks()
graph = DependencyGraph(tasks)
print('Cycles:', graph.detect_cycles())
print('Ready:', len(graph.get_ready_tasks()))
print('Blocked:', len(graph.get_blocked_tasks()))
"
```

## 🚀 Performance Considerations

### Database Optimization
- Use prepared statements for repeated queries
- Batch operations for bulk changes
- Consider connection pooling for high-volume usage
- Vacuum database periodically for SQLite optimization

### Export/Import Performance
- Use compression for large exports (>1000 tasks)
- Filter exports to reduce file size
- Process imports in batches for very large files
- Validate incrementally during import

### CLI Performance
- Use streaming for large result sets
- Implement pagination for list commands
- Cache frequently accessed data
- Optimize JSON serialization

## 🔄 Integration Patterns

### With Bootstrap
```python
# In scripts/bootstrap_enhanced.sh
if [ "${ENABLE_TASKS:-true}" = "true" ]; then
    mkdir -p "${PROJECT_DIR}/.oos/tasks"
    python3 -m src.oos_task_system.database init "${PROJECT_DIR}/.oos/tasks/tasks.db"
    touch "${PROJECT_DIR}/.oos/tasks/export.jsonl"
fi
```

### With Git Workflow
```bash
# Pre-commit hook
python3 -m src.oos_task_system.cli export .oos/tasks/export.jsonl
git add .oos/tasks/export.jsonl

# Post-merge hook
if [ -f .oos/tasks/remote.jsonl ]; then
    python3 -m src.oos_task_system.cli sync .oos/tasks/remote.jsonl
fi
```

### With Archon
```python
# Add task insights to Archon
graph = DependencyGraph(tasks)
critical_tasks = graph.get_critical_path()

for task_id in critical_tasks:
    task = db.get_task(task_id)
    archon.add_task_insight(task)
```

## 📊 Testing Patterns

### Unit Tests
```python
def test_task_creation():
    task = Task(title="Test")
    assert task.title == "Test"
    assert task.status == TaskStatus.TODO

def test_dependency_cycle_detection():
    task1 = Task(id="1", depends_on=["2"])
    task2 = Task(id="2", depends_on=["1"])
    graph = DependencyGraph([task1, task2])
    cycles = graph.detect_cycles()
    assert len(cycles) == 1
```

### Integration Tests
```python
def test_export_import_round_trip():
    # Create tasks
    # Export to JSONL
    # Import from JSONL
    # Verify data integrity
    assert len(original_tasks) == len(imported_tasks)
```

### CLI Tests
```python
def test_cli_task_creation(runner):
    result = runner.invoke(cli, ['create', 'Test Task'])
    assert result.exit_code == 0
    assert 'Created task' in result.output
```

## ⚠️ Edge Cases

### Database Corruption
- Have backup JSONL files
- Implement recovery procedures
- Validate database integrity

### Large Datasets
- Implement pagination
- Use streaming operations
- Consider database sharding

### Concurrency
- Use file locks for database access
- Implement retry logic
- Handle connection timeouts

## 🎯 Claude's Decision Making

When working with task system, Claude should:

1. **Read detailed docs first** - Use technical documentation for implementation
2. **Validate before changes** - Always validate tasks before database operations
3. **Consider dependencies** - Check dependency graph before making changes
4. **Use appropriate conflict resolution** - Choose merge for collaborative work
5. **Guide to simple docs** - When humans ask, point them to GUIDES/ folder
6. **Test thoroughly** - Validate functionality with test scenarios
7. **Maintain data integrity** - Export before major changes, verify imports

## 📚 Quick Reference Commands

```python
# Core operations
from src.oos_task_system import Task, TaskDatabase, DependencyGraph
db = TaskDatabase(path)
task = db.create_task(Task(title="New task"))
ready = db.get_ready_tasks()

# CLI for humans
python -m src.oos_task_system.cli create "Task title"
python -m src.oos_task_system.cli ready
python -m src.oos_task_system.cli export backup.jsonl
```

**Remember**: Use detailed docs for implementation, guide humans to simple guides!