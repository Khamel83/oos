"""
Click-based CLI interface for OOS Task Memory System.

Provides comprehensive command-line interface for task management,
dependency tracking, and export/import operations.
"""

import click
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from .models import Task, TaskStatus, TaskPriority
from .database import TaskDatabase
from .dependencies import DependencyGraph, CyclicDependencyError
from .validation import TaskValidator, ValidationError
from .jsonl_export import TaskExporter, ExportError
from .jsonl_import import TaskImporter, ImportResult, ConflictResolution


class TaskCLI:
    """Main CLI application for task management."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize CLI with database path."""
        if db_path is None:
            # Default to .oos/tasks/tasks.db in current directory
            db_path = ".oos/tasks/tasks.db"

        self.db_path = db_path
        self.db = None
        self.validator = TaskValidator()

    def _get_database(self) -> TaskDatabase:
        """Get database connection, creating if necessary."""
        if self.db is None:
            self.db = TaskDatabase(self.db_path)
        return self.db

    def _print_task(self, task: Task, detailed: bool = False, json_output: bool = False):
        """Print task information in specified format."""
        if json_output:
            data = task.to_dict()
            print(json.dumps(data, indent=2))
        else:
            status_icon = self._get_status_icon(task.status)
            priority_icon = self._get_priority_icon(task.priority)

            # Basic task line
            line = f"{status_icon} {priority_icon} {task.id[:8]}: {task.title}"

            if task.assignee:
                line += f" (@{task.assignee})"

            print(line)

            if detailed:
                # Additional details
                if task.description:
                    print(f"  Description: {task.description}")

                if task.tags:
                    print(f"  Tags: {', '.join(task.tags)}")

                if task.depends_on:
                    print(f"  Depends on: {', '.join(task.depends_on)}")

                if task.context:
                    context_items = [f"{k}={v}" for k, v in task.context.items() if k != 'imported_at']
                    if context_items:
                        print(f"  Context: {', '.join(context_items)}")

                print(f"  Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
                print(f"  Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M')}")

                if task.completed_at:
                    print(f"  Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}")

    def _get_status_icon(self, status: TaskStatus) -> str:
        """Get icon for task status."""
        icons = {
            TaskStatus.TODO: "⏳",
            TaskStatus.DOING: "🚀",
            TaskStatus.TECHNICAL_COMPLETE: "✅",
            TaskStatus.RUAT_VALIDATION: "🧪",
            TaskStatus.REVIEW: "👀",
            TaskStatus.DONE: "✨",
            TaskStatus.BLOCKED: "🚫",
            TaskStatus.CANCELLED: "❌"
        }
        return icons.get(status, "❓")

    def _get_priority_icon(self, priority: TaskPriority) -> str:
        """Get icon for task priority."""
        icons = {
            TaskPriority.LOW: "🔵",
            TaskPriority.MEDIUM: "🟡",
            TaskPriority.HIGH: "🟠",
            TaskPriority.URGENT: "🔴"
        }
        return icons.get(priority, "⚪")

    def _parse_tags(self, tags_str: str) -> List[str]:
        """Parse comma-separated tags string."""
        if not tags_str:
            return []
        return [tag.strip() for tag in tags_str.split(',') if tag.strip()]

    def _parse_dependencies(self, deps_str: str) -> List[str]:
        """Parse comma-separated dependencies string."""
        if not deps_str:
            return []
        return [dep.strip() for dep in deps_str.split(',') if dep.strip()]

    def _parse_context(self, context_str: str) -> Dict[str, Any]:
        """Parse context string (key=value pairs separated by commas)."""
        if not context_str:
            return {}

        context = {}
        for pair in context_str.split(','):
            if '=' in pair:
                key, value = pair.strip().split('=', 1)
                # Try to parse as JSON for complex values
                try:
                    context[key] = json.loads(value)
                except json.JSONDecodeError:
                    context[key] = value
        return context

    def _error(self, message: str, exit_code: int = 1):
        """Print error message and exit."""
        click.echo(f"Error: {message}", err=True)
        sys.exit(exit_code)

    def _success(self, message: str):
        """Print success message."""
        click.echo(f"✅ {message}")

    def _warning(self, message: str):
        """Print warning message."""
        click.echo(f"⚠️  {message}")

    def _info(self, message: str):
        """Print info message."""
        click.echo(f"ℹ️  {message}")


@click.group()
@click.option('--db-path', default='.oos/tasks/tasks.db', help='Database file path')
@click.pass_context
def cli(ctx, db_path):
    """OOS Task Memory System - Project-embedded task management."""
    ctx.ensure_object(dict)
    ctx.obj['cli'] = TaskCLI(db_path)


@cli.command()
@click.argument('title')
@click.option('--description', '-d', help='Task description')
@click.option('--status', '-s', type=click.Choice(['todo', 'doing', 'technical-complete', 'ruat-validation', 'review', 'done', 'blocked', 'cancelled']), default='todo', help='Task status')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high', 'urgent']), default='medium', help='Task priority')
@click.option('--assignee', '-a', help='Task assignee')
@click.option('--tags', '-t', help='Comma-separated tags')
@click.option('--depends-on', help='Comma-separated task IDs this task depends on')
@click.option('--context', help='Context as key=value pairs (comma-separated)')
@click.option('--estimated-hours', type=float, help='Estimated hours')
@click.option('--due-date', help='Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM)')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
@click.pass_context
def create(ctx, title, description, status, priority, assignee, tags, depends_on, context, estimated_hours, due_date, json_output):
    """Create a new task."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        # Parse due date
        due_date_obj = None
        if due_date:
            try:
                # Try parsing as datetime
                due_date_obj = datetime.fromisoformat(due_date.replace(' ', 'T'))
            except ValueError:
                # Try parsing as date only
                try:
                    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                except ValueError:
                    task_cli._error(f"Invalid due date format: {due_date}")

        # Create task
        task = Task(
            title=title,
            description=description or "",
            status=TaskStatus(status),
            priority=TaskPriority(priority),
            assignee=assignee,
            tags=task_cli._parse_tags(tags),
            depends_on=task_cli._parse_dependencies(depends_on),
            context=task_cli._parse_context(context),
            estimated_hours=estimated_hours,
            due_date=due_date_obj
        )

        # Validate task
        validation_result = task_cli.validator.validate_task(task, strict=False)
        if not validation_result.is_valid:
            for error in validation_result.errors:
                task_cli._error(f"Validation error: {error.field}: {error.message}")

        # Show warnings
        for warning in validation_result.warnings:
            task_cli._warning(warning)

        # Create task in database
        created_task = db.create_task(task)

        if json_output:
            print(json.dumps(created_task.to_dict(), indent=2))
        else:
            task_cli._success(f"Created task {created_task.id[:8]}: {created_task.title}")
            task_cli._print_task(created_task)

    except Exception as e:
        task_cli._error(f"Failed to create task: {str(e)}")


@cli.command()
@click.option('--status', '-s', type=click.Choice(['todo', 'doing', 'technical-complete', 'ruat-validation', 'review', 'done', 'blocked', 'cancelled']), help='Filter by status')
@click.option('--assignee', '-a', help='Filter by assignee')
@click.option('--tags', '-t', help='Filter by tags (comma-separated, OR logic)')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high', 'urgent']), help='Filter by priority')
@click.option('--ready', is_flag=True, help='Show only ready tasks (no pending dependencies)')
@click.option('--blocked', is_flag=True, help='Show only blocked tasks')
@click.option('--limit', '-n', type=int, help='Limit number of results')
@click.option('--sort', type=click.Choice(['created', 'updated', 'title', 'priority', 'status']), default='created', help='Sort field')
@click.option('--reverse', is_flag=True, help='Reverse sort order')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
@click.option('--count', is_flag=True, help='Show only count')
@click.pass_context
def list(ctx, status, assignee, tags, priority, ready, blocked, limit, sort, reverse, json_output, count):
    """List tasks with optional filtering."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        # Get tasks based on filters
        if ready:
            tasks = db.get_ready_tasks()
        elif blocked:
            tasks = db.get_blocked_tasks()
        else:
            # Apply filters
            status_filter = TaskStatus(status) if status else None
            tag_filter = task_cli._parse_tags(tags)

            tasks = db.list_tasks(
                status=status_filter,
                assignee=assignee
            )

            # Additional filtering
            if tag_filter:
                tasks = [task for task in tasks if any(tag in task.tags for tag in tag_filter)]

            if priority:
                tasks = [task for task in tasks if task.priority.value == priority]

        # Apply limit
        if limit:
            tasks = tasks[:limit]

        # Sort tasks
        if sort == 'created':
            tasks.sort(key=lambda t: t.created_at, reverse=not reverse)
        elif sort == 'updated':
            tasks.sort(key=lambda t: t.updated_at, reverse=not reverse)
        elif sort == 'title':
            tasks.sort(key=lambda t: t.title.lower(), reverse=reverse)
        elif sort == 'priority':
            priority_order = {'low': 1, 'medium': 2, 'high': 3, 'urgent': 4}
            tasks.sort(key=lambda t: priority_order[t.priority.value], reverse=reverse)
        elif sort == 'status':
            status_order = {'todo': 1, 'doing': 2, 'technical-complete': 3, 'ruat-validation': 4, 'review': 5, 'done': 6}
            tasks.sort(key=lambda t: status_order.get(t.status.value, 0), reverse=reverse)

        if count:
            if json_output:
                print(json.dumps({'count': len(tasks)}))
            else:
                print(f"Total tasks: {len(tasks)}")
            return

        if json_output:
            tasks_data = [task.to_dict() for task in tasks]
            print(json.dumps(tasks_data, indent=2))
        else:
            if not tasks:
                task_cli._info("No tasks found")
                return

            print(f"Found {len(tasks)} task(s):")
            print()
            for task in tasks:
                task_cli._print_task(task)

    except Exception as e:
        task_cli._error(f"Failed to list tasks: {str(e)}")


@cli.command()
@click.argument('task_id')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
@click.pass_context
def show(ctx, task_id, json_output):
    """Show detailed information about a task."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        task = db.get_task(task_id)
        if not task:
            task_cli._error(f"Task {task_id} not found")

        task_cli._print_task(task, detailed=True, json_output=json_output)

    except Exception as e:
        task_cli._error(f"Failed to show task: {str(e)}")


@cli.command()
@click.argument('task_id')
@click.option('--title', help='New task title')
@click.option('--description', '-d', help='New task description')
@click.option('--status', '-s', type=click.Choice(['todo', 'doing', 'technical-complete', 'ruat-validation', 'review', 'done', 'blocked', 'cancelled']), help='New task status')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high', 'urgent']), help='New task priority')
@click.option('--assignee', '-a', help='New task assignee')
@click.option('--add-tags', help='Tags to add (comma-separated)')
@click.option('--remove-tags', help='Tags to remove (comma-separated)')
@click.option('--add-dependencies', help='Dependencies to add (comma-separated)')
@click.option('--remove-dependencies', help='Dependencies to remove (comma-separated)')
@click.option('--estimated-hours', type=float, help='New estimated hours')
@click.option('--actual-hours', type=float, help='Add actual hours')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
@click.pass_context
def update(ctx, task_id, title, description, status, priority, assignee, add_tags, remove_tags, add_dependencies, remove_dependencies, estimated_hours, actual_hours, json_output):
    """Update an existing task."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        task = db.get_task(task_id)
        if not task:
            task_cli._error(f"Task {task_id} not found")

        # Update fields
        if title:
            task.title = title
        if description is not None:
            task.description = description
        if status:
            task.update_status(TaskStatus(status))
        if priority:
            task.priority = TaskPriority(priority)
        if assignee:
            task.assignee = assignee

        # Handle tags
        if add_tags:
            for tag in task_cli._parse_tags(add_tags):
                task.add_tag(tag)

        if remove_tags:
            for tag in task_cli._parse_tags(remove_tags):
                task.remove_tag(tag)

        # Handle dependencies
        if add_dependencies:
            for dep in task_cli._parse_dependencies(add_dependencies):
                task.add_dependency(dep)

        if remove_dependencies:
            for dep in task_cli._parse_dependencies(remove_dependencies):
                task.remove_dependency(dep)

        if estimated_hours is not None:
            task.estimated_hours = estimated_hours

        if actual_hours is not None:
            if task.actual_hours is None:
                task.actual_hours = actual_hours
            else:
                task.actual_hours += actual_hours

        # Validate updated task
        validation_result = task_cli.validator.validate_task(task, strict=False)
        if not validation_result.is_valid:
            for error in validation_result.errors:
                task_cli._error(f"Validation error: {error.field}: {error.message}")

        # Show warnings
        for warning in validation_result.warnings:
            task_cli._warning(warning)

        # Update task in database
        updated_task = db.update_task(task)

        if json_output:
            print(json.dumps(updated_task.to_dict(), indent=2))
        else:
            task_cli._success(f"Updated task {updated_task.id[:8]}: {updated_task.title}")
            task_cli._print_task(updated_task)

    except Exception as e:
        task_cli._error(f"Failed to update task: {str(e)}")


@cli.command()
@click.argument('task_id')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete(ctx, task_id, confirm):
    """Delete a task."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        task = db.get_task(task_id)
        if not task:
            task_cli._error(f"Task {task_id} not found")

        if not confirm:
            if not click.confirm(f"Delete task {task.id[:8]}: {task.title}?"):
                task_cli._info("Deletion cancelled")
                return

        # Check if other tasks depend on this one
        blocking_tasks = db.list_tasks()
        dependent_tasks = [t for t in blocking_tasks if task_id in t.depends_on]

        if dependent_tasks:
            task_cli._warning(f"Warning: {len(dependent_tasks)} task(s) depend on this task:")
            for dep_task in dependent_tasks:
                print(f"  - {dep_task.id[:8]}: {dep_task.title}")

            if not confirm:
                if not click.confirm("Proceed with deletion?"):
                    task_cli._info("Deletion cancelled")
                    return

        success = db.delete_task(task_id)
        if success:
            task_cli._success(f"Deleted task {task.id[:8]}: {task.title}")
        else:
            task_cli._error("Failed to delete task")

    except Exception as e:
        task_cli._error(f"Failed to delete task: {str(e)}")


@cli.command()
@click.argument('task_id')
@click.pass_context
def complete(ctx, task_id):
    """Mark a task as complete."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        task = db.get_task(task_id)
        if not task:
            task_cli._error(f"Task {task_id} not found")

        task.mark_complete()
        updated_task = db.update_task(task)

        task_cli._success(f"Completed task {updated_task.id[:8]}: {updated_task.title}")

    except Exception as e:
        task_cli._error(f"Failed to complete task: {str(e)}")


@cli.command()
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
@click.option('--limit', '-n', type=int, help='Limit number of results')
@click.pass_context
def ready(ctx, json_output, limit):
    """Show tasks ready to work on (no pending dependencies)."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        ready_tasks = db.get_ready_tasks()

        if limit:
            ready_tasks = ready_tasks[:limit]

        if json_output:
            tasks_data = [task.to_dict() for task in ready_tasks]
            print(json.dumps(tasks_data, indent=2))
        else:
            if not ready_tasks:
                task_cli._info("No tasks ready to work on")
                return

            print(f"🚀 {len(ready_tasks)} task(s) ready to work on:")
            print()
            for task in ready_tasks:
                task_cli._print_task(task)

    except Exception as e:
        task_cli._error(f"Failed to get ready tasks: {str(e)}")


@cli.command()
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
@click.pass_context
def blocked(ctx, json_output):
    """Show tasks blocked by dependencies."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        blocked_tasks = db.get_blocked_tasks()

        if json_output:
            tasks_data = [task.to_dict() for task in blocked_tasks]
            print(json.dumps(tasks_data, indent=2))
        else:
            if not blocked_tasks:
                task_cli._info("No blocked tasks")
                return

            print(f"🚫 {len(blocked_tasks)} task(s) blocked by dependencies:")
            print()
            for task in blocked_tasks:
                task_cli._print_task(task)
                # Show what's blocking this task
                blocking_tasks = []
                for dep_id in task.depends_on:
                    dep_task = db.get_task(dep_id)
                    if dep_task and dep_task.status != TaskStatus.DONE:
                        blocking_tasks.append(f"{dep_task.id[:8]} ({dep_task.status.value})")

                if blocking_tasks:
                    print(f"  Blocked by: {', '.join(blocking_tasks)}")
                print()

    except Exception as e:
        task_cli._error(f"Failed to get blocked tasks: {str(e)}")


@cli.command()
@click.option('--output', '-o', default='tasks.jsonl', help='Output file path')
@click.option('--compress', is_flag=True, help='Compress output with gzip')
@click.option('--status', multiple=True, type=click.Choice(['todo', 'doing', 'technical-complete', 'ruat-validation', 'review', 'done', 'blocked', 'cancelled']), help='Filter by status')
@click.option('--assignee', help='Filter by assignee')
@click.option('--tags', help='Filter by tags (comma-separated)')
@click.option('--sort', type=click.Choice(['created', 'updated', 'title', 'priority', 'status']), default='created', help='Sort field')
@click.option('--reverse', is_flag=True, help='Reverse sort order')
@click.option('--exclude-fields', help='Fields to exclude (comma-separated)')
@click.pass_context
def export(ctx, output, compress, status, assignee, tags, sort, reverse, exclude_fields):
    """Export tasks to JSONL file."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        exporter = TaskExporter(db)

        # Parse filters
        status_filter = [TaskStatus(s) for s in status] if status else None
        tag_filter = task_cli._parse_tags(tags)
        exclude_fields_list = task_cli._parse_tags(exclude_fields)

        # Map CLI sort names to exporter sort names
        sort_field_map = {
            'created': 'created_at',
            'updated': 'updated_at',
            'title': 'title',
            'priority': 'priority',
            'status': 'status'
        }
        sort_field = sort_field_map.get(sort, 'created_at')

        # Export tasks
        result = exporter.export_filtered_tasks(
            output,
            status_filter=status_filter,
            assignee_filter=assignee,
            tag_filter=tag_filter,
            sort_by=sort_field,
            reverse_sort=reverse,
            exclude_fields=exclude_fields_list,
            compress=compress
        )

        if result['success']:
            task_cli._success(f"Exported {result['exported_tasks']} tasks to {output}")
            if compress:
                task_cli._info(f"File size: {result['file_size_bytes']} bytes (compressed)")
            else:
                task_cli._info(f"File size: {result['file_size_bytes']} bytes")
        else:
            task_cli._error(f"Export failed: {result.get('error', 'Unknown error')}")

    except ExportError as e:
        task_cli._error(f"Export failed: {str(e)}")
    except Exception as e:
        task_cli._error(f"Export failed: {str(e)}")


@cli.command()
@click.argument('input_file')
@click.option('--resolution', type=click.Choice(['skip', 'overwrite', 'merge', 'create-new']), default='skip', help='Conflict resolution strategy')
@click.option('--dry-run', is_flag=True, help='Preview import without making changes')
@click.option('--validate', is_flag=True, default=True, help='Validate tasks before importing')
@click.option('--strict', is_flag=True, help='Use strict validation')
@click.pass_context
def import_tasks(ctx, input_file, resolution, dry_run, validate, strict):
    """Import tasks from JSONL file."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        importer = TaskImporter(db)

        # Get preview if dry run
        if dry_run:
            preview = importer.get_import_preview(input_file)
            if 'error' in preview:
                task_cli._error(f"Preview failed: {preview['error']}")

            task_cli._info(f"Preview: {preview['total_tasks']} tasks in file")
            for task_summary in preview['preview_tasks']:
                print(f"  {task_summary['id'][:8]}: {task_summary['title']} ({task_summary['status']})")

            if not click.confirm("Proceed with import?"):
                task_cli._info("Import cancelled")
                return

        # Import tasks
        result = importer.import_tasks(
            input_file,
            conflict_resolution=resolution,
            dry_run=dry_run,
            validate=validate,
            strict_validation=strict
        )

        if result.success:
            task_cli._success(f"Import completed successfully")
            task_cli._info(f"  Tasks imported: {result.tasks_imported}")
            task_cli._info(f"  Tasks updated: {result.tasks_updated}")
            task_cli._info(f"  Tasks skipped: {result.tasks_skipped}")
            task_cli._info(f"  Processing time: {result.processing_time:.2f}s")

            if result.warnings:
                task_cli._warning("Warnings:")
                for warning in result.warnings:
                    print(f"  - {warning}")
        else:
            task_cli._error(f"Import failed: {len(result.errors)} error(s)")
            for error in result.errors:
                print(f"  - {error}")

    except Exception as e:
        task_cli._error(f"Import failed: {str(e)}")


@cli.command()
@click.argument('jsonl_file')
@click.option('--resolution', type=click.Choice(['skip', 'overwrite', 'merge', 'create-new']), default='merge', help='Conflict resolution strategy')
@click.pass_context
def sync(ctx, jsonl_file, resolution):
    """Synchronize tasks with JSONL file (export + import)."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        result = db.sync_tasks(jsonl_file, conflict_resolution=resolution)

        if result['success']:
            task_cli._success(f"Sync completed successfully")
            task_cli._info(f"  Backup exported: {result['backup_exported']} tasks")
            task_cli._info(f"  Tasks imported: {result['tasks_imported']}")
            task_cli._info(f"  Tasks updated: {result['tasks_updated']}")
            task_cli._info(f"  Tasks skipped: {result['tasks_skipped']}")
            task_cli._info(f"  Backup file: {result['backup_path']}")
        else:
            task_cli._error(f"Sync failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        task_cli._error(f"Sync failed: {str(e)}")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show database statistics."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        stats = db.get_stats()

        print(f"📊 Task Database Statistics")
        print(f"  Database: {stats['db_path']}")
        print(f"  Total tasks: {stats['total_tasks']}")
        print(f"  File size: {stats['db_size_bytes']} bytes")
        print()
        print("  Status breakdown:")
        for status, count in stats['status_counts'].items():
            icon = task_cli._get_status_icon(TaskStatus(status))
            print(f"    {icon} {status}: {count}")

    except Exception as e:
        task_cli._error(f"Failed to get stats: {str(e)}")


@cli.command()
@click.argument('task_id', required=False)
@click.option('--all-tasks', is_flag=True, help='Validate all tasks')
@click.pass_context
def validate(ctx, task_id, all_tasks):
    """Validate task(s)."""
    task_cli = ctx.obj['cli']
    db = task_cli._get_database()

    try:
        if task_id:
            # Validate specific task
            task = db.get_task(task_id)
            if not task:
                task_cli._error(f"Task {task_id} not found")

            validation_result = task_cli.validator.validate_task(task, strict=True)

            if validation_result.is_valid:
                task_cli._success(f"Task {task_id[:8]} is valid")
            else:
                task_cli._error(f"Task {task_id[:8]} has validation errors:")
                for error in validation_result.errors:
                    print(f"  - {error.field}: {error.message}")

            if validation_result.warnings:
                task_cli._warning("Warnings:")
                for warning in validation_result.warnings:
                    print(f"  - {warning}")

        elif all_tasks:
            # Validate all tasks
            tasks = db.list_tasks()
            total_errors = 0
            total_warnings = 0

            for task in tasks:
                validation_result = task_cli.validator.validate_task(task, strict=True)

                if not validation_result.is_valid:
                    print(f"❌ {task.id[:8]}: {task.title}")
                    for error in validation_result.errors:
                        print(f"    - {error.field}: {error.message}")
                    total_errors += len(validation_result.errors)

                total_warnings += len(validation_result.warnings)

            if total_errors == 0:
                task_cli._success(f"All {len(tasks)} tasks are valid")
            else:
                task_cli._error(f"Found {total_errors} validation errors across {len(tasks)} tasks")

            if total_warnings > 0:
                task_cli._warning(f"Total warnings: {total_warnings}")

        else:
            task_cli._error("Either provide TASK_ID or use --all-tasks")

    except Exception as e:
        task_cli._error(f"Validation failed: {str(e)}")


if __name__ == '__main__':
    cli()