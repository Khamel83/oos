"""
Field validation system for OOS Task Memory System.

Provides comprehensive validation for task fields, business rules,
and data integrity constraints.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import fields

from .models import Task, TaskStatus, TaskPriority


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Validation error in field '{field}': {message}")


class ValidationResult:
    """Result of validation operation."""

    def __init__(self):
        self.is_valid = True
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []

    def add_error(self, field: str, message: str, value: Any = None):
        """Add validation error."""
        error = ValidationError(field, message, value)
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, message: str):
        """Add validation warning."""
        self.warnings.append(message)

    def get_error_summary(self) -> Dict[str, List[str]]:
        """Get errors grouped by field."""
        summary = {}
        for error in self.errors:
            if error.field not in summary:
                summary[error.field] = []
            summary[error.field].append(error.message)
        return summary


class TaskValidator:
    """
    Comprehensive task validation system.

    Validates individual fields, business rules, and cross-field constraints.
    """

    # Field constraints
    MIN_TITLE_LENGTH = 1
    MAX_TITLE_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 5000
    MAX_TAG_LENGTH = 50
    MAX_TAGS_COUNT = 20
    MAX_DEPENDENCIES = 50
    MAX_ASSIGNEE_LENGTH = 100

    # Business rules
    MAX_ESTIMATED_HOURS = 1000.0
    MAX_ACTUAL_HOURS = 2000.0
    MAX_FUTURE_DUE_DATE_YEARS = 10

    # Regex patterns
    TAG_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    ASSIGNEE_PATTERN = re.compile(r'^[a-zA-Z0-9._@-]+$')
    ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,50}$')

    def validate_task(self, task: Task, strict: bool = True) -> ValidationResult:
        """
        Validate a complete task object.

        Args:
            task: Task to validate
            strict: If True, apply strict validation rules

        Returns:
            ValidationResult with any errors/warnings found
        """
        result = ValidationResult()

        # Validate individual fields
        self._validate_title(task.title, result, strict)
        self._validate_description(task.description, result, strict)
        self._validate_id(task.id, result, strict)
        self._validate_status(task.status, result)
        self._validate_priority(task.priority, result)
        self._validate_tags(task.tags, result, strict)
        self._validate_dependencies(task.depends_on, result, strict)
        self._validate_assignee(task.assignee, result, strict)
        self._validate_hours(task.estimated_hours, task.actual_hours, result)
        self._validate_dates(task.created_at, task.updated_at, task.completed_at, task.due_date, result)
        self._validate_context(task.context, result, strict)

        # Validate business rules
        self._validate_business_rules(task, result, strict)

        return result

    def _validate_title(self, title: str, result: ValidationResult, strict: bool):
        """Validate task title."""
        if not title or not title.strip():
            result.add_error('title', 'Title cannot be empty')
            return

        title = title.strip()
        if len(title) < self.MIN_TITLE_LENGTH:
            result.add_error('title', f'Title must be at least {self.MIN_TITLE_LENGTH} character(s)')

        if len(title) > self.MAX_TITLE_LENGTH:
            result.add_error('title', f'Title cannot exceed {self.MAX_TITLE_LENGTH} characters')

        # Strict mode checks
        if strict:
            if title.startswith(' ') or title.endswith(' '):
                result.add_warning('Title has leading or trailing whitespace')

            if '  ' in title:
                result.add_warning('Title contains multiple consecutive spaces')

    def _validate_description(self, description: str, result: ValidationResult, strict: bool):
        """Validate task description."""
        if description and len(description) > self.MAX_DESCRIPTION_LENGTH:
            result.add_error('description', f'Description cannot exceed {self.MAX_DESCRIPTION_LENGTH} characters')

    def _validate_id(self, task_id: str, result: ValidationResult, strict: bool):
        """Validate task ID."""
        if not task_id:
            result.add_error('id', 'Task ID cannot be empty')
            return

        if not self.ID_PATTERN.match(task_id):
            result.add_error('id', 'Task ID can only contain letters, numbers, underscores, and hyphens')

        if len(task_id) > 50:
            result.add_error('id', 'Task ID cannot exceed 50 characters')

    def _validate_status(self, status: TaskStatus, result: ValidationResult):
        """Validate task status."""
        if not isinstance(status, TaskStatus):
            result.add_error('status', f'Invalid status type: {type(status)}')

    def _validate_priority(self, priority: TaskPriority, result: ValidationResult):
        """Validate task priority."""
        if not isinstance(priority, TaskPriority):
            result.add_error('priority', f'Invalid priority type: {type(priority)}')

    def _validate_tags(self, tags: List[str], result: ValidationResult, strict: bool):
        """Validate task tags."""
        if not isinstance(tags, list):
            result.add_error('tags', 'Tags must be a list')
            return

        if len(tags) > self.MAX_TAGS_COUNT:
            result.add_error('tags', f'Cannot have more than {self.MAX_TAGS_COUNT} tags')

        seen_tags = set()
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                result.add_error('tags', f'Tag at index {i} must be a string')
                continue

            tag = tag.strip()
            if not tag:
                result.add_error('tags', f'Tag at index {i} cannot be empty')
                continue

            if len(tag) > self.MAX_TAG_LENGTH:
                result.add_error('tags', f'Tag "{tag}" exceeds {self.MAX_TAG_LENGTH} characters')

            if strict and not self.TAG_PATTERN.match(tag):
                result.add_error('tags', f'Tag "{tag}" contains invalid characters (use only letters, numbers, _, -)')

            # Check for duplicates
            tag_lower = tag.lower()
            if tag_lower in seen_tags:
                result.add_warning(f'Duplicate tag: "{tag}"')
            seen_tags.add(tag_lower)

    def _validate_dependencies(self, dependencies: List[str], result: ValidationResult, strict: bool):
        """Validate task dependencies."""
        if not isinstance(dependencies, list):
            result.add_error('depends_on', 'Dependencies must be a list')
            return

        if len(dependencies) > self.MAX_DEPENDENCIES:
            result.add_error('depends_on', f'Cannot have more than {self.MAX_DEPENDENCIES} dependencies')

        seen_deps = set()
        for i, dep_id in enumerate(dependencies):
            if not isinstance(dep_id, str):
                result.add_error('depends_on', f'Dependency at index {i} must be a string')
                continue

            if not dep_id.strip():
                result.add_error('depends_on', f'Dependency at index {i} cannot be empty')
                continue

            if strict and not self.ID_PATTERN.match(dep_id):
                result.add_error('depends_on', f'Dependency ID "{dep_id}" contains invalid characters')

            # Check for duplicates
            if dep_id in seen_deps:
                result.add_warning(f'Duplicate dependency: "{dep_id}"')
            seen_deps.add(dep_id)

    def _validate_assignee(self, assignee: Optional[str], result: ValidationResult, strict: bool):
        """Validate task assignee."""
        if assignee is None:
            return

        if not isinstance(assignee, str):
            result.add_error('assignee', 'Assignee must be a string')
            return

        if len(assignee) > self.MAX_ASSIGNEE_LENGTH:
            result.add_error('assignee', f'Assignee cannot exceed {self.MAX_ASSIGNEE_LENGTH} characters')

        if strict and assignee and not self.ASSIGNEE_PATTERN.match(assignee):
            result.add_error('assignee', 'Assignee contains invalid characters')

    def _validate_hours(self, estimated: Optional[float], actual: Optional[float], result: ValidationResult):
        """Validate hour estimates."""
        if estimated is not None:
            if not isinstance(estimated, (int, float)):
                result.add_error('estimated_hours', 'Estimated hours must be a number')
            elif estimated < 0:
                result.add_error('estimated_hours', 'Estimated hours cannot be negative')
            elif estimated > self.MAX_ESTIMATED_HOURS:
                result.add_error('estimated_hours', f'Estimated hours cannot exceed {self.MAX_ESTIMATED_HOURS}')

        if actual is not None:
            if not isinstance(actual, (int, float)):
                result.add_error('actual_hours', 'Actual hours must be a number')
            elif actual < 0:
                result.add_error('actual_hours', 'Actual hours cannot be negative')
            elif actual > self.MAX_ACTUAL_HOURS:
                result.add_error('actual_hours', f'Actual hours cannot exceed {self.MAX_ACTUAL_HOURS}')

        # Cross-validation
        if estimated is not None and actual is not None and actual > estimated * 3:
            result.add_warning('Actual hours significantly exceed estimated hours (>3x)')

    def _validate_dates(self, created: datetime, updated: datetime,
                       completed: Optional[datetime], due: Optional[datetime], result: ValidationResult):
        """Validate date fields."""
        now = datetime.now()

        if not isinstance(created, datetime):
            result.add_error('created_at', 'Created date must be a datetime')
            return

        if not isinstance(updated, datetime):
            result.add_error('updated_at', 'Updated date must be a datetime')
            return

        # Created date should not be in the future
        if created > now + timedelta(minutes=5):  # Allow small clock skew
            result.add_warning('Created date is in the future')

        # Updated should be >= created
        if updated < created:
            result.add_error('updated_at', 'Updated date cannot be before created date')

        # Validate completed date
        if completed is not None:
            if not isinstance(completed, datetime):
                result.add_error('completed_at', 'Completed date must be a datetime')
            elif completed < created:
                result.add_error('completed_at', 'Completed date cannot be before created date')

        # Validate due date
        if due is not None:
            if not isinstance(due, datetime):
                result.add_error('due_date', 'Due date must be a datetime')
            elif due > now + timedelta(days=365 * self.MAX_FUTURE_DUE_DATE_YEARS):
                result.add_warning(f'Due date is more than {self.MAX_FUTURE_DUE_DATE_YEARS} years in the future')

    def _validate_context(self, context: Dict[str, Any], result: ValidationResult, strict: bool):
        """Validate context field."""
        if not isinstance(context, dict):
            result.add_error('context', 'Context must be a dictionary')
            return

        # Check context size (when serialized)
        try:
            import json
            context_json = json.dumps(context)
            if len(context_json) > 10000:  # 10KB limit
                result.add_warning('Context data is very large (>10KB)')
        except (TypeError, ValueError):
            result.add_error('context', 'Context contains non-serializable data')

    def _validate_business_rules(self, task: Task, result: ValidationResult, strict: bool):
        """Validate business logic rules."""
        # Completed tasks should have completion timestamp
        if task.status == TaskStatus.DONE and task.completed_at is None:
            result.add_warning('Completed task missing completion timestamp')

        # Non-completed tasks should not have completion timestamp
        if task.status != TaskStatus.DONE and task.completed_at is not None:
            result.add_warning('Non-completed task has completion timestamp')

        # Tasks with actual hours should be in progress or completed
        if task.actual_hours is not None and task.actual_hours > 0:
            if task.status in [TaskStatus.TODO, TaskStatus.BLOCKED]:
                result.add_warning('Task has actual hours but is not in progress')

        # Validate status transitions (if previous status available in context)
        if 'previous_status' in task.context:
            self._validate_status_transition(task.context['previous_status'], task.status, result)

    def _validate_status_transition(self, from_status: str, to_status: TaskStatus, result: ValidationResult):
        """Validate status transition rules."""
        valid_transitions = {
            'todo': [TaskStatus.DOING, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
            'doing': [TaskStatus.TODO, TaskStatus.TECHNICAL_COMPLETE, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
            'technical-complete': [TaskStatus.RUAT_VALIDATION, TaskStatus.DOING],
            'ruat-validation': [TaskStatus.REVIEW, TaskStatus.TECHNICAL_COMPLETE],
            'review': [TaskStatus.DONE, TaskStatus.RUAT_VALIDATION, TaskStatus.DOING],
            'blocked': [TaskStatus.TODO, TaskStatus.DOING],
            'done': [],  # Done is final
            'cancelled': []  # Cancelled is final
        }

        if from_status in valid_transitions:
            if to_status not in valid_transitions[from_status]:
                result.add_warning(f'Invalid status transition: {from_status} -> {to_status.value}')

    def validate_field(self, field_name: str, value: Any, strict: bool = True) -> ValidationResult:
        """
        Validate a single field value.

        Args:
            field_name: Name of the field to validate
            value: Value to validate
            strict: Apply strict validation rules

        Returns:
            ValidationResult for the field
        """
        result = ValidationResult()

        # Create minimal task to use existing validation methods
        if field_name == 'title':
            self._validate_title(value, result, strict)
        elif field_name == 'description':
            self._validate_description(value, result, strict)
        elif field_name == 'id':
            self._validate_id(value, result, strict)
        elif field_name == 'status':
            self._validate_status(value, result)
        elif field_name == 'priority':
            self._validate_priority(value, result)
        elif field_name == 'tags':
            self._validate_tags(value, result, strict)
        elif field_name == 'depends_on':
            self._validate_dependencies(value, result, strict)
        elif field_name == 'assignee':
            self._validate_assignee(value, result, strict)
        elif field_name == 'estimated_hours':
            self._validate_hours(value, None, result)
        elif field_name == 'actual_hours':
            self._validate_hours(None, value, result)
        elif field_name == 'context':
            self._validate_context(value, result, strict)
        else:
            result.add_warning(f'Unknown field: {field_name}')

        return result

    def get_field_constraints(self) -> Dict[str, Dict[str, Any]]:
        """Get all field validation constraints for documentation."""
        return {
            'title': {
                'required': True,
                'min_length': self.MIN_TITLE_LENGTH,
                'max_length': self.MAX_TITLE_LENGTH,
                'pattern': 'Any text (no special constraints)'
            },
            'description': {
                'required': False,
                'max_length': self.MAX_DESCRIPTION_LENGTH
            },
            'id': {
                'required': True,
                'max_length': 50,
                'pattern': self.ID_PATTERN.pattern
            },
            'tags': {
                'required': False,
                'max_count': self.MAX_TAGS_COUNT,
                'max_tag_length': self.MAX_TAG_LENGTH,
                'pattern': self.TAG_PATTERN.pattern
            },
            'depends_on': {
                'required': False,
                'max_count': self.MAX_DEPENDENCIES,
                'item_pattern': self.ID_PATTERN.pattern
            },
            'assignee': {
                'required': False,
                'max_length': self.MAX_ASSIGNEE_LENGTH,
                'pattern': self.ASSIGNEE_PATTERN.pattern
            },
            'estimated_hours': {
                'required': False,
                'min_value': 0,
                'max_value': self.MAX_ESTIMATED_HOURS
            },
            'actual_hours': {
                'required': False,
                'min_value': 0,
                'max_value': self.MAX_ACTUAL_HOURS
            }
        }