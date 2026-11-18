from typing import Dict, List, Set, Optional
from .task import Task
from ..core.agent_state import TaskStatus
from ..core.exceptions import CyclicDependencyError

class TaskGraph:
    """
    Directed Acyclic Graph (DAG) representing tasks and dependencies.
    Provides cycle detection, dependency resolution, and parallel execution layers.
    """
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._dependents: Dict[str, List[str]] = {} # parent -> [children]

    def add_task(self, task: Task):
        self._tasks[task.task_id] = task
        if task.task_id not in self._dependents:
            self._dependents[task.task_id] = []
        for dep in task.dependencies:
            if dep not in self._dependents:
                self._dependents[dep] = []
            self._dependents[dep].append(task.task_id)

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[Task]:
        return list(self._tasks.values())

    def validate_graph(self):
        """Validates all dependencies exist and checks for cycles."""
        for task in self._tasks.values():
            for dep in task.dependencies:
                if dep not in self._tasks:
                    raise ValueError(f"Task {task.task_id} depends on non-existent task {dep}")
        
        # Cycle detection via DFS
        visited: Dict[str, int] = {} # 0: unvisited, 1: visiting, 2: visited
        for task_id in self._tasks:
            visited[task_id] = 0

        def dfs(node: str):
            visited[node] = 1 # visiting
            for child in self._dependents.get(node, []):
                if visited[child] == 1:
                    raise CyclicDependencyError(f"Cycle detected involving task {child} and {node}")
                if visited[child] == 0:
                    dfs(child)
            visited[node] = 2 # visited

        for task_id in self._tasks:
            if visited[task_id] == 0:
                dfs(task_id)

    def get_ready_tasks(self) -> List[Task]:
        """Returns tasks whose dependencies are all COMPLETED and whose status is PENDING or READY."""
        ready: List[Task] = []
        for task in self._tasks.values():
            if task.status in [TaskStatus.PENDING, TaskStatus.READY, TaskStatus.BLOCKED]:
                deps_ok = True
                for dep_id in task.dependencies:
                    dep_task = self._tasks.get(dep_id)
                    if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                        deps_ok = False
                        break
                if deps_ok:
                    ready.append(task)
        return ready

    def get_execution_layers(self) -> List[List[Task]]:
        """Computes topological execution layers for parallel scheduling."""
        self.validate_graph()
        in_degree: Dict[str, int] = {t_id: len(t.dependencies) for t_id, t in self._tasks.items()}
        current_layer = [self._tasks[t_id] for t_id, deg in in_degree.items() if deg == 0]
        layers: List[List[Task]] = []

        while current_layer:
            layers.append(current_layer)
            next_layer = []
            for task in current_layer:
                for child_id in self._dependents.get(task.task_id, []):
                    in_degree[child_id] -= 1
                    if in_degree[child_id] == 0:
                        next_layer.append(self._tasks[child_id])
            current_layer = next_layer
        return layers
