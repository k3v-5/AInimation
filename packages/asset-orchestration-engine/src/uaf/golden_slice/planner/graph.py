"""Generation Directed Acyclic Graph (DAG) and topological resolution."""

from __future__ import annotations
from typing import Dict, List, Set, Optional

from uaf.golden_slice.planner.tasks import GenerationTask, TaskType
from uaf.golden_slice.manifest.models import GoldenSliceManifest


class CyclicDependencyError(Exception):
    """Raised when a cycle is detected in the generation DAG."""
    pass


class GenerationDAG:
    """Manages generation task dependencies and enforces strict topological sequencing."""

    def __init__(self) -> None:
        self._tasks: Dict[str, GenerationTask] = {}
        self._dependents: Dict[str, Set[str]] = {}  # prerequisite -> set of dependents

    @property
    def count(self) -> int:
        return len(self._tasks)

    def add_task(self, task: GenerationTask) -> None:
        self._tasks[task.task_id] = task
        if task.task_id not in self._dependents:
            self._dependents[task.task_id] = set()
        for dep in task.dependencies:
            if dep not in self._dependents:
                self._dependents[dep] = set()
            self._dependents[dep].add(task.task_id)

    def add_dependency(self, dependent_id: str, prerequisite_id: str) -> None:
        if dependent_id in self._tasks and prerequisite_id not in self._tasks[dependent_id].dependencies:
            self._tasks[dependent_id].dependencies.append(prerequisite_id)
        if prerequisite_id not in self._dependents:
            self._dependents[prerequisite_id] = set()
        self._dependents[prerequisite_id].add(dependent_id)

    def get_task(self, task_id: str) -> Optional[GenerationTask]:
        return self._tasks.get(task_id)

    def topological_order(self) -> List[GenerationTask]:
        """Returns tasks sorted in valid execution order using Kahn's algorithm."""
        in_degree: Dict[str, int] = {t_id: len(task.dependencies) for t_id, task in self._tasks.items()}
        queue = [t_id for t_id, deg in in_degree.items() if deg == 0]
        order: List[GenerationTask] = []

        while queue:
            curr = queue.pop(0)
            order.append(self._tasks[curr])
            for dep in self._dependents.get(curr, set()):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        if len(order) != len(self._tasks):
            raise CyclicDependencyError("Cycle detected in generation DAG dependencies!")

        return order

    @classmethod
    def build_standard_dag(cls, manifest: GoldenSliceManifest) -> GenerationDAG:
        """Constructs the canonical production DAG according to Section 7 & 8 specs."""
        dag = cls()

        # Level 1: Foundational assets & systems
        dag.add_task(GenerationTask("world_terrain", TaskType.WORLD_TERRAIN, []))
        dag.add_task(GenerationTask("char_skeleton", TaskType.CHARACTER_SKELETON, []))
        dag.add_task(GenerationTask("vfx_niagara", TaskType.VFX_NIAGARA, []))
        dag.add_task(GenerationTask("audio_spatial", TaskType.AUDIO_SPATIAL, []))

        # Level 2: Dependent on Level 1
        dag.add_task(GenerationTask("world_vegetation", TaskType.WORLD_VEGETATION, ["world_terrain"]))
        dag.add_task(GenerationTask("world_architecture", TaskType.WORLD_ARCHITECTURE, ["world_terrain"]))
        dag.add_task(GenerationTask("char_animation", TaskType.CHARACTER_ANIMATION, ["char_skeleton"]))

        # Level 3: Streaming, AnimBP & AI
        dag.add_task(GenerationTask("world_streaming", TaskType.WORLD_STREAMING, ["world_vegetation", "world_architecture"]))
        dag.add_task(GenerationTask("char_animbp", TaskType.CHARACTER_ANIMBP, ["char_animation"]))
        dag.add_task(GenerationTask("ai_behavior", TaskType.AI_BEHAVIOR, ["world_architecture"]))

        # Level 4: Player & Enemies
        dag.add_task(GenerationTask("char_player", TaskType.CHARACTER_PLAYER, ["char_animbp"]))
        dag.add_task(GenerationTask("char_enemy", TaskType.CHARACTER_ENEMY, ["char_animbp", "ai_behavior"]))

        # Level 5: Gameplay systems
        dag.add_task(GenerationTask("gameplay_combat", TaskType.GAMEPLAY_COMBAT, ["char_player", "char_enemy", "vfx_niagara", "audio_spatial"]))
        dag.add_task(GenerationTask("gameplay_inventory", TaskType.GAMEPLAY_INVENTORY, ["char_player"]))

        # Level 6: UI, Cinematics, Networking, Persistence
        dag.add_task(GenerationTask("ui_hud", TaskType.UI_HUD, ["gameplay_combat", "gameplay_inventory"]))
        dag.add_task(GenerationTask("cinematic_sequencer", TaskType.CINEMATIC_SEQUENCER, ["char_player", "char_enemy", "vfx_niagara"]))
        dag.add_task(GenerationTask("networking_setup", TaskType.NETWORKING_SETUP, ["gameplay_combat"]))
        dag.add_task(GenerationTask("persistence_setup", TaskType.PERSISTENCE_SETUP, ["gameplay_inventory", "world_streaming"]))

        return dag
