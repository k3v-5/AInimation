"""
UAF-81.90: Mission Graph Directed Acyclic Graph (DAG) and Objective Management.
Provides branching quest flow, AND/OR prerequisite gates, spatial volume triggers,
and automated cycle detection via Kahn's algorithm.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple, Any
from pydantic import BaseModel, Field

from uaf.level_design.core.contracts import (
    ObjectiveType,
    ObjectiveState,
    DependencyType,
)


class MissionCycleError(Exception):
    """Raised when a circular dependency is detected in the mission graph."""
    pass


class VolumeTrigger(BaseModel):
    """Spatial 3D volume trigger associated with an objective or event."""
    trigger_id: str
    center_pos: Tuple[float, float, float]
    box_extent: Tuple[float, float, float] = (200.0, 200.0, 150.0)  # Unreal centimeters
    event_on_enter: str = "OnObjectiveVolumeEntered"
    event_on_exit: str = "OnObjectiveVolumeExited"


class MissionNode(BaseModel):
    """Discrete node in the mission quest DAG."""
    node_id: str
    name: str
    description: str = ""
    objective_type: ObjectiveType
    state: ObjectiveState = ObjectiveState.NOT_STARTED
    prerequisites: List[str] = Field(default_factory=list)
    dependency_logic: DependencyType = DependencyType.ALL_REQUIRED
    target_coord: Optional[Tuple[int, ...]] = None
    world_pos: Optional[Tuple[float, float, float]] = None
    trigger: Optional[VolumeTrigger] = None
    is_optional: bool = False
    reward_xp: int = 100
    reward_items: List[str] = Field(default_factory=list)
    custom_properties: Dict[str, Any] = Field(default_factory=dict)


class MissionGraph(BaseModel):
    """
    Directed Acyclic Graph (DAG) managing dynamic mission progression.
    Guarantees acyclicity, evaluates AND/OR preconditions, and tracks runtime states.
    """
    mission_id: str
    mission_title: str
    nodes: Dict[str, MissionNode] = Field(default_factory=dict)

    def add_node(self, node: MissionNode) -> None:
        """Adds a mission objective node and validates DAG acyclicity."""
        if node.node_id in self.nodes:
            raise ValueError(f"Objective node '{node.node_id}' already exists in mission graph")
        self.nodes[node.node_id] = node
        self.validate_dag()

    def add_dependency(self, child_id: str, parent_id: str) -> None:
        """Adds prerequisite dependency: parent_id must complete before child_id."""
        if child_id not in self.nodes:
            raise KeyError(f"Child node '{child_id}' not found in mission graph")
        if parent_id not in self.nodes:
            raise KeyError(f"Parent node '{parent_id}' not found in mission graph")

        child = self.nodes[child_id]
        if parent_id not in child.prerequisites:
            child.prerequisites.append(parent_id)
            self.validate_dag()

    def validate_dag(self) -> List[str]:
        """
        Validates that the mission graph has no circular dependencies using Kahn's algorithm.
        Returns topological ordering of node IDs if valid.
        Raises MissionCycleError if a cycle is detected.
        """
        in_degree: Dict[str, int] = {node_id: 0 for node_id in self.nodes}
        adjacency: Dict[str, List[str]] = {node_id: [] for node_id in self.nodes}

        for node_id, node in self.nodes.items():
            for prereq in node.prerequisites:
                if prereq in adjacency:
                    adjacency[prereq].append(node_id)
                    in_degree[node_id] += 1

        queue: List[str] = [node_id for node_id, deg in in_degree.items() if deg == 0]
        topological_order: List[str] = []

        while queue:
            curr = queue.pop(0)
            topological_order.append(curr)

            for neighbor in adjacency[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(topological_order) != len(self.nodes):
            unresolved = [k for k, v in in_degree.items() if v > 0]
            raise MissionCycleError(f"Mission graph contains a cycle involving nodes: {unresolved}")

        return topological_order

    def get_ready_objectives(self) -> List[MissionNode]:
        """
        Returns all objectives currently in NOT_STARTED state whose prerequisite
        conditions (AND / OR) are satisfied.
        """
        ready: List[MissionNode] = []
        for node in self.nodes.values():
            if node.state != ObjectiveState.NOT_STARTED:
                continue

            if not node.prerequisites:
                ready.append(node)
                continue

            completed_prereqs = [
                self.nodes[p].state == ObjectiveState.COMPLETED
                for p in node.prerequisites
                if p in self.nodes
            ]

            if node.dependency_logic == DependencyType.ALL_REQUIRED:
                if all(completed_prereqs):
                    ready.append(node)
            elif node.dependency_logic == DependencyType.ANY_REQUIRED:
                if any(completed_prereqs):
                    ready.append(node)

        return ready

    def start_objective(self, node_id: str) -> None:
        """Transitions an objective from NOT_STARTED to IN_PROGRESS."""
        if node_id not in self.nodes:
            raise KeyError(f"Objective '{node_id}' not found")
        node = self.nodes[node_id]
        if node.state != ObjectiveState.NOT_STARTED:
            raise ValueError(f"Cannot start objective '{node_id}' in state '{node.state}'")
        node.state = ObjectiveState.IN_PROGRESS

    def complete_objective(self, node_id: str) -> List[MissionNode]:
        """
        Marks an objective as COMPLETED.
        Automatically starts newly unlocked objectives that have all prerequisites met.
        Returns list of newly ready objectives.
        """
        if node_id not in self.nodes:
            raise KeyError(f"Objective '{node_id}' not found")

        node = self.nodes[node_id]
        node.state = ObjectiveState.COMPLETED
        return self.get_ready_objectives()

    def fail_objective(self, node_id: str) -> None:
        """Marks an objective as FAILED."""
        if node_id not in self.nodes:
            raise KeyError(f"Objective '{node_id}' not found")
        self.nodes[node_id].state = ObjectiveState.FAILED

    def is_mission_complete(self) -> bool:
        """
        Returns True if all required (non-optional) objectives are COMPLETED.
        """
        for node in self.nodes.values():
            if not node.is_optional and node.state != ObjectiveState.COMPLETED:
                return False
        return True

    def to_ue5_export_dict(self) -> Dict[str, Any]:
        """Exports mission graph data in format consumable by UE5 UDataAsset / UAFBridge."""
        return {
            "mission_id": self.mission_id,
            "mission_title": self.mission_title,
            "is_complete": self.is_mission_complete(),
            "nodes": [
                {
                    "node_id": n.node_id,
                    "name": n.name,
                    "description": n.description,
                    "objective_type": n.objective_type.value,
                    "state": n.state.value,
                    "prerequisites": n.prerequisites,
                    "dependency_logic": n.dependency_logic.value,
                    "target_coord": list(n.target_coord) if n.target_coord else None,
                    "world_pos": list(n.world_pos) if n.world_pos else None,
                    "trigger": n.trigger.model_dump() if n.trigger else None,
                    "is_optional": n.is_optional,
                    "reward_xp": n.reward_xp,
                    "reward_items": n.reward_items,
                    "custom_properties": n.custom_properties,
                }
                for n in self.nodes.values()
            ],
        }
