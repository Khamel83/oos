# JSONL Export/Import Guide

## Overview

The OOS Task System provides comprehensive JSONL (JSON Lines) export and import functionality for:

- **Git Synchronization**: Export tasks to line-based JSON files that can be committed to git
- **Cross-Project Sharing**: Export tasks from one project and import into another
- **Backup & Restore**: Export tasks for backup and restoration
- **Data Migration**: Move tasks between different databases or systems

## Features

### Export Features

- **Filtering**: Export by status, assignee, tags, date ranges, or custom filters
- **Compression**: Support for gzip-compressed JSONL files (.jsonl.gz)
- **Sorting**: Sort tasks by creation date, title, status, or priority
- **Field Exclusion**: Exclude sensitive or unnecessary fields
- **Incremental Exports**: Export only tasks modified since a specific date
- **Project Grouping**: Export tasks grouped by project into separate files
- **Size Estimation**: Preview export file size before exporting

### Import Features

- **Conflict Resolution**: Handle conflicts with existing tasks (skip, overwrite, merge, create new)
- **Validation**: Comprehensive field validation with strict/non-strict modes
- **Dry Run**: Preview import changes without making them
- **Incremental Imports**: Import only newer versions of tasks
- **Multiple Files**: Import from multiple JSONL files at once
- **Import Preview**: Analyze import files before importing
- **File Validation**: Validate JSONL files without importing

## Quick Start

### Basic Export

```python
from src.oos_task_system import TaskDatabase

# Initialize database
db = TaskDatabase("project/.oos/tasks/tasks.db")

# Export all tasks
result = db.export_tasks("tasks.jsonl")
print(f"Exported {result['exported_tasks']} tasks")
```

### Basic Import

```python
# Import tasks from JSONL file
result = db.import_tasks("tasks.jsonl")
print(f"Imported {result['tasks_imported']} tasks")
print(f"Updated {result['tasks_updated']} tasks")
print(f"Errors: {len(result['errors'])}")
```

### Synchronization

```python
# Sync with JSONL file (backup + import with merge)
result = db.sync_tasks("tasks.jsonl", conflict_resolution="merge")
print(f"Sync successful: {result['success']}")
```

## Advanced Usage

### Export with Filters

```python
from src.oos_task_system.models import TaskStatus

# Export only TODO tasks assigned to specific person
result = db.export_tasks(
    "todo_tasks.jsonl",
    status_filter=[TaskStatus.TODO],
    assignee_filter="alice",
    sort_by="priority",
    reverse_sort=True
)
```

### Export by Project

```python
# Export tasks grouped by project
exporter = TaskExporter(db)
result = exporter.export_by_project("exports/", project_field="project")

print(f"Exported {result['projects_exported']} projects")
for project, info in result['project_files'].items():
    print(f"  {project}: {info['tasks_count']} tasks")
```

### Import with Conflict Resolution

```python
from src.oos_task_system.jsonl_import import ConflictResolution

# Import with specific conflict resolution strategy
result = db.import_tasks(
    "tasks.jsonl",
    conflict_resolution=ConflictResolution.MERGE,
    validate=True,
    strict_validation=False,
    dry_run=False
)
```

### Custom Filtering

```python
# Export tasks with custom filter
def is_urgent_task(task):
    return task.priority.value == "urgent" and "critical" in task.tags

result = db.export_tasks(
    "urgent_tasks.jsonl",
    custom_filter=is_urgent_task
)
```

## Conflict Resolution Strategies

### Skip (default)
- Skip tasks that already exist in the database
- Existing tasks remain unchanged
- Only new tasks are imported

```python
result = db.import_tasks("tasks.jsonl", conflict_resolution=ConflictResolution.SKIP)
```

### Overwrite
- Replace existing tasks with imported versions
- All task data comes from import file
- Useful for full restoration from backup

```python
result = db.import_tasks("tasks.jsonl", conflict_resolution=ConflictResolution.OVERWRITE)
```

### Merge
- Intelligently merge existing and imported tasks
- Prefer newer data based on `updated_at` timestamp
- Combine tags, dependencies, and context fields
- Best for collaborative editing scenarios

```python
result = db.import_tasks("tasks.jsonl", conflict_resolution=ConflictResolution.MERGE)
```

### Create New
- Create new tasks with generated IDs for conflicts
- Original tasks remain unchanged
- Import metadata tracks original task IDs
- Useful for preserving history while importing updates

```python
result = db.import_tasks("tasks.jsonl", conflict_resolution=ConflictResolution.CREATE_NEW)
```

## File Format

### JSONL Structure

Each line in a JSONL file contains a single JSON object:

```json
{"id": "task123", "title": "Implement feature", "status": "todo", "priority": "medium", "created_at": "2024-01-01T10:00:00"}
{"id": "task124", "title": "Write tests", "status": "doing", "priority": "high", "depends_on": ["task123"], "created_at": "2024-01-01T11:00:00"}
```

### Metadata Header (optional)

```json
{"__metadata__": {"version": "1.0", "exported_at": "2024-01-01T12:00:00", "total_tasks": 2}}
```

### Task Object Schema

```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "status": "todo|doing|technical-complete|ruat-validation|review|done|blocked|cancelled",
  "priority": "low|medium|high|urgent",
  "tags": ["string"],
  "depends_on": ["string"],
  "blocks": ["string"],
  "assignee": "string|null",
  "created_at": "ISO8601 datetime",
  "updated_at": "ISO8601 datetime",
  "completed_at": "ISO8601 datetime|null",
  "due_date": "ISO8601 datetime|null",
  "estimated_hours": "number|null",
  "actual_hours": "number|null",
  "context": {"key": "value"},
  "__exported_at__": "ISO8601 datetime"  # Added during export
}
```

## Command Line Integration

The export/import functionality integrates with OOS CLI commands:

```bash
# Export all tasks
oos task export all --output tasks.jsonl

# Export filtered tasks
oos task export --status todo --assignee alice --output alice-tasks.jsonl

# Import tasks
oos task import tasks.jsonl --resolution merge

# Preview import
oos task import tasks.jsonl --dry-run --validate

# Sync with remote JSONL file
oos task sync remote-tasks.jsonl --resolution merge
```

## Best Practices

### Git Workflow

1. **Commit Regularly**: Export and commit JSONL files regularly
2. **Use Descriptive Names**: Name export files clearly (e.g., `tasks-2024-01-01.jsonl`)
3. **Review Conflicts**: Use `--dry-run` before importing to review conflicts
4. **Backup Before Sync**: Always sync creates automatic backups

### Performance

1. **Large Projects**: Use compression (`.jsonl.gz`) for large task collections
2. **Filtering**: Filter exports to reduce file size when sharing subsets
3. **Incremental**: Use incremental exports for frequent backups

### Collaboration

1. **Merge Strategy**: Use `merge` resolution for collaborative editing
2. **Validation**: Enable validation to catch data issues
3. **Communication**: Document any custom filtering or transformation

### Data Integrity

1. **Validation**: Always validate imports in production environments
2. **Backups**: Keep multiple backup files at different time points
3. **Testing**: Test import/export workflows with `--dry-run` first

## Error Handling

### Common Export Errors

- **Permission Denied**: Check write permissions to output directory
- **Disk Space**: Use compression or reduce export scope
- **Invalid Filters**: Verify filter values and data types

### Common Import Errors

- **File Not Found**: Verify file path and permissions
- **Invalid JSON**: Check file format and encoding
- **Validation Failures**: Review task data against schema requirements
- **Conflicts**: Choose appropriate conflict resolution strategy

### Recovery

1. **Backup Files**: Sync operations create automatic backups
2. **Rollback**: Use backup files to restore previous state
3. **Partial Imports**: Import operations continue on individual task failures

## Integration Examples

### CI/CD Pipeline

```python
# Export tasks for CI/CD backup
def backup_tasks():
    db = TaskDatabase("project/.oos/tasks/tasks.db")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = db.export_tasks(f"backup/tasks-{timestamp}.jsonl", compress=True)

    if not result['success']:
        raise Exception(f"Backup failed: {result.get('error', 'Unknown error')}")

    return result['backup_path']

# Import tasks during deployment
def restore_tasks(backup_file):
    db = TaskDatabase("project/.oos/tasks/tasks.db")
    result = db.import_tasks(
        backup_file,
        conflict_resolution=ConflictResolution.OVERWRITE,
        validate=True
    )

    if not result['success']:
        raise Exception(f"Restore failed: {result['errors']}")

    return result
```

### Cross-Project Templates

```python
# Export project template
def create_project_template(source_db, output_file):
    exporter = TaskExporter(source_db)

    # Export only structure (no assignees, no actual work)
    result = exporter.export_filtered_tasks(
        output_file,
        custom_filter=lambda task: task.status in [TaskStatus.TODO],
        exclude_fields=['assignee', 'actual_hours', 'completed_at']
    )

    return result

# Import template into new project
def use_project_template(target_db, template_file):
    result = target_db.import_tasks(
        template_file,
        conflict_resolution=ConflictResolution.CREATE_NEW,
        import_metadata={'source': 'template', 'imported_at': datetime.now().isoformat()}
    )

    return result
```

## API Reference

### TaskDatabase Methods

- `export_tasks(output_path, **options)`: Export tasks to JSONL
- `import_tasks(input_path, **options)`: Import tasks from JSONL
- `sync_tasks(jsonl_path, conflict_resolution)`: Sync with JSONL file

### TaskExporter Methods

- `export_all_tasks(output_path, **options)`: Export all tasks
- `export_filtered_tasks(output_path, **filters, **options)`: Export with filters
- `export_incremental(output_path, since, **options)`: Incremental export
- `export_by_project(output_dir, **options)`: Export by project
- `estimate_export_size(tasks, compress)`: Estimate file size

### TaskImporter Methods

- `import_tasks(input_path, **options)`: Import tasks
- `import_incremental(input_path, since, **options)`: Incremental import
- `import_from_multiple_files(input_paths, **options)`: Multiple file import
- `validate_import_file(input_path)`: Validate file without importing
- `get_import_preview(input_path)`: Get file preview

### Export Options

- `compress`: Enable gzip compression (bool)
- `include_metadata`: Include metadata header (bool)
- `sort_by`: Sort field (str)
- `reverse_sort`: Reverse sort order (bool)
- `exclude_fields`: Fields to exclude (list)
- `pretty_format`: Pretty JSON formatting (bool)

### Import Options

- `conflict_resolution`: Conflict strategy (str)
- `dry_run`: Preview without changes (bool)
- `validate`: Validate tasks (bool)
- `strict_validation`: Strict validation mode (bool)
- `import_metadata`: Metadata to add (dict)