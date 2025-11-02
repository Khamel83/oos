"""
Task data model for OOS Task Memory System.

Provides the core Task dataclass with validation, status management,
and dependency tracking capabilities.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    """Task status enumeration."""
    TODO = "todo"
    DOING = "doing"
    TECHNICAL_COMPLETE = "technical-complete"
    RUAT_VALIDATION = "ruat-validation"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Task:
    """
    Core Task data model.

    Represents a single task with all metadata, dependencies,
    and status tracking information.
    """
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)
    assignee: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    due_date: datetime | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize task data after initialization."""
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)
        if isinstance(self.priority, str):
            self.priority = TaskPriority(self.priority)

        # Ensure tags is a list
        if isinstance(self.tags, str):
            self.tags = [tag.strip() for tag in self.tags.split(",") if tag.strip()]

        # Normalize datetime fields
        for field_name in ['created_at', 'updated_at', 'completed_at', 'due_date']:
            value = getattr(self, field_name)
            if isinstance(value, str) and value:
                setattr(self, field_name, datetime.fromisoformat(value.replace('Z', '+00:00')))

    def is_ready(self) -> bool:
        """Check if task is ready to be worked on (no pending dependencies)."""
        return (
            self.status == TaskStatus.TODO and
            len(self.depends_on) == 0  # No dependencies means ready
        )

    def is_blocked(self) -> bool:
        """Check if task is currently blocked."""
        return self.status == TaskStatus.BLOCKED

    def is_complete(self) -> bool:
        """Check if task is complete."""
        return self.status == TaskStatus.DONE

    def mark_complete(self) -> None:
        """Mark task as complete and set completion timestamp."""
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def mark_blocked(self) -> None:
        """Mark task as blocked."""
        self.status = TaskStatus.BLOCKED
        self.updated_at = datetime.now()

    def mark_in_progress(self) -> None:
        """Mark task as in progress."""
        self.status = TaskStatus.DOING
        self.updated_at = datetime.now()

    def update_status(self, new_status: TaskStatus) -> None:
        """Update task status with timestamp."""
        self.status = new_status
        self.updated_at = datetime.now()

        if new_status == TaskStatus.DONE and not self.completed_at:
            self.completed_at = datetime.now()

    def add_dependency(self, task_id: str) -> None:
        """Add a dependency to this task."""
        if task_id not in self.depends_on:
            self.depends_on.append(task_id)
            self.updated_at = datetime.now()

    def remove_dependency(self, task_id: str) -> None:
        """Remove a dependency from this task."""
        if task_id in self.depends_on:
            self.depends_on.remove(task_id)
            self.updated_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        """Add a tag to this task."""
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this task."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'tags': self.tags,
            'depends_on': self.depends_on,
            'blocks': self.blocks,
            'assignee': self.assignee,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'context': self.context
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        # Handle datetime fields
        for field_name in ['created_at', 'updated_at', 'completed_at', 'due_date']:
            if data.get(field_name):
                data[field_name] = datetime.fromisoformat(data[field_name].replace('Z', '+00:00'))

        # Convert enum strings back to enums
        if 'status' in data:
            data['status'] = TaskStatus(data['status'])
        if 'priority' in data:
            data['priority'] = TaskPriority(data['priority'])

        return cls(**data)

    def to_jsonl(self) -> str:
        """Convert task to JSONL format (single line JSON)."""
        return json.dumps(self.to_dict(), separators=(',', ':'))

    @classmethod
    def from_jsonl(cls, jsonl_line: str) -> 'Task':
        """Create task from JSONL line."""
        data = json.loads(jsonl_line.strip())
        return cls.from_dict(data)

    def __str__(self) -> str:
        """String representation of task."""
        return f"Task({self.id}): {self.title} [{self.status.value}]"

    def __repr__(self) -> str:
        """Detailed representation of task."""
        return (f"Task(id='{self.id}', title='{self.title}', "
                f"status={self.status.value}, priority={self.priority.value})")
