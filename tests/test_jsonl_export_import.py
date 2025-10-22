"""
Tests for OOS Task System JSONL export/import functionality.

Comprehensive test suite for export, import, validation, and
conflict resolution features.
"""

import pytest
import json
import gzip
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from src.oos_task_system.models import Task, TaskStatus, TaskPriority
from src.oos_task_system.database import TaskDatabase
from src.oos_task_system.jsonl_export import TaskExporter, ExportError
from src.oos_task_system.jsonl_import import TaskImporter, ImportResult, ConflictResolution


class TestTaskExporter:
    """Test suite for TaskExporter."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database with test tasks."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_tasks.db"
        database = TaskDatabase(str(db_path))

        # Create test tasks
        tasks = [
            Task(id="task1", title="Task 1", status=TaskStatus.DONE, assignee="alice"),
            Task(id="task2", title="Task 2", status=TaskStatus.TODO, assignee="bob",
                 tags=["frontend", "urgent"]),
            Task(id="task3", title="Task 3", status=TaskStatus.DOING, assignee="alice",
                 depends_on=["task2"], estimated_hours=4.0),
            Task(id="task4", title="Task 4", status=TaskStatus.TODO, assignee="charlie",
                 priority=TaskPriority.HIGH)
        ]

        for task in tasks:
            database.create_task(task)

        yield database

        shutil.rmtree(temp_dir)

    def test_export_all_tasks(self, temp_db):
        """Test exporting all tasks to JSONL."""
        exporter = TaskExporter(temp_db)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            output_path = f.name

        try:
            result = exporter.export_all_tasks(output_path)

            assert result['success'] is True
            assert result['exported_tasks'] == 4
            assert result['file_size_bytes'] > 0

            # Verify file contents
            with open(output_path, 'r') as f:
                lines = [line for line in f if line.strip() and not line.startswith('"__metadata__"')]

            assert len(lines) == 4  # 4 tasks exported

            # Verify first task
            task_data = json.loads(lines[0])
            assert task_data['title'] == "Task 1"
            assert '__exported_at__' in task_data

        finally:
            Path(output_path).unlink()

    def test_export_compressed(self, temp_db):
        """Test exporting to compressed JSONL."""
        exporter = TaskExporter(temp_db)

        with tempfile.NamedTemporaryFile(suffix='.jsonl.gz', delete=False) as f:
            output_path = f.name

        try:
            result = exporter.export_all_tasks(output_path, compress=True)

            assert result['success'] is True
            assert result['compressed'] is True

            # Verify compressed file can be read
            with gzip.open(output_path, 'rt') as f:
                lines = [line for line in f if line.strip()]

            assert len(lines) >= 4  # At least 4 tasks + possibly metadata

        finally:
            Path(output_path).unlink()

    def test_export_filtered_by_status(self, temp_db):
        """Test exporting tasks filtered by status."""
        exporter = TaskExporter(temp_db)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            output_path = f.name

        try:
            result = exporter.export_filtered_tasks(
                output_path,
                status_filter=[TaskStatus.TODO, TaskStatus.DOING]
            )

            assert result['success'] is True
            assert result['exported_tasks'] == 3  # task2, task3, task4

            # Verify filters were recorded
            assert 'status' in str(result['metadata']['filters_applied'])

        finally:
            Path(output_path).unlink()

    def test_export_filtered_by_assignee(self, temp_db):
        """Test exporting tasks filtered by assignee."""
        exporter = TaskExporter(temp_db)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            output_path = f.name

        try:
            result = exporter.export_filtered_tasks(
                output_path,
                assignee_filter="alice"
            )

            assert result['success'] is True
            assert result['exported_tasks'] == 2  # task1, task3

        finally:
            Path(output_path).unlink()

    def test_export_filtered_by_tags(self, temp_db):
        """Test exporting tasks filtered by tags."""
        exporter = TaskExporter(temp_db)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            output_path = f.name

        try:
            result = exporter.export_filtered_tasks(
                output_path,
                tag_filter=["frontend", "backend"]
            )

            assert result['success'] is True
            assert result['exported_tasks'] == 1  # only task2 has "frontend" tag

        finally:
            Path(output_path).unlink()

    def test_export_custom_filter(self, temp_db):
        """Test exporting tasks with custom filter function."""
        exporter = TaskExporter(temp_db)

        # Export only tasks with estimated hours
        def has_estimated_hours(task):
            return task.estimated_hours is not None

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            output_path = f.name

        try:
            result = exporter.export_filtered_tasks(
                output_path,
                custom_filter=has_estimated_hours
            )

            assert result['success'] is True
            assert result['exported_tasks'] == 1  # only task3 has estimated hours

        finally:
            Path(output_path).unlink()

    def test_export_with_sorting(self, temp_db):
        """Test exporting tasks with sorting."""
        exporter = TaskExporter(temp_db)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            output_path = f.name

        try:
            result = exporter.export_all_tasks(
                output_path,
                sort_by='title',
                reverse_sort=False
            )

            assert result['success'] is True

            # Verify sorting
            with open(output_path, 'r') as f:
                lines = [line for line in f if line.strip() and not line.startswith('"__metadata__"')]

            task_titles = [json.loads(line)['title'] for line in lines]
            expected_titles = ["Task 1", "Task 2", "Task 3", "Task 4"]
            assert task_titles == expected_titles

        finally:
            Path(output_path).unlink()

    def test_export_exclude_fields(self, temp_db):
        """Test exporting with excluded fields."""
        exporter = TaskExporter(temp_db)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            output_path = f.name

        try:
            result = exporter.export_all_tasks(
                output_path,
                exclude_fields=['context', 'estimated_hours']
            )

            assert result['success'] is True

            # Verify fields are excluded
            with open(output_path, 'r') as f:
                task_data = json.loads(f.readline())
                assert 'context' not in task_data
                assert 'estimated_hours' not in task_data
                assert 'title' in task_data  # Should still have title

        finally:
            Path(output_path).unlink()

    def test_export_incremental(self, temp_db):
        """Test incremental export based on update time."""
        exporter = TaskExporter(temp_db)

        # Update one task to create a newer timestamp
        task2 = temp_db.get_task("task2")
        task2.title = "Updated Task 2"
        temp_db.update_task(task2)

        since_time = datetime.now() - timedelta(minutes=1)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            output_path = f.name

        try:
            result = exporter.export_incremental(output_path, since_time)

            assert result['success'] is True
            assert result['exported_tasks'] >= 1  # At least the updated task
            assert 'incremental_since' in str(result['metadata']['filters_applied'])

        finally:
            Path(output_path).unlink()

    def test_export_by_project(self, temp_db):
        """Test exporting tasks grouped by project."""
        exporter = TaskExporter(temp_db)

        # Add project context to tasks
        task2 = temp_db.get_task("task2")
        task2.context['project'] = 'web-app'
        temp_db.update_task(task2)

        task3 = temp_db.get_task("task3")
        task3.context['project'] = 'web-app'
        temp_db.update_task(task3)

        with tempfile.TemporaryDirectory() as temp_dir:
            result = exporter.export_by_project(temp_dir)

            assert result['success'] is True
            assert result['projects_exported'] >= 1
            assert 'web-app' in result['project_files']

            # Verify project file was created
            web_app_file = Path(temp_dir) / 'web-app.jsonl'
            assert web_app_file.exists()

    def test_estimate_export_size(self, temp_db):
        """Test export size estimation."""
        exporter = TaskExporter(temp_db)
        tasks = temp_db.list_tasks()

        estimate = exporter.estimate_export_size(tasks)

        assert 'uncompressed' in estimate
        assert 'compressed' in estimate
        assert 'task_count' in estimate
        assert estimate['task_count'] == 4
        assert estimate['uncompressed'] > 0

    def test_validate_export_path(self, temp_db):
        """Test export path validation."""
        exporter = TaskExporter(temp_db)

        # Valid path
        with tempfile.TemporaryDirectory() as temp_dir:
            valid_path = Path(temp_dir) / "test.jsonl"
            is_valid, error = exporter.validate_export_path(str(valid_path))
            assert is_valid is True
            assert error == ""

        # Invalid directory (should be creatable)
        invalid_path = "/root/nonexistent/test.jsonl"
        is_valid, error = exporter.validate_export_path(invalid_path)
        # Result depends on system, but should not crash


class TestTaskImporter:
    """Test suite for TaskImporter."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_tasks.db"
        database = TaskDatabase(str(db_path))
        yield database
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_tasks_jsonl(self):
        """Create temporary JSONL file with sample tasks."""
        tasks = [
            {
                "id": "import1",
                "title": "Import Task 1",
                "description": "First imported task",
                "status": "todo",
                "priority": "medium",
                "tags": ["import", "test"],
                "assignee": "alice",
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00",
                "context": {"source": "test"}
            },
            {
                "id": "import2",
                "title": "Import Task 2",
                "description": "Second imported task",
                "status": "doing",
                "priority": "high",
                "depends_on": ["import1"],
                "estimated_hours": 3.0,
                "created_at": "2024-01-01T11:00:00",
                "updated_at": "2024-01-01T11:00:00",
                "context": {"source": "test"}
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for task in tasks:
                f.write(json.dumps(task) + '\n')
            return f.name

    def test_import_basic(self, temp_db, sample_tasks_jsonl):
        """Test basic import functionality."""
        importer = TaskImporter(temp_db)

        result = importer.import_tasks(sample_tasks_jsonl)

        assert result.success is True
        assert result.tasks_imported == 2
        assert result.tasks_updated == 0
        assert result.tasks_failed == 0
        assert len(result.errors) == 0

        # Verify tasks were imported
        task1 = temp_db.get_task("import1")
        task2 = temp_db.get_task("import2")

        assert task1 is not None
        assert task1.title == "Import Task 1"
        assert task1.assignee == "alice"

        assert task2 is not None
        assert task2.status == TaskStatus.DOING
        assert "import1" in task2.depends_on

    def test_import_dry_run(self, temp_db, sample_tasks_jsonl):
        """Test dry run import."""
        importer = TaskImporter(temp_db)

        result = importer.import_tasks(sample_tasks_jsonl, dry_run=True)

        assert result.success is True
        assert result.tasks_imported == 2

        # Verify no actual changes made
        assert temp_db.get_task("import1") is None
        assert temp_db.get_task("import2") is None

    def test_import_conflict_skip(self, temp_db, sample_tasks_jsonl):
        """Test import with conflict resolution - skip."""
        # Create existing task with same ID
        existing_task = Task(id="import1", title="Existing Task")
        temp_db.create_task(existing_task)

        importer = TaskImporter(temp_db)

        result = importer.import_tasks(
            sample_tasks_jsonl,
            conflict_resolution=ConflictResolution.SKIP
        )

        assert result.success is True
        assert result.tasks_imported == 1  # Only import2
        assert result.tasks_skipped == 1   # Skip import1

        # Verify existing task unchanged
        task1 = temp_db.get_task("import1")
        assert task1.title == "Existing Task"

        # Verify new task imported
        task2 = temp_db.get_task("import2")
        assert task2 is not None

    def test_import_conflict_overwrite(self, temp_db, sample_tasks_jsonl):
        """Test import with conflict resolution - overwrite."""
        # Create existing task with same ID
        existing_task = Task(id="import1", title="Existing Task")
        temp_db.create_task(existing_task)

        importer = TaskImporter(temp_db)

        result = importer.import_tasks(
            sample_tasks_jsonl,
            conflict_resolution=ConflictResolution.OVERWRITE
        )

        assert result.success is True
        assert result.tasks_imported == 1  # Only import2
        assert result.tasks_updated == 1   # Overwrite import1

        # Verify task was overwritten
        task1 = temp_db.get_task("import1")
        assert task1.title == "Import Task 1"  # New title

    def test_import_conflict_merge(self, temp_db, sample_tasks_jsonl):
        """Test import with conflict resolution - merge."""
        # Create existing task with same ID
        existing_task = Task(
            id="import1",
            title="Existing Task",
            tags=["existing"],
            context={"existing_field": "value"}
        )
        temp_db.create_task(existing_task)

        importer = TaskImporter(temp_db)

        result = importer.import_tasks(
            sample_tasks_jsonl,
            conflict_resolution=ConflictResolution.MERGE
        )

        assert result.success is True
        assert result.tasks_imported == 1  # Only import2
        assert result.tasks_updated == 1   # Merge import1

        # Verify task was merged
        task1 = temp_db.get_task("import1")
        assert task1.title == "Import Task 1"  # From incoming
        assert "existing" in task1.tags       # From existing
        assert "import" in task1.tags         # From incoming
        assert "existing_field" in task1.context  # From existing
        assert "source" in task1.context           # From incoming

    def test_import_conflict_create_new(self, temp_db, sample_tasks_jsonl):
        """Test import with conflict resolution - create new."""
        # Create existing task with same ID
        existing_task = Task(id="import1", title="Existing Task")
        temp_db.create_task(existing_task)

        importer = TaskImporter(temp_db)

        result = importer.import_tasks(
            sample_tasks_jsonl,
            conflict_resolution=ConflictResolution.CREATE_NEW
        )

        assert result.success is True
        assert result.tasks_imported == 2  # Both tasks (one with new ID)

        # Verify existing task unchanged
        original_task = temp_db.get_task("import1")
        assert original_task.title == "Existing Task"

        # Verify new task created with different ID
        all_tasks = temp_db.list_tasks()
        imported_tasks = [t for t in all_tasks if t.title == "Import Task 1"]
        assert len(imported_tasks) == 2  # Original + new copy

    def test_import_validation_error(self, temp_db):
        """Test import with validation errors."""
        # Create invalid task data
        invalid_tasks = [
            {
                "id": "invalid1",
                "title": "",  # Invalid: empty title
                "status": "invalid_status",  # Invalid status
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00"
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write(json.dumps(invalid_tasks[0]) + '\n')
            invalid_file = f.name

        try:
            importer = TaskImporter(temp_db)

            result = importer.import_tasks(
                invalid_file,
                validate=True,
                strict_validation=True
            )

            assert result.success is False
            assert result.tasks_failed == 1
            assert len(result.errors) > 0

        finally:
            Path(invalid_file).unlink()

    def test_import_compressed_file(self, temp_db, sample_tasks_jsonl):
        """Test importing from compressed JSONL file."""
        # Create compressed version
        compressed_file = sample_tasks_jsonl + '.gz'
        with open(sample_tasks_jsonl, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        try:
            importer = TaskImporter(temp_db)

            result = importer.import_tasks(compressed_file)

            assert result.success is True
            assert result.tasks_imported == 2

        finally:
            Path(compressed_file).unlink()
            Path(sample_tasks_jsonl).unlink()

    def test_import_multiple_files(self, temp_db):
        """Test importing from multiple files."""
        # Create first file
        tasks1 = [{"id": "multi1", "title": "Multi Task 1", "status": "todo",
                   "created_at": "2024-01-01T10:00:00", "updated_at": "2024-01-01T10:00:00"}]

        # Create second file
        tasks2 = [{"id": "multi2", "title": "Multi Task 2", "status": "doing",
                   "created_at": "2024-01-01T11:00:00", "updated_at": "2024-01-01T11:00:00"}]

        file1 = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
        file2 = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)

        with file1:
            for task in tasks1:
                file1.write(json.dumps(task) + '\n')
        with file2:
            for task in tasks2:
                file2.write(json.dumps(task) + '\n')

        try:
            importer = TaskImporter(temp_db)

            result = importer.import_from_multiple_files([file1.name, file2.name])

            assert result.success is True
            assert result.tasks_imported == 2

            # Verify metadata
            assert 'imported_from_files' in result.metadata
            assert len(result.metadata['imported_from_files']) == 2

        finally:
            Path(file1.name).unlink()
            Path(file2.name).unlink()

    def test_validate_import_file(self, temp_db, sample_tasks_jsonl):
        """Test import file validation."""
        importer = TaskImporter(temp_db)

        is_valid, errors = importer.validate_import_file(sample_tasks_jsonl)

        assert is_valid is True
        assert len(errors) == 0

    def test_get_import_preview(self, temp_db, sample_tasks_jsonl):
        """Test import preview functionality."""
        importer = TaskImporter(temp_db)

        preview = importer.get_import_preview(sample_tasks_jsonl)

        assert 'total_tasks' in preview
        assert preview['total_tasks'] == 2
        assert 'preview_tasks' in preview
        assert len(preview['preview_tasks']) == 2

        # Check task summary
        task1_summary = preview['preview_tasks'][0]
        assert 'id' in task1_summary
        assert 'title' in task1_summary
        assert 'status' in task1_summary
        assert task1_summary['title'] == "Import Task 1"

        # Check distributions
        assert 'status_distribution' in preview
        assert 'priority_distribution' in preview
        assert preview['status_distribution']['todo'] == 1
        assert preview['status_distribution']['doing'] == 1


class TestExportImportIntegration:
    """Integration tests for export/import workflow."""

    def test_round_trip_export_import(self):
        """Test complete export then import round trip."""
        # Setup source database
        temp_dir1 = tempfile.mkdtemp()
        db1_path = Path(temp_dir1) / "source.db"
        source_db = TaskDatabase(str(db1_path))

        original_tasks = [
            Task(id="round1", title="Round Trip 1", status=TaskStatus.DONE,
                 tags=["test", "round"], context={"test": True}),
            Task(id="round2", title="Round Trip 2", status=TaskStatus.TODO,
                 depends_on=["round1"], estimated_hours=2.5),
        ]

        for task in original_tasks:
            source_db.create_task(task)

        # Export tasks
        exporter = TaskExporter(source_db)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            export_file = f.name

        try:
            export_result = exporter.export_all_tasks(export_file)
            assert export_result['success'] is True

            # Setup destination database
            temp_dir2 = tempfile.mkdtemp()
            db2_path = Path(temp_dir2) / "dest.db"
            dest_db = TaskDatabase(str(db2_path))

            # Import tasks
            importer = TaskImporter(dest_db)
            import_result = importer.import_tasks(export_file)

            assert import_result.success is True
            assert import_result.tasks_imported == 2

            # Verify data integrity
            imported_task1 = dest_db.get_task("round1")
            imported_task2 = dest_db.get_task("round2")

            assert imported_task1.title == "Round Trip 1"
            assert imported_task1.status == TaskStatus.DONE
            assert "test" in imported_task1.tags
            assert imported_task1.context["test"] is True

            assert imported_task2.title == "Round Trip 2"
            assert imported_task2.depends_on == ["round1"]
            assert imported_task2.estimated_hours == 2.5

        finally:
            Path(export_file).unlink()
            shutil.rmtree(temp_dir1)
            shutil.rmtree(temp_dir2)

    def test_export_import_with_dependencies(self):
        """Test export/import with complex dependency chains."""
        # Create tasks with dependencies
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "deps.db"
        database = TaskDatabase(str(db_path))

        tasks = [
            Task(id="dep1", title="Dep 1", status=TaskStatus.DONE),
            Task(id="dep2", title="Dep 2", status=TaskStatus.TODO, depends_on=["dep1"]),
            Task(id="dep3", title="Dep 3", status=TaskStatus.TODO, depends_on=["dep1", "dep2"]),
            Task(id="dep4", title="Dep 4", status=TaskStatus.TODO, depends_on=["dep2"])
        ]

        for task in tasks:
            database.create_task(task)

        # Export
        exporter = TaskExporter(database)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            export_file = f.name

        try:
            export_result = exporter.export_all_tasks(export_file)
            assert export_result['success'] is True

            # Import into new database
            temp_dir2 = tempfile.mkdtemp()
            db2_path = Path(temp_dir2) / "imported.db"
            imported_db = TaskDatabase(str(db2_path))

            importer = TaskImporter(imported_db)
            import_result = importer.import_tasks(export_file)

            assert import_result.success is True

            # Verify dependencies preserved
            imported_dep3 = imported_db.get_task("dep3")
            assert set(imported_dep3.depends_on) == {"dep1", "dep2"}

            imported_dep4 = imported_db.get_task("dep4")
            assert imported_dep4.depends_on == ["dep2"]

        finally:
            Path(export_file).unlink()
            shutil.rmtree(temp_dir)
            shutil.rmtree(temp_dir2)