"""
SQLite database operations for OOS Task Memory System.

Provides TaskDatabase class with CRUD operations, dependency tracking,
and database schema management.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import Task, TaskPriority, TaskStatus


class TaskDatabase:
    """
    SQLite database interface for task management.

    Handles all database operations including schema creation,
    CRUD operations, and dependency queries.
    """

    def __init__(self, db_path: str):
        """Initialize database connection and ensure schema exists."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper settings."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn

    def _init_schema(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT DEFAULT 'todo',
                    priority TEXT DEFAULT 'medium',
                    tags TEXT DEFAULT '[]',
                    assignee TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    due_date TEXT,
                    estimated_hours REAL,
                    actual_hours REAL,
                    context TEXT DEFAULT '{}'
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    depends_on_id TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                    FOREIGN KEY (depends_on_id) REFERENCES tasks (id) ON DELETE CASCADE,
                    UNIQUE (task_id, depends_on_id)
                )
            """)

            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks (created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks (assignee)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_task ON task_dependencies (task_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_depends ON task_dependencies (depends_on_id)")

    def create_task(self, task: Task) -> Task:
        """Create a new task in the database."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO tasks (
                    id, title, description, status, priority, tags, assignee,
                    created_at, updated_at, completed_at, due_date,
                    estimated_hours, actual_hours, context
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id, task.title, task.description,
                task.status.value, task.priority.value,
                json.dumps(task.tags), task.assignee,
                task.created_at.isoformat(), task.updated_at.isoformat(),
                task.completed_at.isoformat() if task.completed_at else None,
                task.due_date.isoformat() if task.due_date else None,
                task.estimated_hours, task.actual_hours,
                json.dumps(task.context)
            ))

            # Insert dependencies
            for dep_id in task.depends_on:
                self._add_dependency(conn, task.id, dep_id)

        return task

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if not row:
                return None

            # Get dependencies
            deps = conn.execute(
                "SELECT depends_on_id FROM task_dependencies WHERE task_id = ?",
                (task_id,)
            ).fetchall()
            depends_on = [dep['depends_on_id'] for dep in deps]

            # Get blocks (tasks that depend on this one)
            blocks = conn.execute(
                "SELECT task_id FROM task_dependencies WHERE depends_on_id = ?",
                (task_id,)
            ).fetchall()
            blocks_list = [block['task_id'] for block in blocks]

            return self._row_to_task(row, depends_on, blocks_list)

    def update_task(self, task: Task) -> Task:
        """Update an existing task."""
        task.updated_at = datetime.now()

        with self._get_connection() as conn:
            conn.execute("""
                UPDATE tasks SET
                    title = ?, description = ?, status = ?, priority = ?,
                    tags = ?, assignee = ?, updated_at = ?, completed_at = ?,
                    due_date = ?, estimated_hours = ?, actual_hours = ?, context = ?
                WHERE id = ?
            """, (
                task.title, task.description, task.status.value, task.priority.value,
                json.dumps(task.tags), task.assignee, task.updated_at.isoformat(),
                task.completed_at.isoformat() if task.completed_at else None,
                task.due_date.isoformat() if task.due_date else None,
                task.estimated_hours, task.actual_hours, json.dumps(task.context),
                task.id
            ))

            # Update dependencies - remove all and re-add
            conn.execute("DELETE FROM task_dependencies WHERE task_id = ?", (task.id,))
            for dep_id in task.depends_on:
                self._add_dependency(conn, task.id, dep_id)

        return task

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def list_tasks(self, status: TaskStatus | None = None,
                   assignee: str | None = None,
                   tags: list[str] | None = None) -> list[Task]:
        """List tasks with optional filtering."""
        query = "SELECT * FROM tasks"
        params = []
        conditions = []

        if status:
            conditions.append("status = ?")
            params.append(status.value)

        if assignee:
            conditions.append("assignee = ?")
            params.append(assignee)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            tasks = []

            for row in rows:
                # Get dependencies for each task
                deps = conn.execute(
                    "SELECT depends_on_id FROM task_dependencies WHERE task_id = ?",
                    (row['id'],)
                ).fetchall()
                depends_on = [dep['depends_on_id'] for dep in deps]

                # Get blocks
                blocks = conn.execute(
                    "SELECT task_id FROM task_dependencies WHERE depends_on_id = ?",
                    (row['id'],)
                ).fetchall()
                blocks_list = [block['task_id'] for block in blocks]

                task = self._row_to_task(row, depends_on, blocks_list)

                # Filter by tags if specified
                if tags and not any(tag in task.tags for tag in tags):
                    continue

                tasks.append(task)

        return tasks

    def get_ready_tasks(self) -> list[Task]:
        """Get tasks that are ready to work on (no pending dependencies)."""
        with self._get_connection() as conn:
            # Find TODO tasks that have no dependencies or all dependencies are complete
            query = """
                SELECT t.* FROM tasks t
                WHERE t.status = 'todo'
                AND NOT EXISTS (
                    SELECT 1 FROM task_dependencies td
                    JOIN tasks dep ON td.depends_on_id = dep.id
                    WHERE td.task_id = t.id
                    AND dep.status != 'done'
                )
                ORDER BY
                    CASE t.priority
                        WHEN 'urgent' THEN 4
                        WHEN 'high' THEN 3
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 1
                        ELSE 0
                    END DESC,
                    t.created_at ASC
            """

            rows = conn.execute(query).fetchall()
            tasks = []

            for row in rows:
                # Get dependencies and blocks for each task
                deps = conn.execute(
                    "SELECT depends_on_id FROM task_dependencies WHERE task_id = ?",
                    (row['id'],)
                ).fetchall()
                depends_on = [dep['depends_on_id'] for dep in deps]

                blocks = conn.execute(
                    "SELECT task_id FROM task_dependencies WHERE depends_on_id = ?",
                    (row['id'],)
                ).fetchall()
                blocks_list = [block['task_id'] for block in blocks]

                tasks.append(self._row_to_task(row, depends_on, blocks_list))

        return tasks

    def get_blocked_tasks(self) -> list[Task]:
        """Get tasks that are blocked by pending dependencies."""
        with self._get_connection() as conn:
            query = """
                SELECT DISTINCT t.* FROM tasks t
                JOIN task_dependencies td ON t.id = td.task_id
                JOIN tasks dep ON td.depends_on_id = dep.id
                WHERE t.status = 'todo'
                AND dep.status != 'done'
                ORDER BY t.created_at ASC
            """

            rows = conn.execute(query).fetchall()
            tasks = []

            for row in rows:
                deps = conn.execute(
                    "SELECT depends_on_id FROM task_dependencies WHERE task_id = ?",
                    (row['id'],)
                ).fetchall()
                depends_on = [dep['depends_on_id'] for dep in deps]

                blocks = conn.execute(
                    "SELECT task_id FROM task_dependencies WHERE depends_on_id = ?",
                    (row['id'],)
                ).fetchall()
                blocks_list = [block['task_id'] for block in blocks]

                tasks.append(self._row_to_task(row, depends_on, blocks_list))

        return tasks

    def add_dependency(self, task_id: str, depends_on_id: str) -> bool:
        """Add a dependency between tasks."""
        with self._get_connection() as conn:
            return self._add_dependency(conn, task_id, depends_on_id)

    def remove_dependency(self, task_id: str, depends_on_id: str) -> bool:
        """Remove a dependency between tasks."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM task_dependencies WHERE task_id = ? AND depends_on_id = ?",
                (task_id, depends_on_id)
            )
            return cursor.rowcount > 0

    def _add_dependency(self, conn: sqlite3.Connection, task_id: str, depends_on_id: str) -> bool:
        """Add dependency within existing connection."""
        try:
            conn.execute(
                "INSERT INTO task_dependencies (task_id, depends_on_id) VALUES (?, ?)",
                (task_id, depends_on_id)
            )
            return True
        except sqlite3.IntegrityError:
            return False  # Dependency already exists

    def _row_to_task(self, row: sqlite3.Row, depends_on: list[str], blocks: list[str]) -> Task:
        """Convert database row to Task object."""
        return Task(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            status=TaskStatus(row['status']),
            priority=TaskPriority(row['priority']),
            tags=json.loads(row['tags']),
            depends_on=depends_on,
            blocks=blocks,
            assignee=row['assignee'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.now(),
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
            due_date=datetime.fromisoformat(row['due_date']) if row['due_date'] else None,
            estimated_hours=row['estimated_hours'],
            actual_hours=row['actual_hours'],
            context=json.loads(row['context']) if row['context'] else {}
        )

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) as count FROM tasks").fetchone()['count']

            status_counts = {}
            for status in TaskStatus:
                count = conn.execute(
                    "SELECT COUNT(*) as count FROM tasks WHERE status = ?",
                    (status.value,)
                ).fetchone()['count']
                status_counts[status.value] = count

            return {
                'total_tasks': total,
                'status_counts': status_counts,
                'db_path': str(self.db_path),
                'db_size_bytes': self.db_path.stat().st_size if self.db_path.exists() else 0
            }

    def export_tasks(self, output_path: str, **export_options) -> dict[str, Any]:
        """
        Export tasks to JSONL file.

        Convenience method that creates an exporter and performs export.

        Args:
            output_path: Path to output JSONL file
            **export_options: Options passed to TaskExporter

        Returns:
            Export result dictionary
        """
        # Local import to avoid circular dependency
        from .jsonl_export import TaskExporter
        exporter = TaskExporter(self)
        return exporter.export_all_tasks(output_path, **export_options)

    def import_tasks(self, input_path: str, **import_options) -> dict[str, Any]:
        """
        Import tasks from JSONL file.

        Convenience method that creates an importer and performs import.

        Args:
            input_path: Path to input JSONL file
            **import_options: Options passed to TaskImporter

        Returns:
            ImportResult dictionary
        """
        # Local import to avoid circular dependency
        from .jsonl_import import TaskImporter
        importer = TaskImporter(self)
        result = importer.import_tasks(input_path, **import_options)
        return result.__dict__

    def sync_tasks(self, jsonl_path: str, conflict_resolution: str = "merge") -> dict[str, Any]:
        """
        Synchronize tasks with JSONL file (export then import with merge).

        This method exports current tasks, imports from the JSONL file,
        and resolves conflicts using the specified strategy.

        Args:
            jsonl_path: Path to JSONL file to sync with
            conflict_resolution: How to handle conflicts

        Returns:
            Synchronization result
        """
        # Create temporary backup export
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            backup_path = f.name

        try:
            # Export current tasks as backup
            export_result = self.export_tasks(backup_path)
            if not export_result['success']:
                return {'success': False, 'error': 'Failed to export backup', 'export_result': export_result}

            # Import from sync file
            import_result = self.import_tasks(jsonl_path, conflict_resolution=conflict_resolution)

            return {
                'success': import_result['success'],
                'backup_exported': export_result['exported_tasks'],
                'tasks_imported': import_result['tasks_imported'],
                'tasks_updated': import_result['tasks_updated'],
                'tasks_skipped': import_result['tasks_skipped'],
                'errors': import_result['errors'],
                'warnings': import_result['warnings'],
                'backup_path': backup_path
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'backup_path': backup_path}
