"""
Tests for OOS Task System CLI interface.

Comprehensive test suite for all CLI commands including
task CRUD operations, dependency management, and export/import.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner
from datetime import datetime, timedelta

from src.oos_task_system.cli import cli
from src.oos_task_system.models import Task, TaskStatus, TaskPriority
from src.oos_task_system.database import TaskDatabase


class TestTaskCLI:
    """Test suite for CLI commands."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_tasks.db"
        yield str(db_path)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'OOS Task Memory System' in result.output
        assert 'create' in result.output
        assert 'list' in result.output

    def test_create_task_basic(self, runner, temp_db):
        """Test basic task creation."""
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'create',
            'Test Task Title'
        ])

        assert result.exit_code == 0
        assert 'Created task' in result.output
        assert 'Test Task Title' in result.output

    def test_create_task_with_options(self, runner, temp_db):
        """Test task creation with all options."""
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'create',
            'Complex Task',
            '--description', 'Task description',
            '--status', 'doing',
            '--priority', 'high',
            '--assignee', 'alice',
            '--tags', 'urgent,backend',
            '--depends-on', 'task1,task2',
            '--context', 'project=web-app,sprint=3',
            '--estimated-hours', 4.5
        ])

        assert result.exit_code == 0
        assert 'Created task' in result.output

    def test_create_task_json_output(self, runner, temp_db):
        """Test task creation with JSON output."""
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'create',
            'JSON Task',
            '--json'
        ])

        assert result.exit_code == 0

        # Parse JSON output
        task_data = json.loads(result.output)
        assert task_data['title'] == 'JSON Task'
        assert 'id' in task_data
        assert 'created_at' in task_data

    def test_create_task_invalid_due_date(self, runner, temp_db):
        """Test task creation with invalid due date."""
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'create',
            'Task',
            '--due-date', 'invalid-date'
        ])

        assert result.exit_code == 1
        assert 'Invalid due date format' in result.output

    def test_list_empty_tasks(self, runner, temp_db):
        """Test listing tasks when database is empty."""
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'list'
        ])

        assert result.exit_code == 0
        assert 'No tasks found' in result.output

    def test_list_tasks_with_filters(self, runner, temp_db):
        """Test listing tasks with various filters."""
        # Create some test tasks
        db = TaskDatabase(temp_db)
        tasks = [
            Task(title="Task 1", status=TaskStatus.TODO, assignee="alice", priority=TaskPriority.HIGH),
            Task(title="Task 2", status=TaskStatus.DOING, assignee="bob", priority=TaskPriority.MEDIUM),
            Task(title="Task 3", status=TaskStatus.TODO, assignee="alice", priority=TaskPriority.LOW, tags=["urgent"])
        ]
        for task in tasks:
            db.create_task(task)

        # Test status filter
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'list',
            '--status', 'todo'
        ])
        assert result.exit_code == 0
        assert 'Task 1' in result.output
        assert 'Task 3' in result.output
        assert 'Task 2' not in result.output

        # Test assignee filter
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'list',
            '--assignee', 'alice'
        ])
        assert result.exit_code == 0
        assert 'Task 1' in result.output
        assert 'Task 3' in result.output
        assert 'Task 2' not in result.output

        # Test tag filter
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'list',
            '--tags', 'urgent'
        ])
        assert result.exit_code == 0
        assert 'Task 3' in result.output
        assert 'Task 1' not in result.output

    def test_list_tasks_json_output(self, runner, temp_db):
        """Test listing tasks with JSON output."""
        # Create test task
        db = TaskDatabase(temp_db)
        task = Task(title="Test Task")
        db.create_task(task)

        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'list',
            '--json'
        ])

        assert result.exit_code == 0
        tasks_data = json.loads(result.output)
        assert len(tasks_data) == 1
        assert tasks_data[0]['title'] == 'Test Task'

    def test_list_tasks_count_only(self, runner, temp_db):
        """Test listing tasks with count only."""
        # Create test tasks
        db = TaskDatabase(temp_db)
        for i in range(3):
            db.create_task(Task(title=f"Task {i}"))

        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'list',
            '--count'
        ])

        assert result.exit_code == 0
        assert 'Total tasks: 3' in result.output

    def test_show_task(self, runner, temp_db):
        """Test showing task details."""
        # Create test task
        db = TaskDatabase(temp_db)
        task = Task(
            title="Show Task",
            description="Task description",
            tags=["test"],
            context={"project": "test"}
        )
        created_task = db.create_task(task)

        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'show',
            created_task.id
        ])

        assert result.exit_code == 0
        assert 'Show Task' in result.output
        assert 'Task description' in result.output
        assert 'test' in result.output

    def test_show_nonexistent_task(self, runner, temp_db):
        """Test showing non-existent task."""
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'show',
            'nonexistent'
        ])

        assert result.exit_code == 1
        assert 'not found' in result.output

    def test_update_task(self, runner, temp_db):
        """Test updating a task."""
        # Create test task
        db = TaskDatabase(temp_db)
        task = Task(title="Original Title")
        created_task = db.create_task(task)

        # Update task
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'update',
            created_task.id,
            '--title', 'Updated Title',
            '--status', 'doing',
            '--priority', 'high',
            '--add-tags', 'urgent,backend'
        ])

        assert result.exit_code == 0
        assert 'Updated task' in result.output
        assert 'Updated Title' in result.output

        # Verify update
        updated_task = db.get_task(created_task.id)
        assert updated_task.title == 'Updated Title'
        assert updated_task.status == TaskStatus.DOING
        assert updated_task.priority == TaskPriority.HIGH
        assert 'urgent' in updated_task.tags

    def test_complete_task(self, runner, temp_db):
        """Test completing a task."""
        # Create test task
        db = TaskDatabase(temp_db)
        task = Task(title="To Complete")
        created_task = db.create_task(task)

        # Complete task
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'complete',
            created_task.id
        ])

        assert result.exit_code == 0
        assert 'Completed task' in result.output

        # Verify completion
        completed_task = db.get_task(created_task.id)
        assert completed_task.status == TaskStatus.DONE
        assert completed_task.completed_at is not None

    def test_delete_task(self, runner, temp_db):
        """Test deleting a task."""
        # Create test task
        db = TaskDatabase(temp_db)
        task = Task(title="To Delete")
        created_task = db.create_task(task)

        # Delete task with confirmation
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'delete',
            created_task.id,
            '--confirm'
        ])

        assert result.exit_code == 0
        assert 'Deleted task' in result.output

        # Verify deletion
        deleted_task = db.get_task(created_task.id)
        assert deleted_task is None

    def test_delete_task_with_dependencies(self, runner, temp_db):
        """Test deleting task that other tasks depend on."""
        # Create test tasks with dependency
        db = TaskDatabase(temp_db)
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2", depends_on=[task1.id])
        created_task1 = db.create_task(task1)
        created_task2 = db.create_task(task2)

        # Try to delete task1
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'delete',
            created_task1.id,
            '--confirm'
        ])

        assert result.exit_code == 0
        assert 'Warning:' in result.output
        assert '1 task(s) depend on this task' in result.output

    def test_ready_tasks(self, runner, temp_db):
        """Test showing ready tasks."""
        # Create test tasks
        db = TaskDatabase(temp_db)
        ready_task = Task(title="Ready Task")
        blocked_task = Task(title="Blocked Task", depends_on=["nonexistent"])

        db.create_task(ready_task)
        db.create_task(blocked_task)

        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'ready'
        ])

        assert result.exit_code == 0
        assert 'Ready Task' in result.output
        assert 'Blocked Task' not in result.output
        assert '1 task(s) ready to work on' in result.output

    def test_blocked_tasks(self, runner, temp_db):
        """Test showing blocked tasks."""
        # Create test tasks
        db = TaskDatabase(temp_db)
        blocker = Task(title="Blocker", status=TaskStatus.DONE)
        blocked = Task(title="Blocked", depends_on=[blocker.id])

        db.create_task(blocker)
        db.create_task(blocked)

        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'blocked'
        ])

        assert result.exit_code == 0
        # Blocked task should not be shown because blocker is done
        assert '0 blocked tasks' in result.output

    def test_export_tasks(self, runner, temp_db):
        """Test exporting tasks to JSONL."""
        # Create test tasks
        db = TaskDatabase(temp_db)
        tasks = [
            Task(title="Export Task 1", status=TaskStatus.TODO),
            Task(title="Export Task 2", status=TaskStatus.DOING)
        ]
        for task in tasks:
            db.create_task(task)

        # Export tasks
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            export_file = f.name

        try:
            result = runner.invoke(cli, [
                '--db-path', temp_db,
                'export',
                '--output', export_file
            ])

            assert result.exit_code == 0
            assert 'Exported 2 tasks' in result.output

            # Verify file exists and has content
            export_path = Path(export_file)
            assert export_path.exists()
            assert export_path.stat().st_size > 0

        finally:
            Path(export_file).unlink()

    def test_export_filtered_tasks(self, runner, temp_db):
        """Test exporting tasks with filters."""
        # Create test tasks
        db = TaskDatabase(temp_db)
        todo_task = Task(title="TODO Task", status=TaskStatus.TODO)
        doing_task = Task(title="DOING Task", status=TaskStatus.DOING)

        db.create_task(todo_task)
        db.create_task(doing_task)

        # Export only TODO tasks
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            export_file = f.name

        try:
            result = runner.invoke(cli, [
                '--db-path', temp_db,
                'export',
                '--output', export_file,
                '--status', 'todo'
            ])

            assert result.exit_code == 0
            assert 'Exported 1 tasks' in result.output

        finally:
            Path(export_file).unlink()

    def test_import_tasks(self, runner, temp_db):
        """Test importing tasks from JSONL."""
        # Create import file
        import_tasks = [
            {
                "id": "import1",
                "title": "Import Task 1",
                "status": "todo",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": "import2",
                "title": "Import Task 2",
                "status": "doing",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for task in import_tasks:
                f.write(json.dumps(task) + '\n')
            import_file = f.name

        try:
            result = runner.invoke(cli, [
                '--db-path', temp_db,
                'import-tasks',
                import_file
            ])

            assert result.exit_code == 0
            assert 'Import completed successfully' in result.output
            assert 'Tasks imported: 2' in result.output

            # Verify tasks were imported
            db = TaskDatabase(temp_db)
            imported_tasks = db.list_tasks()
            assert len(imported_tasks) == 2

        finally:
            Path(import_file).unlink()

    def test_import_tasks_dry_run(self, runner, temp_db):
        """Test importing tasks with dry run."""
        # Create import file
        import_data = {
            "id": "dryrun1",
            "title": "Dry Run Task",
            "status": "todo",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write(json.dumps(import_data) + '\n')
            import_file = f.name

        try:
            result = runner.invoke(cli, [
                '--db-path', temp_db,
                'import-tasks',
                import_file,
                '--dry-run'
            ])

            assert result.exit_code == 0
            assert 'Preview: 1 tasks in file' in result.output

            # Verify no tasks were actually imported
            db = TaskDatabase(temp_db)
            tasks = db.list_tasks()
            assert len(tasks) == 0

        finally:
            Path(import_file).unlink()

    def test_stats_command(self, runner, temp_db):
        """Test database statistics command."""
        # Create test tasks
        db = TaskDatabase(temp_db)
        tasks = [
            Task(title="Task 1", status=TaskStatus.TODO),
            Task(title="Task 2", status=TaskStatus.DONE),
            Task(title="Task 3", status=TaskStatus.DOING)
        ]
        for task in tasks:
            db.create_task(task)

        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'stats'
        ])

        assert result.exit_code == 0
        assert 'Task Database Statistics' in result.output
        assert 'Total tasks: 3' in result.output
        assert 'todo: 1' in result.output
        assert 'done: 1' in result.output
        assert 'doing: 1' in result.output

    def test_validate_specific_task(self, runner, temp_db):
        """Test validating a specific task."""
        # Create valid task
        db = TaskDatabase(temp_db)
        task = Task(title="Valid Task")
        created_task = db.create_task(task)

        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'validate',
            created_task.id
        ])

        assert result.exit_code == 0
        assert 'is valid' in result.output

    def test_validate_all_tasks(self, runner, temp_db):
        """Test validating all tasks."""
        # Create test tasks
        db = TaskDatabase(temp_db)
        tasks = [
            Task(title="Valid Task 1"),
            Task(title="Valid Task 2")
        ]
        for task in tasks:
            db.create_task(task)

        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'validate',
            '--all-tasks'
        ])

        assert result.exit_code == 0
        assert 'All 2 tasks are valid' in result.output

    def test_command_error_handling(self, runner, temp_db):
        """Test CLI error handling."""
        # Test invalid database path
        result = runner.invoke(cli, [
            '--db-path', '/invalid/path/tasks.db',
            'list'
        ])

        assert result.exit_code != 0

        # Test invalid command arguments
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'create'
        ])

        assert result.exit_code != 0
        assert 'Missing argument' in result.output

    def test_json_output_consistency(self, runner, temp_db):
        """Test JSON output consistency across commands."""
        # Create test task
        db = TaskDatabase(temp_db)
        task = Task(title="JSON Test")
        created_task = db.create_task(task)

        # Test show command JSON output
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'show',
            created_task.id,
            '--json'
        ])

        assert result.exit_code == 0
        show_data = json.loads(result.output)
        assert show_data['title'] == 'JSON Test'
        assert 'id' in show_data

        # Test list command JSON output
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'list',
            '--json'
        ])

        assert result.exit_code == 0
        list_data = json.loads(result.output)
        assert len(list_data) == 1
        assert list_data[0]['title'] == 'JSON Test'

    def test_task_dependency_management_cli(self, runner, temp_db):
        """Test dependency management through CLI."""
        # Create tasks
        db = TaskDatabase(temp_db)
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")
        created_task1 = db.create_task(task1)
        created_task2 = db.create_task(task2)

        # Add dependency
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'update',
            created_task2.id,
            '--add-dependencies', created_task1.id
        ])

        assert result.exit_code == 0

        # Check ready tasks (task2 should not be ready)
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'ready'
        ])

        assert result.exit_code == 0
        assert 'Task 1' in result.output
        assert 'Task 2' not in result.output

        # Complete task1
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'complete',
            created_task1.id
        ])

        assert result.exit_code == 0

        # Check ready tasks again (task2 should now be ready)
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'ready'
        ])

        assert result.exit_code == 0
        assert 'Task 2' in result.output

    def test_context_parsing(self, runner, temp_db):
        """Test context parsing in CLI."""
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'create',
            'Context Test',
            '--context', 'project=web-app,sprint=3,complex={"key":"value"}'
        ])

        assert result.exit_code == 0

        # Verify context was parsed correctly
        db = TaskDatabase(temp_db)
        tasks = db.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].context['project'] == 'web-app'
        assert tasks[0].context['sprint'] == 3
        assert tasks[0].context['complex']['key'] == 'value'

    def test_tags_and_dependencies_parsing(self, runner, temp_db):
        """Test tags and dependencies parsing."""
        # Create first task
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'create',
            'First Task',
            '--tags', 'tag1,tag2, tag3 '
        ])

        assert result.exit_code == 0

        # Get first task ID
        db = TaskDatabase(temp_db)
        first_task = db.list_tasks()[0]

        # Create second task with dependency
        result = runner.invoke(cli, [
            '--db-path', temp_db,
            'create',
            'Second Task',
            '--tags', 'urgent,backend',
            '--depends-on', first_task.id
        ])

        assert result.exit_code == 0

        # Verify parsing
        second_task = db.list_tasks()[1]
        assert 'tag1' in first_task.tags
        assert 'tag2' in first_task.tags
        assert 'tag3' in first_task.tags
        assert 'urgent' in second_task.tags
        assert 'backend' in second_task.tags
        assert first_task.id in second_task.depends_on