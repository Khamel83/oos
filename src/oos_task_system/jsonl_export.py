"""
JSONL export functionality for OOS Task Memory System.

Provides git-syncable task export with filtering, formatting,
and incremental export capabilities.
"""

import gzip
import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from .database import TaskDatabase
from .models import Task, TaskStatus


class ExportError(Exception):
    """Raised when export operations fail."""
    pass


class TaskExporter:
    """
    Exports tasks to JSONL format for git synchronization.

    Supports filtering, compression, incremental exports,
    and custom formatting options.
    """

    def __init__(self, database: TaskDatabase):
        """Initialize exporter with database connection."""
        self.database = database
        self.export_metadata = {
            'version': '1.0',
            'exported_at': None,
            'total_tasks': 0,
            'exported_tasks': 0,
            'filters_applied': [],
            'format_options': {}
        }

    def export_all_tasks(self, output_path: str, **options) -> dict[str, Any]:
        """
        Export all tasks to JSONL file.

        Args:
            output_path: Path to output JSONL file
            **options: Export options (compress, include_metadata, etc.)

        Returns:
            Export summary with statistics
        """
        tasks = self.database.list_tasks()
        return self._export_tasks(tasks, output_path, **options)

    def export_filtered_tasks(self, output_path: str,
                            status_filter: list[TaskStatus] | None = None,
                            assignee_filter: str | None = None,
                            tag_filter: list[str] | None = None,
                            date_range: tuple | None = None,
                            custom_filter: Callable[[Task], bool] | None = None,
                            **options) -> dict[str, Any]:
        """
        Export tasks with filtering options.

        Args:
            output_path: Path to output JSONL file
            status_filter: List of statuses to include
            assignee_filter: Assignee to filter by
            tag_filter: Tags to filter by (OR logic)
            date_range: (start_date, end_date) tuple for created_at filtering
            custom_filter: Custom function to filter tasks
            **options: Export options

        Returns:
            Export summary with statistics
        """
        tasks = self.database.list_tasks()

        # Apply filters
        filtered_tasks = self._apply_filters(
            tasks, status_filter, assignee_filter, tag_filter,
            date_range, custom_filter
        )

        # Track applied filters
        filters_applied = []
        if status_filter:
            filters_applied.append(f"status: {[s.value for s in status_filter]}")
        if assignee_filter:
            filters_applied.append(f"assignee: {assignee_filter}")
        if tag_filter:
            filters_applied.append(f"tags: {tag_filter}")
        if date_range:
            filters_applied.append(f"date_range: {date_range}")
        if custom_filter:
            filters_applied.append("custom_filter: applied")

        self.export_metadata['filters_applied'] = filters_applied

        return self._export_tasks(filtered_tasks, output_path, **options)

    def export_incremental(self, output_path: str, since: datetime, **options) -> dict[str, Any]:
        """
        Export tasks modified since a specific date.

        Args:
            output_path: Path to output JSONL file
            since: Export tasks updated after this date
            **options: Export options

        Returns:
            Export summary with statistics
        """
        tasks = self.database.list_tasks()
        incremental_tasks = [task for task in tasks if task.updated_at > since]

        self.export_metadata['filters_applied'] = [f"incremental_since: {since.isoformat()}"]

        return self._export_tasks(incremental_tasks, output_path, **options)

    def export_by_project(self, output_dir: str, project_field: str = "project", **options) -> dict[str, Any]:
        """
        Export tasks grouped by project into separate files.

        Args:
            output_dir: Directory to create project files in
            project_field: Context field to group by (default: "project")
            **options: Export options

        Returns:
            Summary of all project exports
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        tasks = self.database.list_tasks()

        # Group tasks by project
        projects = {}
        unassigned_tasks = []

        for task in tasks:
            project = task.context.get(project_field)
            if project:
                if project not in projects:
                    projects[project] = []
                projects[project].append(task)
            else:
                unassigned_tasks.append(task)

        # Export each project
        export_summary = {
            'projects_exported': 0,
            'total_tasks_exported': 0,
            'project_files': {},
            'unassigned_tasks': len(unassigned_tasks)
        }

        for project_name, project_tasks in projects.items():
            safe_name = self._sanitize_filename(project_name)
            project_file = output_path / f"{safe_name}.jsonl"

            project_summary = self._export_tasks(project_tasks, str(project_file), **options)
            export_summary['project_files'][project_name] = {
                'file': str(project_file),
                'tasks_count': project_summary['exported_tasks']
            }
            export_summary['total_tasks_exported'] += project_summary['exported_tasks']
            export_summary['projects_exported'] += 1

        # Export unassigned tasks if any
        if unassigned_tasks:
            unassigned_file = output_path / "unassigned.jsonl"
            unassigned_summary = self._export_tasks(unassigned_tasks, str(unassigned_file), **options)
            export_summary['project_files']['unassigned'] = {
                'file': str(unassigned_file),
                'tasks_count': unassigned_summary['exported_tasks']
            }
            export_summary['total_tasks_exported'] += unassigned_summary['exported_tasks']

        return export_summary

    def _export_tasks(self, tasks: list[Task], output_path: str, **options) -> dict[str, Any]:
        """
        Internal method to export task list to JSONL.

        Args:
            tasks: List of tasks to export
            output_path: Output file path
            **options: Export options

        Returns:
            Export summary
        """
        compress = options.get('compress', False)
        include_metadata = options.get('include_metadata', True)
        sort_by = options.get('sort_by', 'created_at')
        reverse_sort = options.get('reverse_sort', False)
        exclude_fields = options.get('exclude_fields', [])
        pretty_format = options.get('pretty_format', False)

        # Update metadata
        self.export_metadata.update({
            'exported_at': datetime.now().isoformat(),
            'total_tasks': len(tasks),
            'exported_tasks': len(tasks),
            'format_options': {
                'compress': compress,
                'include_metadata': include_metadata,
                'sort_by': sort_by,
                'reverse_sort': reverse_sort,
                'exclude_fields': exclude_fields,
                'pretty_format': pretty_format
            }
        })

        try:
            # Sort tasks if requested
            if sort_by:
                tasks = self._sort_tasks(tasks, sort_by, reverse_sort)

            # Prepare output file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Write tasks
            if compress:
                with gzip.open(output_file, 'wt', encoding='utf-8') as f:
                    self._write_tasks_to_file(f, tasks, include_metadata, exclude_fields, pretty_format)
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    self._write_tasks_to_file(f, tasks, include_metadata, exclude_fields, pretty_format)

            return {
                'success': True,
                'output_path': str(output_file),
                'exported_tasks': len(tasks),
                'file_size_bytes': output_file.stat().st_size,
                'compressed': compress,
                'metadata': self.export_metadata.copy()
            }

        except Exception as e:
            raise ExportError(f"Failed to export tasks to {output_path}: {str(e)}")

    def _write_tasks_to_file(self, file, tasks: list[Task], include_metadata: bool,
                           exclude_fields: list[str], pretty_format: bool):
        """Write tasks to file handle."""
        # Write metadata header if requested
        if include_metadata:
            metadata_line = json.dumps({
                '__metadata__': self.export_metadata
            }, separators=(',', ':'))
            file.write(metadata_line + '\n')

        # Write tasks
        for task in tasks:
            task_data = self._prepare_task_data(task, exclude_fields)

            if pretty_format:
                task_line = json.dumps(task_data, indent=None, separators=(', ', ': '))
            else:
                task_line = json.dumps(task_data, separators=(',', ':'))

            file.write(task_line + '\n')

    def _prepare_task_data(self, task: Task, exclude_fields: list[str]) -> dict[str, Any]:
        """Prepare task data for export."""
        task_data = task.to_dict()

        # Remove excluded fields
        for field in exclude_fields:
            task_data.pop(field, None)

        # Add export timestamp
        task_data['__exported_at__'] = datetime.now().isoformat()

        return task_data

    def _apply_filters(self, tasks: list[Task], status_filter: list[TaskStatus] | None,
                      assignee_filter: str | None, tag_filter: list[str] | None,
                      date_range: tuple | None, custom_filter: Callable[[Task], bool] | None) -> list[Task]:
        """Apply filtering logic to task list."""
        filtered = tasks

        # Status filter
        if status_filter:
            filtered = [task for task in filtered if task.status in status_filter]

        # Assignee filter
        if assignee_filter:
            filtered = [task for task in filtered if task.assignee == assignee_filter]

        # Tag filter (OR logic)
        if tag_filter:
            filtered = [task for task in filtered
                       if any(tag in task.tags for tag in tag_filter)]

        # Date range filter
        if date_range:
            start_date, end_date = date_range
            filtered = [task for task in filtered
                       if start_date <= task.created_at <= end_date]

        # Custom filter
        if custom_filter:
            filtered = [task for task in filtered if custom_filter(task)]

        return filtered

    def _sort_tasks(self, tasks: list[Task], sort_by: str, reverse: bool) -> list[Task]:
        """Sort tasks by specified field."""
        sort_key_map = {
            'created_at': lambda t: t.created_at,
            'updated_at': lambda t: t.updated_at,
            'title': lambda t: t.title.lower(),
            'status': lambda t: t.status.value,
            'priority': lambda t: t.priority.value,
            'id': lambda t: t.id
        }

        if sort_by not in sort_key_map:
            raise ExportError(f"Invalid sort field: {sort_by}")

        return sorted(tasks, key=sort_key_map[sort_by], reverse=reverse)

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use as filename."""
        import re
        # Replace invalid filename characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Limit length
        sanitized = sanitized[:100]
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        return sanitized or 'unnamed'

    def get_export_formats(self) -> list[str]:
        """Get list of supported export formats."""
        return ['jsonl', 'jsonl.gz']

    def validate_export_path(self, path: str) -> tuple[bool, str]:
        """
        Validate export path and permissions.

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            output_path = Path(path)

            # Check if parent directory exists or can be created
            if not output_path.parent.exists():
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                except (OSError, PermissionError) as e:
                    return False, f"Cannot create directory: {e}"

            # Check write permissions
            if output_path.exists():
                if not output_path.is_file():
                    return False, "Path exists but is not a file"
                if not os.access(output_path, os.W_OK):
                    return False, "No write permission for existing file"
            else:
                # Check parent directory write permission
                import os
                if not os.access(output_path.parent, os.W_OK):
                    return False, "No write permission for directory"

            return True, ""

        except Exception as e:
            return False, f"Invalid path: {e}"

    def estimate_export_size(self, tasks: list[Task], compress: bool = False) -> dict[str, int]:
        """
        Estimate export file size.

        Args:
            tasks: Tasks to estimate size for
            compress: Whether compression will be used

        Returns:
            Size estimates in bytes
        """
        if not tasks:
            return {'uncompressed': 0, 'compressed': 0}

        # Sample a few tasks to estimate average size
        sample_size = min(10, len(tasks))
        sample_tasks = tasks[:sample_size]

        total_sample_size = 0
        for task in sample_tasks:
            task_json = json.dumps(task.to_dict(), separators=(',', ':'))
            total_sample_size += len(task_json.encode('utf-8')) + 1  # +1 for newline

        average_task_size = total_sample_size / sample_size
        estimated_uncompressed = int(average_task_size * len(tasks))

        # Estimate compression ratio (typical JSON compression is ~70%)
        estimated_compressed = int(estimated_uncompressed * 0.3) if compress else estimated_uncompressed

        return {
            'uncompressed': estimated_uncompressed,
            'compressed': estimated_compressed,
            'task_count': len(tasks),
            'average_task_size': int(average_task_size)
        }
