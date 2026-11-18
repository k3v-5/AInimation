"""
UAF-81.84.4: VFX Graph DAG Execution and Sub-Emitter Wiring.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Set

from ..emitter.emitter import VFXEmitter
from ..emitter.particle import Particle
from ..models.definition import VFXGraphCycleError
from .events import VFXEvent, VFXEventBus


class VFXGraphNode:
    """A stage node in the VFX execution directed acyclic graph (DAG)."""

    def __init__(self, node_id: str, stage_name: str, execute_fn: Optional[Callable[..., Any]] = None):
        self.node_id = node_id
        self.stage_name = stage_name
        self.execute_fn = execute_fn
        self.dependencies: Set[str] = set()

    def add_dependency(self, parent_node_id: str) -> None:
        self.dependencies.add(parent_node_id)


class SubEmitterBinding:
    """Wires an event from a parent emitter to trigger child emitter bursts."""

    def __init__(
        self,
        parent_emitter_id: str,
        trigger_event: str,  # e.g. "OnCollision", "OnDeath"
        child_emitter: VFXEmitter,
        spawn_count: int = 15,
    ):
        self.parent_emitter_id = parent_emitter_id
        self.trigger_event = trigger_event
        self.child_emitter = child_emitter
        self.spawn_count = spawn_count

    def on_event(self, event: VFXEvent) -> None:
        if event.payload.get("emitter_id") == self.parent_emitter_id:
            # Re-position child emitter at impact point if specified
            if "position" in event.payload:
                self.child_emitter.config = self.child_emitter.config.__class__(
                    **{**self.child_emitter.config.__dict__, "initial_position": event.payload["position"]}
                )
            self.child_emitter.spawn(self.spawn_count)


class VFXGraph:
    """Directed Acyclic Graph orchestrating execution stages and sub-emitters."""

    def __init__(self):
        self.nodes: Dict[str, VFXGraphNode] = {}
        self.sub_emitters: List[SubEmitterBinding] = []
        self.event_bus = VFXEventBus()

    def add_node(self, node: VFXGraphNode) -> None:
        self.nodes[node.node_id] = node

    def add_sub_emitter(self, binding: SubEmitterBinding) -> None:
        self.sub_emitters.append(binding)
        self.event_bus.subscribe(binding.trigger_event, binding.on_event)

    def topological_sort(self) -> List[str]:
        """
        Compute deterministic topological sort of DAG nodes.
        Raises VFXGraphCycleError if cycles are detected.
        """
        # Kahn's algorithm or DFS
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}

        for nid, node in self.nodes.items():
            for dep in node.dependencies:
                if dep in self.nodes:
                    adj[dep].append(nid)
                    in_degree[nid] += 1

        # Queue nodes with 0 dependencies, sorted by id for determinism
        queue = sorted([nid for nid in in_degree if in_degree[nid] == 0])
        ordered: List[str] = []

        while queue:
            curr = queue.pop(0)
            ordered.append(curr)
            for neighbor in sorted(adj[curr]):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
            queue.sort()

        if len(ordered) != len(self.nodes):
            raise VFXGraphCycleError(
                f"Cycle detected in VFX Graph! Resolved {len(ordered)} of {len(self.nodes)} nodes."
            )

        return ordered

    def execute(self, context: Any = None) -> None:
        """Execute all nodes in DAG order."""
        ordered_ids = self.topological_sort()
        for nid in ordered_ids:
            node = self.nodes[nid]
            if node.execute_fn:
                node.execute_fn(context)
        # Dispatch queued events
        self.event_bus.dispatch_all()
