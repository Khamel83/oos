"""
Tests for OOS Task System database operations.

Comprehensive test suite for TaskDatabase including CRUD operations,
dependency tracking, and query functionality.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from src.oos_task_system.database import TaskDatabase
from src.oos_task_system.models import Task, TaskPriority, TaskStatus


class TestTaskDatabase:
    """Test suite for TaskDatabase."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_tasks.db"

        # Create database
        database = TaskDatabase(str(db_path))

        yield database

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_database_initialization(self, temp_db):
        """Test database initialization and schema creation."""
        # Database should be created and accessible
        assert temp_db.db_path.exists()

        # Should be able to get stats from empty database
        stats = temp_db.get_stats()
        assert stats['total_tasks'] == 0
        assert stats['db_size_bytes'] > 0  # Schema exists

    def test_create_task(self, temp_db):
        """Test task creation."""
        task = Task(
            title="Test Task",
            description="A test task",
            priority=TaskPriority.HIGH,
            tags=["test", "important"]
        )

        # Create task
        created = temp_db.create_task(task)

        assert created.id == task.id
        assert created.title == task.title
        assert created.description == task.description
        assert created.priority == TaskPriority.HIGH
        assert created.tags == ["test", "important"]

        # Verify in database
        retrieved = temp_db.get_task(task.id)
        assert retrieved is not None
        assert retrieved.title == task.title

    def test_get_task(self, temp_db):
        """Test task retrieval."""
        # Create task
        task = Task(title="Get Test", assignee="alice")
        temp_db.create_task(task)

        # Retrieve task
        retrieved = temp_db.get_task(task.id)

        assert retrieved is not None
        assert retrieved.id == task.id
        assert retrieved.title == "Get Test"
        assert retrieved.assignee == "alice"

        # Non-existent task should return None
        assert temp_db.get_task("nonexistent") is None

    def test_update_task(self, temp_db):
        """Test task updates."""
        # Create task
        task = Task(title="Original Title", status=TaskStatus.TODO)
        temp_db.create_task(task)

        # Update task
        task.title = "Updated Title"
        task.status = TaskStatus.DOING
        task.description = "Added description"

        updated = temp_db.update_task(task)

        assert updated.title == "Updated Title"
        assert updated.status == TaskStatus.DOING
        assert updated.description == "Added description"

        # Verify update in database
        retrieved = temp_db.get_task(task.id)
        assert retrieved.title == "Updated Title"
        assert retrieved.status == TaskStatus.DOING

    def test_delete_task(self, temp_db):
        """Test task deletion."""
        # Create task
        task = Task(title="Delete Me")
        temp_db.create_task(task)

        # Verify exists
        assert temp_db.get_task(task.id) is not None

        # Delete task
        deleted = temp_db.delete_task(task.id)
        assert deleted is True

        # Verify deleted
        assert temp_db.get_task(task.id) is None

        # Deleting non-existent task should return False
        assert temp_db.delete_task("nonexistent") is False

    def test_list_tasks(self, temp_db):
        """Test task listing with filters."""
        # Create tasks with different properties
        tasks = [
            Task(title="Task 1", status=TaskStatus.TODO, assignee="alice"),
            Task(title="Task 2", status=TaskStatus.DOING, assignee="bob"),
            Task(title="Task 3", status=TaskStatus.DONE, assignee="alice"),
            Task(title="Task 4", status=TaskStatus.TODO, assignee="charlie")
        ]

        for task in tasks:
            temp_db.create_task(task)

        # List all tasks
        all_tasks = temp_db.list_tasks()
        assert len(all_tasks) == 4

        # Filter by status
        todo_tasks = temp_db.list_tasks(status=TaskStatus.TODO)
        assert len(todo_tasks) == 2
        assert all(t.status == TaskStatus.TODO for t in todo_tasks)

        # Filter by assignee
        alice_tasks = temp_db.list_tasks(assignee="alice")
        assert len(alice_tasks) == 2
        assert all(t.assignee == "alice" for t in alice_tasks)

        # Filter by status and assignee
        alice_todo = temp_db.list_tasks(status=TaskStatus.TODO, assignee="alice")
        assert len(alice_todo) == 1
        assert alice_todo[0].title == "Task 1"

    def test_list_tasks_with_tags(self, temp_db):
        """Test task listing with tag filtering."""
        # Create tasks with different tags
        tasks = [
            Task(title="Task 1", tags=["frontend", "urgent"]),
            Task(title="Task 2", tags=["backend", "bug"]),
            Task(title="Task 3", tags=["frontend", "feature"]),
            Task(title="Task 4", tags=["docs"])
        ]

        for task in tasks:
            temp_db.create_task(task)

        # Filter by tags
        frontend_tasks = temp_db.list_tasks(tags=["frontend"])
        assert len(frontend_tasks) == 2

        urgent_tasks = temp_db.list_tasks(tags=["urgent"])
        assert len(urgent_tasks) == 1

        # Multiple tags (OR logic)
        multiple_tag_tasks = temp_db.list_tasks(tags=["urgent", "bug"])
        assert len(multiple_tag_tasks) == 2

    def test_dependencies(self, temp_db):
        """Test dependency management."""
        # Create tasks
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")
        task3 = Task(title="Task 3")

        temp_db.create_task(task1)
        temp_db.create_task(task2)
        temp_db.create_task(task3)

        # Add dependencies: task3 depends on task1 and task2
        task3.depends_on = [task1.id, task2.id]
        temp_db.update_task(task3)

        # Verify dependencies
        retrieved = temp_db.get_task(task3.id)
        assert task1.id in retrieved.depends_on
        assert task2.id in retrieved.depends_on

        # Verify blocks relationships
        task1_retrieved = temp_db.get_task(task1.id)
        assert task3.id in task1_retrieved.blocks

    def test_add_remove_dependencies(self, temp_db):
        """Test adding and removing dependencies directly."""
        # Create tasks
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")

        temp_db.create_task(task1)
        temp_db.create_task(task2)

        # Add dependency
        success = temp_db.add_dependency(task2.id, task1.id)
        assert success is True

        # Verify dependency exists
        retrieved = temp_db.get_task(task2.id)
        assert task1.id in retrieved.depends_on

        # Adding duplicate dependency should return False
        success = temp_db.add_dependency(task2.id, task1.id)
        assert success is False

        # Remove dependency
        success = temp_db.remove_dependency(task2.id, task1.id)
        assert success is True

        # Verify dependency removed
        retrieved = temp_db.get_task(task2.id)
        assert task1.id not in retrieved.depends_on

    def test_get_ready_tasks(self, temp_db):
        """Test getting tasks ready to work on."""
        # Create tasks with dependencies
        task1 = Task(title="Independent Task", status=TaskStatus.TODO)
        task2 = Task(title="Blocked Task", status=TaskStatus.TODO)
        task3 = Task(title="Dependency Task", status=TaskStatus.DONE)
        task4 = Task(title="Unblocked Task", status=TaskStatus.TODO)

        temp_db.create_task(task1)
        temp_db.create_task(task2)
        temp_db.create_task(task3)
        temp_db.create_task(task4)

        # Set up dependencies
        task2.depends_on = [task1.id]  # task2 blocked by task1 (not done)
        task4.depends_on = [task3.id]  # task4 depends on task3 (done)

        temp_db.update_task(task2)
        temp_db.update_task(task4)

        # Get ready tasks
        ready_tasks = temp_db.get_ready_tasks()

        # Should include task1 (independent) and task4 (dependency satisfied)
        ready_ids = [t.id for t in ready_tasks]
        assert task1.id in ready_ids
        assert task4.id in ready_ids
        assert task2.id not in ready_ids  # blocked by task1

    def test_get_blocked_tasks(self, temp_db):
        """Test getting blocked tasks."""
        # Create tasks
        task1 = Task(title="Blocking Task", status=TaskStatus.TODO)
        task2 = Task(title="Blocked Task", status=TaskStatus.TODO)
        task3 = Task(title="Independent Task", status=TaskStatus.TODO)

        temp_db.create_task(task1)
        temp_db.create_task(task2)
        temp_db.create_task(task3)

        # Set up blocking relationship
        task2.depends_on = [task1.id]
        temp_db.update_task(task2)

        # Get blocked tasks
        blocked_tasks = temp_db.get_blocked_tasks()

        # Should only include task2
        blocked_ids = [t.id for t in blocked_tasks]
        assert task2.id in blocked_ids
        assert task1.id not in blocked_ids
        assert task3.id not in blocked_ids

    def test_priority_ordering(self, temp_db):
        """Test that ready tasks are ordered by priority."""
        # Create tasks with different priorities
        low_task = Task(title="Low Priority", priority=TaskPriority.LOW)
        high_task = Task(title="High Priority", priority=TaskPriority.HIGH)
        urgent_task = Task(title="Urgent Priority", priority=TaskPriority.URGENT)

        temp_db.create_task(low_task)
        temp_db.create_task(high_task)
        temp_db.create_task(urgent_task)

        # Get ready tasks (should be ordered by priority DESC)
        ready_tasks = temp_db.get_ready_tasks()

        assert len(ready_tasks) == 3
        assert ready_tasks[0].priority == TaskPriority.URGENT
        assert ready_tasks[1].priority == TaskPriority.HIGH
        assert ready_tasks[2].priority == TaskPriority.LOW

    def test_database_stats(self, temp_db):
        """Test database statistics."""
        # Create tasks with different statuses
        tasks = [
            Task(title="TODO 1", status=TaskStatus.TODO),
            Task(title="TODO 2", status=TaskStatus.TODO),
            Task(title="DOING 1", status=TaskStatus.DOING),
            Task(title="DONE 1", status=TaskStatus.DONE)
        ]

        for task in tasks:
            temp_db.create_task(task)

        # Get stats
        stats = temp_db.get_stats()

        assert stats['total_tasks'] == 4
        assert stats['status_counts']['todo'] == 2
        assert stats['status_counts']['doing'] == 1
        assert stats['status_counts']['done'] == 1
        assert stats['status_counts']['blocked'] == 0
        assert 'db_path' in stats
        assert stats['db_size_bytes'] > 0

    def test_complex_dependency_chain(self, temp_db):
        """Test complex dependency chains."""
        # Create chain: task1 -> task2 -> task3 -> task4
        task1 = Task(title="Task 1", status=TaskStatus.DONE)
        task2 = Task(title="Task 2", status=TaskStatus.DONE)
        task3 = Task(title="Task 3", status=TaskStatus.TODO)
        task4 = Task(title="Task 4", status=TaskStatus.TODO)

        temp_db.create_task(task1)
        temp_db.create_task(task2)
        temp_db.create_task(task3)
        temp_db.create_task(task4)

        # Set up dependency chain
        task2.depends_on = [task1.id]
        task3.depends_on = [task2.id]
        task4.depends_on = [task3.id]

        temp_db.update_task(task2)
        temp_db.update_task(task3)
        temp_db.update_task(task4)

        # Only task3 should be ready (task1 and task2 are done)
        ready_tasks = temp_db.get_ready_tasks()
        ready_ids = [t.id for t in ready_tasks]

        assert task3.id in ready_ids
        assert task4.id not in ready_ids  # blocked by task3

        # task4 should be blocked
        blocked_tasks = temp_db.get_blocked_tasks()
        blocked_ids = [t.id for t in blocked_tasks]
        assert task4.id in blocked_ids

    def test_task_context_persistence(self, temp_db):
        """Test that complex context data persists correctly."""
        context = {
            "project": "test-project",
            "sprint": 3,
            "story_points": 8,
            "components": ["api", "database", "ui"],
            "metadata": {
                "created_by": "script",
                "automated": True,
                "source": "jira"
            }
        }

        task = Task(title="Context Test", context=context)
        temp_db.create_task(task)

        # Retrieve and verify context
        retrieved = temp_db.get_task(task.id)
        assert retrieved.context == context
        assert retrieved.context["metadata"]["automated"] is True
        assert retrieved.context["components"] == ["api", "database", "ui"]
