"""
GenerationPlan encapsulates the complete DAG of operations, nodes, and resources scheduled for asset production.
UAF-81.2 Sections 20, 21, 55, 62, 63.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .plan_node import GenerationPlanNode
from ...core.hashing.canonical_hasher import CanonicalHasher
from ...intelligence.dependencies.dependency_graph import DependencyGraph


@dataclass
class GenerationPlan:
    """
    Immutable production blueprint scheduled for execution.
    """
    plan_id: str
    asset_id: str
    strategy_id: str
    specification_hash: str
    nodes: Dict[str, GenerationPlanNode] = field(default_factory=dict)
    execution_order: List[str] = field(default_factory=list)
    estimated_cost: float = 0.5
    expected_quality: float = 0.8
    risks: List[str] = field(default_factory=list)
    fallbacks: Dict[str, List[str]] = field(default_factory=dict)
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def plan_hash(self) -> str:
        """Computes the canonical SHA-256 hash of the planned generation DAG."""
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "asset_id": self.asset_id,
            "strategy_id": self.strategy_id,
            "specification_hash": self.specification_hash,
            "nodes": {k: v.to_dict() for k, v in sorted(self.nodes.items())},
            "execution_order": self.execution_order,
            "estimated_cost": self.estimated_cost,
            "expected_quality": self.expected_quality,
            "risks": self.risks,
            "fallbacks": self.fallbacks,
            "version": self.version,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationPlan":
        nodes = {k: GenerationPlanNode.from_dict(v) for k, v in data.get("nodes", {}).items()}
        return cls(
            plan_id=data["plan_id"],
            asset_id=data["asset_id"],
            strategy_id=data["strategy_id"],
            specification_hash=data["specification_hash"],
            nodes=nodes,
            execution_order=data.get("execution_order", []),
            estimated_cost=float(data.get("estimated_cost", 0.5)),
            expected_quality=float(data.get("expected_quality", 0.8)),
            risks=data.get("risks", []),
            fallbacks=data.get("fallbacks", {}),
            version=data.get("version", "1.0.0"),
            created_at=float(data.get("created_at", time.time())),
            metadata=data.get("metadata", {}),
        )
