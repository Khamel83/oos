"""
Tests for OOS Task System models.

Comprehensive test suite for Task dataclass including validation,
status management, and serialization.
"""

import json
from datetime import datetime, timedelta

import pytest

from src.oos_task_system.models import Task, TaskPriority, TaskStatus


class TestTask:
    """Test suite for Task model."""

    def test_task_creation_minimal(self):
        """Test creating task with minimal parameters."""
        task = Task(title="Test Task")

        assert task.title == "Test Task"
        assert task.description == ""
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM
        assert len(task.id) == 8  # UUID first 8 chars
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
        assert task.completed_at is None
        assert task.tags == []
        assert task.depends_on == []
        assert task.blocks == []

    def test_task_creation_full(self):
        """Test creating task with all parameters."""
        now = datetime.now()
        due = now + timedelta(days=7)

        task = Task(
            title="Complex Task",
            description="A complex task with all fields",
            status=TaskStatus.DOING,
            priority=TaskPriority.HIGH,
            tags=["urgent", "backend"],
            assignee="alice",
            due_date=due,
            estimated_hours=8.5,
            context={"project": "web-app", "sprint": 2}
        )

        assert task.title == "Complex Task"
        assert task.description == "A complex task with all fields"
        assert task.status == TaskStatus.DOING
        assert task.priority == TaskPriority.HIGH
        assert task.tags == ["urgent", "backend"]
        assert task.assignee == "alice"
        assert task.due_date == due
        assert task.estimated_hours == 8.5
        assert task.context == {"project": "web-app", "sprint": 2}

    def test_task_string_enum_conversion(self):
        """Test that string enums are converted properly."""
        task = Task(title="Test", status="doing", priority="high")

        assert task.status == TaskStatus.DOING
        assert task.priority == TaskPriority.HIGH

    def test_task_tags_string_conversion(self):
        """Test that comma-separated tag strings are converted to lists."""
        task = Task(title="Test", tags="frontend, ui, react")

        assert task.tags == ["frontend", "ui", "react"]

    def test_task_is_ready(self):
        """Test ready status detection."""
        # Task with no dependencies is ready
        task = Task(title="Ready Task")
        assert task.is_ready() is True

        # Task with dependencies is not ready
        task.depends_on = ["other-task-id"]
        assert task.is_ready() is False

        # Task in progress is not ready
        task.depends_on = []
        task.status = TaskStatus.DOING
        assert task.is_ready() is False

    def test_task_status_methods(self):
        """Test status management methods."""
        task = Task(title="Test Task")

        # Test mark in progress
        task.mark_in_progress()
        assert task.status == TaskStatus.DOING

        # Test mark complete
        old_updated = task.updated_at
        task.mark_complete()
        assert task.status == TaskStatus.DONE
        assert task.completed_at is not None
        assert task.updated_at > old_updated

        # Test mark blocked
        task.mark_blocked()
        assert task.status == TaskStatus.BLOCKED

    def test_task_dependency_management(self):
        """Test dependency addition and removal."""
        task = Task(title="Test Task")

        # Add dependency
        task.add_dependency("dep1")
        assert "dep1" in task.depends_on

        # Add duplicate dependency (should not duplicate)
        task.add_dependency("dep1")
        assert task.depends_on.count("dep1") == 1

        # Add second dependency
        task.add_dependency("dep2")
        assert len(task.depends_on) == 2

        # Remove dependency
        task.remove_dependency("dep1")
        assert "dep1" not in task.depends_on
        assert "dep2" in task.depends_on

    def test_task_tag_management(self):
        """Test tag addition and removal."""
        task = Task(title="Test Task")

        # Add tag
        task.add_tag("urgent")
        assert "urgent" in task.tags

        # Add duplicate tag (should not duplicate)
        task.add_tag("urgent")
        assert task.tags.count("urgent") == 1

        # Add tag with whitespace
        task.add_tag("  backend  ")
        assert "backend" in task.tags
        assert "  backend  " not in task.tags

        # Remove tag
        task.remove_tag("urgent")
        assert "urgent" not in task.tags

    def test_task_serialization(self):
        """Test task to_dict and from_dict."""
        original = Task(
            title="Serialize Test",
            description="Test serialization",
            status=TaskStatus.DOING,
            priority=TaskPriority.HIGH,
            tags=["test", "serialization"],
            assignee="bob",
            estimated_hours=4.0
        )

        # Serialize to dict
        data = original.to_dict()

        assert data['title'] == "Serialize Test"
        assert data['status'] == "doing"
        assert data['priority'] == "high"
        assert data['tags'] == ["test", "serialization"]
        assert data['assignee'] == "bob"
        assert data['estimated_hours'] == 4.0

        # Deserialize from dict
        restored = Task.from_dict(data)

        assert restored.title == original.title
        assert restored.status == original.status
        assert restored.priority == original.priority
        assert restored.tags == original.tags
        assert restored.assignee == original.assignee
        assert restored.estimated_hours == original.estimated_hours

    def test_task_jsonl_format(self):
        """Test JSONL serialization and deserialization."""
        task = Task(
            title="JSONL Test",
            description="Test JSONL format",
            tags=["jsonl", "test"]
        )

        # Serialize to JSONL
        jsonl_line = task.to_jsonl()

        # Should be valid JSON on single line
        assert '\n' not in jsonl_line
        data = json.loads(jsonl_line)
        assert data['title'] == "JSONL Test"

        # Deserialize from JSONL
        restored = Task.from_jsonl(jsonl_line)

        assert restored.title == task.title
        assert restored.description == task.description
        assert restored.tags == task.tags

    def test_task_datetime_handling(self):
        """Test datetime field handling in serialization."""
        task = Task(title="DateTime Test")
        task.mark_complete()

        # Serialize and deserialize
        data = task.to_dict()
        restored = Task.from_dict(data)

        # Compare datetime fields (allowing small difference due to serialization)
        assert abs((restored.created_at - task.created_at).total_seconds()) < 1
        assert abs((restored.updated_at - task.updated_at).total_seconds()) < 1
        assert abs((restored.completed_at - task.completed_at).total_seconds()) < 1

    def test_task_update_status(self):
        """Test update_status method."""
        task = Task(title="Status Test")
        old_updated = task.updated_at

        # Update to DOING
        task.update_status(TaskStatus.DOING)
        assert task.status == TaskStatus.DOING
        assert task.updated_at > old_updated
        assert task.completed_at is None

        # Update to DONE (should set completed_at)
        task.update_status(TaskStatus.DONE)
        assert task.status == TaskStatus.DONE
        assert task.completed_at is not None

    def test_task_string_representations(self):
        """Test string representation methods."""
        task = Task(title="String Test", status=TaskStatus.DOING)

        str_repr = str(task)
        assert "String Test" in str_repr
        assert "doing" in str_repr
        assert task.id in str_repr

        repr_repr = repr(task)
        assert "Task(" in repr_repr
        assert "String Test" in repr_repr
        assert "doing" in repr_repr

    def test_task_validation_edge_cases(self):
        """Test edge cases and validation."""
        # Empty title should be allowed (validation handled by database layer)
        task = Task(title="")
        assert task.title == ""

        # Invalid status should raise ValueError
        with pytest.raises(ValueError):
            Task(title="Test", status="invalid-status")

        # Invalid priority should raise ValueError
        with pytest.raises(ValueError):
            Task(title="Test", priority="invalid-priority")

    def test_task_context_handling(self):
        """Test context field handling."""
        context = {
            "project": "my-project",
            "sprint": 3,
            "components": ["api", "ui"],
            "meta": {"created_by": "script"}
        }

        task = Task(title="Context Test", context=context)

        # Should preserve complex context structure
        assert task.context == context

        # Should serialize and deserialize correctly
        data = task.to_dict()
        restored = Task.from_dict(data)
        assert restored.context == context
