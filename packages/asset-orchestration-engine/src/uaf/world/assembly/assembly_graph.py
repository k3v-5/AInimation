"""
AssemblyGraph and AssemblyNode models for discrete modular level construction.
UAF-81.6 Sections 14, 15.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Set
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class AssemblyNode:
    instance_id: str
    module_id: str
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    connected_edges: Dict[str, Tuple[str, str]] = field(default_factory=dict)  # my_conn -> (other_instance_id, other_conn_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "module_id": self.module_id,
            "position": self.position,
            "rotation": self.rotation,
            "connected_edges": {k: list(v) for k, v in self.connected_edges.items()},
        }


@dataclass
class AssemblyGraph:
    nodes: Dict[str, AssemblyNode] = field(default_factory=dict)

    def add_node(
        self,
        instance_id: str,
        module_id: str,
        position: List[float],
        rotation: Optional[List[float]] = None,
    ) -> AssemblyNode:
        rot = rotation or [0.0, 0.0, 0.0]
        node = AssemblyNode(instance_id=instance_id, module_id=module_id, position=position, rotation=rot)
        self.nodes[instance_id] = node
        return node

    def connect(self, from_id: str, from_conn: str, to_id: str, to_conn: str) -> None:
        if from_id in self.nodes and to_id in self.nodes:
            self.nodes[from_id].connected_edges[from_conn] = (to_id, to_conn)
            self.nodes[to_id].connected_edges[to_conn] = (from_id, from_conn)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    def check_overlaps(self, tolerance_meters: float = 0.1) -> List[Tuple[str, str]]:
        """Detects coincident overlapping module instances."""
        overlaps = []
        node_list = list(self.nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                n1, n2 = node_list[i], node_list[j]
                # If exact position match
                dx = abs(n1.position[0] - n2.position[0])
                dy = abs(n1.position[1] - n2.position[1])
                dz = abs(n1.position[2] - n2.position[2])
                if dx < tolerance_meters and dy < tolerance_meters and dz < tolerance_meters:
                    overlaps.append((n1.instance_id, n2.instance_id))
        return overlaps

    @property
    def assembly_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {k: v.to_dict() for k, v in sorted(self.nodes.items())},
            "node_count": self.node_count,
        }
