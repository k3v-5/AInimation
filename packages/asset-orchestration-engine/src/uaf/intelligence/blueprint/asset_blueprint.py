"""
AssetBlueprint models the structural DAG of sub-components and tasks planned before physical generation.
UAF-81.1 Sections 51, 53, 54.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .blueprint_node import BlueprintNode
from ...core.hashing.canonical_hasher import CanonicalHasher
from ..dependencies.dependency_graph import DependencyGraph


@dataclass
class AssetBlueprint:
    """
    DAG of component nodes required to synthesize an asset.
    """
    blueprint_id: str
    asset_id: str
    nodes: Dict[str, BlueprintNode] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: BlueprintNode) -> None:
        self.nodes[node.node_id] = node

    def build_dependency_graph(self) -> DependencyGraph:
        graph = DependencyGraph()
        for node in self.nodes.values():
            graph.add_node(node.node_id)
            for dep in node.dependencies:
                graph.add_dependency(node.node_id, dep)
        return graph

    def get_execution_order(self) -> List[str]:
        """Returns nodes topologically ordered for sequential or parallel generation."""
        graph = self.build_dependency_graph()
        return graph.topological_sort()

    @property
    def blueprint_hash(self) -> str:
        """Computes the canonical hash of the planned production graph."""
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blueprint_id": self.blueprint_id,
            "asset_id": self.asset_id,
            "nodes": {k: v.to_dict() for k, v in sorted(self.nodes.items())},
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetBlueprint":
        nodes = {k: BlueprintNode.from_dict(v) for k, v in data.get("nodes", {}).items()}
        return cls(
            blueprint_id=data["blueprint_id"],
            asset_id=data["asset_id"],
            nodes=nodes,
            metadata=data.get("metadata", {}),
        )
