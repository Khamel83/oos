"""
Tests for OOS Task System dependency graph analysis.

Comprehensive test suite for DependencyGraph including cycle detection,
topological sorting, and impact analysis.
"""


import pytest

from src.oos_task_system.dependencies import CyclicDependencyError, DependencyGraph
from src.oos_task_system.models import Task, TaskPriority, TaskStatus


class TestDependencyGraph:
    """Test suite for DependencyGraph."""

    def create_tasks(self) -> list[Task]:
        """Create a set of test tasks."""
        return [
            Task(id="task1", title="Task 1", status=TaskStatus.DONE),
            Task(id="task2", title="Task 2", status=TaskStatus.TODO, depends_on=["task1"]),
            Task(id="task3", title="Task 3", status=TaskStatus.TODO, depends_on=["task1", "task2"]),
            Task(id="task4", title="Task 4", status=TaskStatus.TODO),
            Task(id="task5", title="Task 5", status=TaskStatus.TODO, depends_on=["task4"])
        ]

    def test_graph_initialization(self):
        """Test dependency graph initialization."""
        tasks = self.create_tasks()
        graph = DependencyGraph(tasks)

        assert len(graph.tasks) == 5
        assert "task1" in graph.tasks
        assert "task5" in graph.tasks

        # Check dependency mapping
        assert graph.dependencies["task2"] == {"task1"}
        assert graph.dependencies["task3"] == {"task1", "task2"}
        assert graph.dependencies["task4"] == set()

        # Check reverse dependencies
        assert graph.reverse_dependencies["task1"] == {"task2", "task3"}
        assert graph.reverse_dependencies["task2"] == {"task3"}

    def test_cycle_detection_no_cycles(self):
        """Test cycle detection with no cycles."""
        tasks = self.create_tasks()
        graph = DependencyGraph(tasks)

        cycles = graph.detect_cycles()
        assert len(cycles) == 0

    def test_cycle_detection_simple_cycle(self):
        """Test detection of simple two-node cycle."""
        tasks = [
            Task(id="task1", title="Task 1", depends_on=["task2"]),
            Task(id="task2", title="Task 2", depends_on=["task1"])
        ]
        graph = DependencyGraph(tasks)

        cycles = graph.detect_cycles()
        assert len(cycles) == 1

        cycle = cycles[0]
        # Cycle should contain both tasks
        assert len(cycle) == 3  # task -> other_task -> task
        assert "task1" in cycle
        assert "task2" in cycle

    def test_cycle_detection_complex_cycle(self):
        """Test detection of complex multi-node cycle."""
        tasks = [
            Task(id="task1", title="Task 1", depends_on=["task3"]),
            Task(id="task2", title="Task 2", depends_on=["task1"]),
            Task(id="task3", title="Task 3", depends_on=["task2"]),
            Task(id="task4", title="Task 4")  # Independent task
        ]
        graph = DependencyGraph(tasks)

        cycles = graph.detect_cycles()
        assert len(cycles) == 1

        cycle = cycles[0]
        assert len(cycle) == 4  # All three tasks + return to first
        cycle_ids = set(cycle[:-1])  # Remove duplicate at end
        assert cycle_ids == {"task1", "task2", "task3"}

    def test_topological_sort_valid(self):
        """Test topological sorting with valid graph."""
        tasks = self.create_tasks()
        graph = DependencyGraph(tasks)

        sorted_ids = graph.topological_sort()

        # Should have all tasks
        assert len(sorted_ids) == 5
        assert set(sorted_ids) == {"task1", "task2", "task3", "task4", "task5"}

        # Dependencies should come before dependents
        task1_pos = sorted_ids.index("task1")
        task2_pos = sorted_ids.index("task2")
        task3_pos = sorted_ids.index("task3")

        assert task1_pos < task2_pos  # task1 before task2
        assert task1_pos < task3_pos  # task1 before task3
        assert task2_pos < task3_pos  # task2 before task3

    def test_topological_sort_with_cycle(self):
        """Test topological sorting with cycles raises error."""
        tasks = [
            Task(id="task1", title="Task 1", depends_on=["task2"]),
            Task(id="task2", title="Task 2", depends_on=["task1"])
        ]
        graph = DependencyGraph(tasks)

        with pytest.raises(CyclicDependencyError) as exc_info:
            graph.topological_sort()

        assert "task1" in str(exc_info.value)
        assert "task2" in str(exc_info.value)

    def test_get_ready_tasks(self):
        """Test getting tasks ready to work on."""
        tasks = [
            Task(id="task1", title="Task 1", status=TaskStatus.DONE),
            Task(id="task2", title="Task 2", status=TaskStatus.TODO, depends_on=["task1"]),
            Task(id="task3", title="Task 3", status=TaskStatus.TODO, depends_on=["task2"]),
            Task(id="task4", title="Task 4", status=TaskStatus.TODO),
            Task(id="task5", title="Task 5", status=TaskStatus.DOING)
        ]
        graph = DependencyGraph(tasks)

        ready_tasks = graph.get_ready_tasks()

        # Should include task2 (task1 is done) and task4 (no dependencies)
        # Should not include task3 (task2 not done) or task5 (not TODO status)
        ready_ids = set(ready_tasks)
        assert "task2" in ready_ids
        assert "task4" in ready_ids
        assert "task3" not in ready_ids
        assert "task5" not in ready_ids

    def test_get_ready_tasks_priority_ordering(self):
        """Test that ready tasks are ordered by priority."""
        tasks = [
            Task(id="low", title="Low Priority", status=TaskStatus.TODO, priority=TaskPriority.LOW),
            Task(id="high", title="High Priority", status=TaskStatus.TODO, priority=TaskPriority.HIGH),
            Task(id="urgent", title="Urgent Priority", status=TaskStatus.TODO, priority=TaskPriority.URGENT),
            Task(id="medium", title="Medium Priority", status=TaskStatus.TODO, priority=TaskPriority.MEDIUM)
        ]
        graph = DependencyGraph(tasks)

        ready_tasks = graph.get_ready_tasks()

        # Should be ordered by priority: urgent, high, medium, low
        assert ready_tasks[0] == "urgent"
        assert ready_tasks[1] == "high"
        assert ready_tasks[2] == "medium"
        assert ready_tasks[3] == "low"

    def test_get_blocked_tasks(self):
        """Test getting blocked tasks."""
        tasks = [
            Task(id="task1", title="Task 1", status=TaskStatus.TODO),
            Task(id="task2", title="Task 2", status=TaskStatus.TODO, depends_on=["task1"]),
            Task(id="task3", title="Task 3", status=TaskStatus.TODO),
            Task(id="task4", title="Task 4", status=TaskStatus.DONE, depends_on=["task3"])
        ]
        graph = DependencyGraph(tasks)

        blocked_tasks = graph.get_blocked_tasks()

        # task2 is blocked by task1 (not done)
        # task4 is not blocked (done status, and task3 dependency is satisfied for done tasks)
        blocked_ids = set(blocked_tasks)
        assert "task2" in blocked_ids
        assert "task1" not in blocked_ids  # No dependencies
        assert "task3" not in blocked_ids  # No dependencies
        assert "task4" not in blocked_ids  # Not TODO status

    def test_get_blocking_tasks(self):
        """Test getting tasks that block a specific task."""
        tasks = [
            Task(id="task1", title="Task 1", status=TaskStatus.TODO),
            Task(id="task2", title="Task 2", status=TaskStatus.DONE),
            Task(id="task3", title="Task 3", status=TaskStatus.TODO, depends_on=["task1", "task2"])
        ]
        graph = DependencyGraph(tasks)

        blocking = graph.get_blocking_tasks("task3")

        # Only task1 should be blocking (task2 is done)
        assert blocking == ["task1"]

        # Task with no dependencies should have no blocking tasks
        assert graph.get_blocking_tasks("task1") == []

    def test_get_impact_analysis(self):
        """Test impact analysis for task status changes."""
        tasks = [
            Task(id="task1", title="Task 1"),
            Task(id="task2", title="Task 2", depends_on=["task1"]),
            Task(id="task3", title="Task 3", depends_on=["task1"]),
            Task(id="task4", title="Task 4", depends_on=["task2"]),
            Task(id="task5", title="Task 5", depends_on=["task3"])
        ]
        graph = DependencyGraph(tasks)

        impact = graph.get_impact_analysis("task1")

        # task2 and task3 directly depend on task1
        directly_affected = set(impact['directly_affected'])
        assert directly_affected == {"task2", "task3"}

        # task4 and task5 are transitively affected
        transitively_affected = set(impact['transitively_affected'])
        assert transitively_affected == {"task4", "task5"}

    def test_get_critical_path(self):
        """Test critical path calculation."""
        tasks = [
            Task(id="task1", title="Task 1"),
            Task(id="task2", title="Task 2", depends_on=["task1"]),
            Task(id="task3", title="Task 3", depends_on=["task2"]),
            Task(id="task4", title="Task 4", depends_on=["task1"]),
            Task(id="task5", title="Task 5", depends_on=["task3", "task4"])
        ]
        graph = DependencyGraph(tasks)

        critical_path = graph.get_critical_path()

        # Longest path should be task1 -> task2 -> task3 -> task5
        expected_path = ["task1", "task2", "task3", "task5"]
        assert critical_path == expected_path

    def test_validate_dependency_valid(self):
        """Test validation of valid dependency."""
        tasks = [
            Task(id="task1", title="Task 1"),
            Task(id="task2", title="Task 2")
        ]
        graph = DependencyGraph(tasks)

        is_valid, message = graph.validate_dependency("task2", "task1")
        assert is_valid is True
        assert message == ""

    def test_validate_dependency_self_reference(self):
        """Test validation rejects self-dependency."""
        tasks = [Task(id="task1", title="Task 1")]
        graph = DependencyGraph(tasks)

        is_valid, message = graph.validate_dependency("task1", "task1")
        assert is_valid is False
        assert "cannot depend on itself" in message

    def test_validate_dependency_nonexistent_task(self):
        """Test validation rejects nonexistent tasks."""
        tasks = [Task(id="task1", title="Task 1")]
        graph = DependencyGraph(tasks)

        is_valid, message = graph.validate_dependency("task1", "nonexistent")
        assert is_valid is False
        assert "does not exist" in message

        is_valid, message = graph.validate_dependency("nonexistent", "task1")
        assert is_valid is False
        assert "does not exist" in message

    def test_validate_dependency_would_create_cycle(self):
        """Test validation rejects dependencies that would create cycles."""
        tasks = [
            Task(id="task1", title="Task 1", depends_on=["task2"]),
            Task(id="task2", title="Task 2")
        ]
        graph = DependencyGraph(tasks)

        # Adding task2 -> task1 would create a cycle
        is_valid, message = graph.validate_dependency("task2", "task1")
        assert is_valid is False
        assert "circular dependency" in message

    def test_validate_dependency_already_exists(self):
        """Test validation rejects existing dependencies."""
        tasks = [
            Task(id="task1", title="Task 1"),
            Task(id="task2", title="Task 2", depends_on=["task1"])
        ]
        graph = DependencyGraph(tasks)

        is_valid, message = graph.validate_dependency("task2", "task1")
        assert is_valid is False
        assert "already exists" in message

    def test_get_dependency_chains(self):
        """Test getting dependency chains for a task."""
        tasks = [
            Task(id="task1", title="Task 1"),
            Task(id="task2", title="Task 2"),
            Task(id="task3", title="Task 3", depends_on=["task1", "task2"]),
            Task(id="task4", title="Task 4", depends_on=["task3"])
        ]
        graph = DependencyGraph(tasks)

        chains = graph.get_dependency_chains("task4")

        # Should have two chains: task1->task3->task4 and task2->task3->task4
        assert len(chains) == 2

        chain_sets = [set(chain) for chain in chains]
        expected_chains = [
            {"task1", "task3", "task4"},
            {"task2", "task3", "task4"}
        ]

        for expected in expected_chains:
            assert expected in chain_sets

    def test_get_dependency_chains_no_dependencies(self):
        """Test dependency chains for task with no dependencies."""
        tasks = [Task(id="task1", title="Task 1")]
        graph = DependencyGraph(tasks)

        chains = graph.get_dependency_chains("task1")

        # Should have one chain with just the task itself
        assert len(chains) == 1
        assert chains[0] == ["task1"]

    def test_get_dependency_chains_cycle_prevention(self):
        """Test that dependency chains prevent infinite recursion on cycles."""
        tasks = [
            Task(id="task1", title="Task 1", depends_on=["task2"]),
            Task(id="task2", title="Task 2", depends_on=["task1"])
        ]
        graph = DependencyGraph(tasks)

        # Should not hang or crash despite the cycle
        chains = graph.get_dependency_chains("task1", max_depth=5)

        # Should return some result without infinite recursion
        assert isinstance(chains, list)

    def test_get_stats(self):
        """Test dependency graph statistics."""
        tasks = [
            Task(id="task1", title="Task 1", status=TaskStatus.DONE),
            Task(id="task2", title="Task 2", status=TaskStatus.TODO, depends_on=["task1"]),
            Task(id="task3", title="Task 3", status=TaskStatus.TODO, depends_on=["task2"]),
            Task(id="task4", title="Task 4", status=TaskStatus.TODO)
        ]
        graph = DependencyGraph(tasks)

        stats = graph.get_stats()

        assert stats['total_tasks'] == 4
        assert stats['ready_tasks'] == 2  # task2 and task4
        assert stats['blocked_tasks'] == 1  # task3
        assert stats['total_dependencies'] == 2  # task2->task1, task3->task2
        assert stats['cycles_detected'] == 0

    def test_empty_graph(self):
        """Test behavior with empty task list."""
        graph = DependencyGraph([])

        assert len(graph.tasks) == 0
        assert graph.detect_cycles() == []
        assert graph.topological_sort() == []
        assert graph.get_ready_tasks() == []
        assert graph.get_blocked_tasks() == []

        stats = graph.get_stats()
        assert stats['total_tasks'] == 0
        assert stats['ready_tasks'] == 0

    def test_priority_value_helper(self):
        """Test priority value conversion."""
        tasks = [
            Task(id="task1", title="Task 1", priority=TaskPriority.LOW),
            Task(id="task2", title="Task 2", priority=TaskPriority.URGENT)
        ]
        graph = DependencyGraph(tasks)

        # Test the internal priority value method
        assert graph._priority_value(TaskPriority.LOW) == 1
        assert graph._priority_value(TaskPriority.MEDIUM) == 2
        assert graph._priority_value(TaskPriority.HIGH) == 3
        assert graph._priority_value(TaskPriority.URGENT) == 4

        # Test with string values
        assert graph._priority_value('low') == 1
        assert graph._priority_value('urgent') == 4
