"""
OOS Task Memory System - Optional task management for OOS projects.

This system provides project-embedded task memory with git-syncable storage.
All functionality is optional and can be disabled via configuration.

Key Features:
- SQLite database for fast local operations
- JSONL export for git synchronization
- Dependency tracking and ready task identification
- Agent-friendly CLI interface
- Zero external dependencies beyond SQLite

Usage:
    from src.oos_task_system import Task, TaskDatabase

    # Initialize database
    db = TaskDatabase("project/.oos/tasks/tasks.db")

    # Create and manage tasks
    task = Task(title="Implement feature", description="Add new functionality")
    db.create_task(task)

    # Find ready tasks
    ready_tasks = db.get_ready_tasks()
"""

from .models import Task, TaskStatus, TaskPriority
from .database import TaskDatabase
from .dependencies import DependencyGraph, CyclicDependencyError
from .validation import TaskValidator, ValidationError, ValidationResult
from .jsonl_export import TaskExporter, ExportError
from .jsonl_import import TaskImporter, ImportResult, ConflictResolution

# CLI is optional import to avoid requiring click for basic usage
try:
    from .cli import cli
    CLI_AVAILABLE = True
except ImportError:
    cli = None
    CLI_AVAILABLE = False

__version__ = "1.0.0"
__all__ = [
    'Task', 'TaskStatus', 'TaskPriority', 'TaskDatabase',
    'DependencyGraph', 'CyclicDependencyError',
    'TaskValidator', 'ValidationError', 'ValidationResult',
    'TaskExporter', 'ExportError',
    'TaskImporter', 'ImportResult', 'ConflictResolution',
    'cli', 'CLI_AVAILABLE'
]


def get_version() -> str:
    """Get the version of the task system."""
    return __version__


def create_database(db_path: str) -> TaskDatabase:
    """
    Convenience function to create a new TaskDatabase instance.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Configured TaskDatabase instance
    """
    return TaskDatabase(db_path)