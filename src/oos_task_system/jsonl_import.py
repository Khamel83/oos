"""
JSONL import functionality for OOS Task Memory System.

Provides robust task import with conflict resolution,
validation, and incremental updates.
"""

import json
import gzip
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass

from .models import Task, TaskStatus, TaskPriority
from .database import TaskDatabase
from .validation import TaskValidator, ValidationResult


class ImportError(Exception):
    """Raised when import operations fail."""
    pass


class ConflictResolution:
    """Conflict resolution strategies."""
    SKIP = 'skip'  # Skip conflicting tasks
    OVERWRITE = 'overwrite'  # Replace existing tasks
    MERGE = 'merge'  # Merge with existing tasks (prefer newer)
    CREATE_NEW = 'create_new'  # Create new task with new ID


@dataclass
class ImportResult:
    """Result of import operation."""
    success: bool
    total_processed: int
    tasks_imported: int
    tasks_updated: int
    tasks_skipped: int
    tasks_failed: int
    errors: List[str]
    warnings: List[str]
    processing_time: float
    metadata: Dict[str, Any]


class TaskImporter:
    """
    Imports tasks from JSONL format into database.

    Supports conflict resolution, validation, and various import modes.
    """

    def __init__(self, database: TaskDatabase, validator: Optional[TaskValidator] = None):
        """Initialize importer with database and optional validator."""
        self.database = database
        self.validator = validator or TaskValidator()
        self.import_stats = {
            'processed': 0,
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'failed': 0,
            'errors': [],
            'warnings': []
        }

    def import_tasks(self, input_path: str,
                    conflict_resolution: str = ConflictResolution.SKIP,
                    dry_run: bool = False,
                    validate: bool = True,
                    strict_validation: bool = False,
                    import_metadata: Optional[Dict[str, Any]] = None) -> ImportResult:
        """
        Import tasks from JSONL file.

        Args:
            input_path: Path to JSONL file
            conflict_resolution: How to handle conflicts with existing tasks
            dry_run: Preview import without making changes
            validate: Validate tasks before importing
            strict_validation: Use strict validation rules
            import_metadata: Optional metadata to add to imported tasks

        Returns:
            ImportResult with detailed statistics
        """
        start_time = datetime.now()

        try:
            tasks = self._read_jsonl_file(input_path)
            return self._process_import(tasks, conflict_resolution, dry_run,
                                      validate, strict_validation, import_metadata, start_time)
        except Exception as e:
            return ImportResult(
                success=False,
                total_processed=0,
                tasks_imported=0,
                tasks_updated=0,
                tasks_skipped=0,
                tasks_failed=0,
                errors=[f"Failed to read file: {str(e)}"],
                warnings=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={}
            )

    def import_incremental(self, input_path: str,
                          since: datetime,
                          conflict_resolution: str = ConflictResolution.MERGE,
                          **kwargs) -> ImportResult:
        """
        Import tasks with incremental update logic.

        Only imports tasks that are newer than existing versions.

        Args:
            input_path: Path to JSONL file
            since: Only import tasks updated after this date
            **kwargs: Additional import options

        Returns:
            ImportResult with statistics
        """
        start_time = datetime.now()

        try:
            tasks = self._read_jsonl_file(input_path)
            # Filter for newer tasks
            newer_tasks = [task for task in tasks if task.updated_at > since]

            return self._process_import(newer_tasks, conflict_resolution,
                                      kwargs.get('dry_run', False),
                                      kwargs.get('validate', True),
                                      kwargs.get('strict_validation', False),
                                      kwargs.get('import_metadata'), start_time)
        except Exception as e:
            return ImportResult(
                success=False,
                total_processed=0,
                tasks_imported=0,
                tasks_updated=0,
                tasks_skipped=0,
                tasks_failed=0,
                errors=[f"Failed incremental import: {str(e)}"],
                warnings=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={'incremental_since': since.isoformat()}
            )

    def import_from_multiple_files(self, input_paths: List[str],
                                  conflict_resolution: str = ConflictResolution.SKIP,
                                  merge_strategy: str = 'first',
                                  **kwargs) -> ImportResult:
        """
        Import tasks from multiple JSONL files.

        Args:
            input_paths: List of JSONL file paths
            conflict_resolution: How to handle conflicts
            merge_strategy: How to merge duplicates across files
            **kwargs: Additional import options

        Returns:
            ImportResult with combined statistics
        """
        start_time = datetime.now()
        all_tasks = []
        file_stats = {}
        seen_task_ids = set()

        for file_path in input_paths:
            try:
                file_tasks = self._read_jsonl_file(file_path)

                # Handle merge strategy
                if merge_strategy == 'first':
                    filtered_tasks = [t for t in file_tasks if t.id not in seen_task_ids]
                    seen_task_ids.update(t.id for t in filtered_tasks)
                elif merge_strategy == 'last':
                    # Keep last occurrence (we'll deduplicate later)
                    filtered_tasks = file_tasks
                else:  # all
                    filtered_tasks = file_tasks

                all_tasks.extend(filtered_tasks)
                file_stats[file_path] = len(filtered_tasks)

            except Exception as e:
                self.import_stats['errors'].append(f"Failed to read {file_path}: {str(e)}")

        # Final deduplication for 'last' strategy
        if merge_strategy == 'last':
            task_dict = {}
            for task in all_tasks:
                task_dict[task.id] = task
            all_tasks = list(task_dict.values())

        kwargs['import_metadata'] = kwargs.get('import_metadata', {})
        kwargs['import_metadata']['imported_from_files'] = input_paths
        kwargs['import_metadata']['file_stats'] = file_stats
        kwargs['import_metadata']['merge_strategy'] = merge_strategy

        return self._process_import(all_tasks, conflict_resolution,
                                  kwargs.get('dry_run', False),
                                  kwargs.get('validate', True),
                                  kwargs.get('strict_validation', False),
                                  kwargs.get('import_metadata'), start_time)

    def _read_jsonl_file(self, input_path: str) -> List[Task]:
        """Read tasks from JSONL file."""
        tasks = []
        file_path = Path(input_path)

        if not file_path.exists():
            raise ImportError(f"File not found: {input_path}")

        try:
            # Determine if file is compressed
            open_func = gzip.open if input_path.endswith('.gz') else open

            with open_func(input_path, 'rt', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)

                        # Skip metadata lines
                        if '__metadata__' in data:
                            continue

                        # Parse task (remove export metadata if present)
                        task_data = data.copy()
                        task_data.pop('__exported_at__', None)

                        task = self._parse_task_data(task_data)
                        tasks.append(task)

                    except json.JSONDecodeError as e:
                        self.import_stats['errors'].append(
                            f"Line {line_num}: Invalid JSON: {str(e)}"
                        )
                    except Exception as e:
                        self.import_stats['errors'].append(
                            f"Line {line_num}: Task parsing failed: {str(e)}"
                        )

        except Exception as e:
            raise ImportError(f"Failed to read file {input_path}: {str(e)}")

        return tasks

    def _parse_task_data(self, data: Dict[str, Any]) -> Task:
        """Parse task data from JSON."""
        try:
            # Handle datetime fields
            datetime_fields = ['created_at', 'updated_at', 'completed_at', 'due_date']
            for field in datetime_fields:
                if data.get(field):
                    if isinstance(data[field], str):
                        data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))

            # Handle enum fields
            if 'status' in data:
                if isinstance(data['status'], str):
                    data['status'] = TaskStatus(data['status'])
            if 'priority' in data:
                if isinstance(data['priority'], str):
                    data['priority'] = TaskPriority(data['priority'])

            # Handle list fields
            for field in ['tags', 'depends_on', 'blocks']:
                if field in data and data[field] is None:
                    data[field] = []

            # Handle context field
            if 'context' not in data:
                data['context'] = {}

            return Task(**data)

        except Exception as e:
            raise ImportError(f"Task data parsing failed: {str(e)}")

    def _process_import(self, tasks: List[Task], conflict_resolution: str,
                       dry_run: bool, validate: bool, strict_validation: bool,
                       import_metadata: Optional[Dict[str, Any]], start_time: datetime) -> ImportResult:
        """Process task import with all options."""
        self.import_stats = {
            'processed': 0,
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'failed': 0,
            'errors': [],
            'warnings': []
        }

        # Add import metadata to tasks
        if import_metadata:
            for task in tasks:
                task.context.update({
                    'imported_at': datetime.now().isoformat(),
                    **import_metadata
                })

        # Process each task
        for task in tasks:
            self.import_stats['processed'] += 1

            try:
                result = self._process_single_task(
                    task, conflict_resolution, dry_run, validate, strict_validation
                )

                if result == 'imported':
                    self.import_stats['imported'] += 1
                elif result == 'updated':
                    self.import_stats['updated'] += 1
                elif result == 'skipped':
                    self.import_stats['skipped'] += 1
                else:
                    self.import_stats['failed'] += 1

            except Exception as e:
                self.import_stats['failed'] += 1
                self.import_stats['errors'].append(
                    f"Task {task.id}: {str(e)}"
                )

        processing_time = (datetime.now() - start_time).total_seconds()

        return ImportResult(
            success=len(self.import_stats['errors']) == 0,
            total_processed=self.import_stats['processed'],
            tasks_imported=self.import_stats['imported'],
            tasks_updated=self.import_stats['updated'],
            tasks_skipped=self.import_stats['skipped'],
            tasks_failed=self.import_stats['failed'],
            errors=self.import_stats['errors'],
            warnings=self.import_stats['warnings'],
            processing_time=processing_time,
            metadata={
                'conflict_resolution': conflict_resolution,
                'dry_run': dry_run,
                'validation': validate,
                'strict_validation': strict_validation,
                'file_path': import_metadata.get('file_path') if import_metadata else None
            }
        )

    def _process_single_task(self, task: Task, conflict_resolution: str,
                           dry_run: bool, validate: bool, strict_validation: bool) -> str:
        """Process a single task during import."""
        # Validate task if requested
        if validate:
            validation_result = self.validator.validate_task(task, strict=strict_validation)
            if not validation_result.is_valid:
                error_messages = [f"{error.field}: {error.message}" for error in validation_result.errors]
                raise ImportError(f"Validation failed: {'; '.join(error_messages)}")

            # Add warnings
            self.import_stats['warnings'].extend(validation_result.warnings)

        # Check for existing task
        existing_task = self.database.get_task(task.id)

        if existing_task is None:
            # New task - import it
            if not dry_run:
                self.database.create_task(task)
            return 'imported'

        # Handle conflict with existing task
        return self._handle_conflict(task, existing_task, conflict_resolution, dry_run, validate, strict_validation)

    def _handle_conflict(self, incoming_task: Task, existing_task: Task,
                        conflict_resolution: str, dry_run: bool, validate: bool, strict_validation: bool) -> str:
        """Handle conflict between incoming and existing task."""
        if conflict_resolution == ConflictResolution.SKIP:
            self.import_stats['warnings'].append(f"Skipped existing task {incoming_task.id}")
            return 'skipped'

        elif conflict_resolution == ConflictResolution.OVERWRITE:
            if not dry_run:
                self.database.update_task(incoming_task)
            return 'updated'

        elif conflict_resolution == ConflictResolution.MERGE:
            merged_task = self._merge_tasks(existing_task, incoming_task)
            if validate:
                validation_result = self.validator.validate_task(merged_task, strict=strict_validation)
                if not validation_result.is_valid:
                    raise ImportError(f"Merged task validation failed: {validation_result.errors}")

            if not dry_run:
                self.database.update_task(merged_task)
            return 'updated'

        elif conflict_resolution == ConflictResolution.CREATE_NEW:
            # Generate new ID and import as new task
            import uuid
            incoming_task.id = str(uuid.uuid4())[:8]
            incoming_task.context['original_id'] = incoming_task.context.get('original_id', incoming_task.id)

            if not dry_run:
                self.database.create_task(incoming_task)
            return 'imported'

        else:
            raise ImportError(f"Unknown conflict resolution: {conflict_resolution}")

    def _merge_tasks(self, existing_task: Task, incoming_task: Task) -> Task:
        """Merge two tasks, preferring newer data."""
        # Start with existing task as base
        merged_data = existing_task.to_dict()
        incoming_data = incoming_task.to_dict()

        # Use newer updated_at timestamp
        if incoming_task.updated_at > existing_task.updated_at:
            # Prefer incoming task data
            merged_data.update({
                'title': incoming_data['title'],
                'description': incoming_data['description'],
                'status': incoming_data['status'],
                'priority': incoming_data['priority'],
                'updated_at': incoming_data['updated_at'],
                'context': incoming_data['context']
            })

        # Merge fields intelligently
        merged_data['tags'] = list(set(existing_task.tags + incoming_task.tags))
        merged_data['depends_on'] = list(set(existing_task.depends_on + incoming_task.depends_on))
        merged_data['blocks'] = list(set(existing_task.blocks + incoming_task.blocks))

        # Preserve some existing fields if they're not None in incoming
        for field in ['assignee', 'due_date', 'estimated_hours', 'actual_hours']:
            if incoming_data[field] is not None:
                merged_data[field] = incoming_data[field]
            elif merged_data[field] is None:
                merged_data[field] = incoming_data[field]

        # Merge context
        merged_context = {**existing_task.context, **incoming_task.context}
        merged_context['merged_from'] = {
            'existing_updated': existing_task.updated_at.isoformat(),
            'incoming_updated': incoming_task.updated_at.isoformat(),
            'merge_timestamp': datetime.now().isoformat()
        }
        merged_data['context'] = merged_context

        return Task.from_dict(merged_data)

    def validate_import_file(self, input_path: str) -> Tuple[bool, List[str]]:
        """
        Validate import file without importing.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            tasks = self._read_jsonl_file(input_path)
            errors = []

            for task in tasks:
                validation_result = self.validator.validate_task(task, strict=True)
                if not validation_result.is_valid:
                    task_errors = [f"Task {task.id}: {error.field} - {error.message}"
                                 for error in validation_result.errors]
                    errors.extend(task_errors)

            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"File validation failed: {str(e)}"]

    def get_import_preview(self, input_path: str, max_tasks: int = 10) -> Dict[str, Any]:
        """
        Get preview of import data.

        Args:
            input_path: Path to JSONL file
            max_tasks: Maximum tasks to preview

        Returns:
            Preview information
        """
        try:
            tasks = self._read_jsonl_file(input_path)

            preview_tasks = tasks[:max_tasks]
            task_summaries = []

            for task in preview_tasks:
                task_summaries.append({
                    'id': task.id,
                    'title': task.title,
                    'status': task.status.value,
                    'priority': task.priority.value,
                    'created_at': task.created_at.isoformat(),
                    'assignee': task.assignee,
                    'tag_count': len(task.tags),
                    'dependency_count': len(task.depends_on)
                })

            return {
                'total_tasks': len(tasks),
                'preview_tasks': task_summaries,
                'status_distribution': self._get_status_distribution(tasks),
                'priority_distribution': self._get_priority_distribution(tasks),
                'assignee_distribution': self._get_assignee_distribution(tasks)
            }

        except Exception as e:
            return {'error': str(e)}

    def _get_status_distribution(self, tasks: List[Task]) -> Dict[str, int]:
        """Get distribution of task statuses."""
        distribution = {}
        for task in tasks:
            status = task.status.value
            distribution[status] = distribution.get(status, 0) + 1
        return distribution

    def _get_priority_distribution(self, tasks: List[Task]) -> Dict[str, int]:
        """Get distribution of task priorities."""
        distribution = {}
        for task in tasks:
            priority = task.priority.value
            distribution[priority] = distribution.get(priority, 0) + 1
        return distribution

    def _get_assignee_distribution(self, tasks: List[Task]) -> Dict[str, int]:
        """Get distribution of task assignees."""
        distribution = {}
        for task in tasks:
            assignee = task.assignee or 'unassigned'
            distribution[assignee] = distribution.get(assignee, 0) + 1
        return distribution