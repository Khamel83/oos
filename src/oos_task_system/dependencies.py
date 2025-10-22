"""
Dependency graph analysis for OOS Task Memory System.

Provides DependencyGraph class for analyzing task relationships,
detecting cycles, and computing work order.
"""

from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict, deque

from .models import Task, TaskStatus


class CyclicDependencyError(Exception):
    """Raised when a circular dependency is detected."""

    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        super().__init__(f"Circular dependency detected: {' -> '.join(cycle + [cycle[0]])}")


class DependencyGraph:
    """
    Analyzes and manages task dependency relationships.

    Provides cycle detection, topological sorting, and dependency
    impact analysis for task management.
    """

    def __init__(self, tasks: List[Task]):
        """Initialize dependency graph from list of tasks."""
        self.tasks = {task.id: task for task in tasks}
        self.dependencies = self._build_dependency_map()
        self.reverse_dependencies = self._build_reverse_dependency_map()

    def _build_dependency_map(self) -> Dict[str, Set[str]]:
        """Build mapping of task_id -> set of dependencies."""
        deps = defaultdict(set)
        for task in self.tasks.values():
            deps[task.id] = set(task.depends_on)
        return dict(deps)

    def _build_reverse_dependency_map(self) -> Dict[str, Set[str]]:
        """Build mapping of task_id -> set of tasks that depend on it."""
        reverse_deps = defaultdict(set)
        for task_id, deps in self.dependencies.items():
            for dep_id in deps:
                reverse_deps[dep_id].add(task_id)
        return dict(reverse_deps)

    def detect_cycles(self) -> List[List[str]]:
        """
        Detect all circular dependencies in the graph.

        Returns:
            List of cycles, where each cycle is a list of task IDs
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(task_id: str, path: List[str]) -> None:
            if task_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(task_id)
                cycle = path[cycle_start:] + [task_id]
                cycles.append(cycle)
                return

            if task_id in visited:
                return

            visited.add(task_id)
            rec_stack.add(task_id)
            path.append(task_id)

            for dep_id in self.dependencies.get(task_id, set()):
                if dep_id in self.tasks:  # Only follow valid dependencies
                    dfs(dep_id, path)

            rec_stack.remove(task_id)
            path.pop()

        for task_id in self.tasks:
            if task_id not in visited:
                dfs(task_id, [])

        return cycles

    def topological_sort(self) -> List[str]:
        """
        Return tasks in topological order (dependencies first).

        Raises:
            CyclicDependencyError: If circular dependencies exist

        Returns:
            List of task IDs in dependency order
        """
        cycles = self.detect_cycles()
        if cycles:
            raise CyclicDependencyError(cycles[0])

        # Kahn's algorithm
        in_degree = defaultdict(int)
        for task_id in self.tasks:
            in_degree[task_id] = len(self.dependencies.get(task_id, set()))

        queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
        result = []

        while queue:
            task_id = queue.popleft()
            result.append(task_id)

            # Reduce in-degree for dependent tasks
            for dependent_id in self.reverse_dependencies.get(task_id, set()):
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)

        return result

    def get_ready_tasks(self) -> List[str]:
        """
        Get tasks that are ready to work on (no pending dependencies).

        Returns:
            List of task IDs ready for work, ordered by priority
        """
        ready_tasks = []

        for task_id, task in self.tasks.items():
            if task.status != TaskStatus.TODO:
                continue

            # Check if all dependencies are completed
            all_deps_done = True
            for dep_id in self.dependencies.get(task_id, set()):
                if dep_id in self.tasks:
                    dep_task = self.tasks[dep_id]
                    if dep_task.status != TaskStatus.DONE:
                        all_deps_done = False
                        break

            if all_deps_done:
                ready_tasks.append(task_id)

        # Sort by priority (urgent first) then by creation date
        ready_tasks.sort(key=lambda tid: (
            -self._priority_value(self.tasks[tid].priority),
            self.tasks[tid].created_at
        ))

        return ready_tasks

    def get_blocked_tasks(self) -> List[str]:
        """
        Get tasks that are blocked by pending dependencies.

        Returns:
            List of task IDs that are blocked
        """
        blocked_tasks = []

        for task_id, task in self.tasks.items():
            if task.status != TaskStatus.TODO:
                continue

            # Check if any dependencies are not completed
            has_pending_deps = False
            for dep_id in self.dependencies.get(task_id, set()):
                if dep_id in self.tasks:
                    dep_task = self.tasks[dep_id]
                    if dep_task.status != TaskStatus.DONE:
                        has_pending_deps = True
                        break

            if has_pending_deps:
                blocked_tasks.append(task_id)

        return blocked_tasks

    def get_blocking_tasks(self, task_id: str) -> List[str]:
        """
        Get tasks that are blocking the specified task.

        Args:
            task_id: ID of task to check

        Returns:
            List of task IDs that are blocking this task
        """
        blocking = []

        for dep_id in self.dependencies.get(task_id, set()):
            if dep_id in self.tasks:
                dep_task = self.tasks[dep_id]
                if dep_task.status != TaskStatus.DONE:
                    blocking.append(dep_id)

        return blocking

    def get_impact_analysis(self, task_id: str) -> Dict[str, List[str]]:
        """
        Analyze the impact of changing a task's status.

        Args:
            task_id: ID of task to analyze

        Returns:
            Dictionary with 'directly_affected' and 'transitively_affected' lists
        """
        if task_id not in self.tasks:
            return {'directly_affected': [], 'transitively_affected': []}

        directly_affected = list(self.reverse_dependencies.get(task_id, set()))
        transitively_affected = []

        # BFS to find all transitively affected tasks
        visited = set(directly_affected)
        queue = deque(directly_affected)

        while queue:
            current_id = queue.popleft()
            for affected_id in self.reverse_dependencies.get(current_id, set()):
                if affected_id not in visited:
                    visited.add(affected_id)
                    transitively_affected.append(affected_id)
                    queue.append(affected_id)

        return {
            'directly_affected': directly_affected,
            'transitively_affected': transitively_affected
        }

    def get_critical_path(self) -> List[str]:
        """
        Find the critical path (longest chain of dependencies).

        Returns:
            List of task IDs representing the critical path
        """
        try:
            sorted_tasks = self.topological_sort()
        except CyclicDependencyError:
            return []

        # Calculate longest path to each task
        distances = {task_id: 0 for task_id in self.tasks}
        predecessors = {}

        for task_id in sorted_tasks:
            for dependent_id in self.reverse_dependencies.get(task_id, set()):
                if distances[task_id] + 1 > distances[dependent_id]:
                    distances[dependent_id] = distances[task_id] + 1
                    predecessors[dependent_id] = task_id

        # Find task with maximum distance
        if not distances:
            return []

        end_task = max(distances.keys(), key=lambda tid: distances[tid])

        # Reconstruct path
        path = []
        current = end_task
        while current is not None:
            path.append(current)
            current = predecessors.get(current)

        path.reverse()
        return path

    def validate_dependency(self, task_id: str, dependency_id: str) -> Tuple[bool, str]:
        """
        Validate if adding a dependency would create issues.

        Args:
            task_id: Task that would depend on dependency_id
            dependency_id: Task that would be depended upon

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if both tasks exist
        if task_id not in self.tasks:
            return False, f"Task {task_id} does not exist"

        if dependency_id not in self.tasks:
            return False, f"Dependency task {dependency_id} does not exist"

        # Check for self-dependency
        if task_id == dependency_id:
            return False, "Task cannot depend on itself"

        # Check if dependency already exists
        if dependency_id in self.dependencies.get(task_id, set()):
            return False, f"Dependency already exists: {task_id} -> {dependency_id}"

        # Check if adding this dependency would create a cycle
        temp_deps = self.dependencies.copy()
        temp_deps[task_id] = temp_deps.get(task_id, set()) | {dependency_id}

        # Create temporary graph to test for cycles
        temp_graph = DependencyGraph([])
        temp_graph.tasks = self.tasks
        temp_graph.dependencies = temp_deps
        temp_graph.reverse_dependencies = temp_graph._build_reverse_dependency_map()

        cycles = temp_graph.detect_cycles()
        if cycles:
            cycle_str = ' -> '.join(cycles[0] + [cycles[0][0]])
            return False, f"Would create circular dependency: {cycle_str}"

        return True, ""

    def get_dependency_chains(self, task_id: str, max_depth: int = 10) -> List[List[str]]:
        """
        Get all dependency chains for a task.

        Args:
            task_id: Task to analyze
            max_depth: Maximum chain depth to prevent infinite recursion

        Returns:
            List of dependency chains (each chain is a list of task IDs)
        """
        if task_id not in self.tasks:
            return []

        chains = []

        def dfs(current_id: str, chain: List[str], depth: int) -> None:
            if depth > max_depth:
                return

            dependencies = self.dependencies.get(current_id, set())
            if not dependencies:
                # Leaf node - add completed chain
                chains.append(chain + [current_id])
                return

            for dep_id in dependencies:
                if dep_id in self.tasks and dep_id not in chain:  # Avoid cycles
                    dfs(dep_id, chain + [current_id], depth + 1)

        dfs(task_id, [], 0)
        return chains

    def _priority_value(self, priority) -> int:
        """Convert priority enum to numeric value for sorting."""
        priority_values = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'urgent': 4
        }
        if hasattr(priority, 'value'):
            return priority_values.get(priority.value, 2)
        return priority_values.get(priority, 2)

    def get_stats(self) -> Dict[str, int]:
        """Get dependency graph statistics."""
        ready_count = len(self.get_ready_tasks())
        blocked_count = len(self.get_blocked_tasks())
        cycles = self.detect_cycles()

        return {
            'total_tasks': len(self.tasks),
            'ready_tasks': ready_count,
            'blocked_tasks': blocked_count,
            'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
            'cycles_detected': len(cycles),
            'max_depth': max([len(chain) for chain in self.get_dependency_chains(tid)]
                           for tid in self.tasks) if self.tasks else 0
        }