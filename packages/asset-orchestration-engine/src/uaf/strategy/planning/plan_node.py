"""
GenerationPlanNode specifies a scheduled step in the generation DAG.
UAF-81.2 Sections 21, 22, 31, 32.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.operations.operation_types import OperationType


@dataclass(frozen=True)
class GenerationPlanNode:
    """
    Executable node within a GenerationPlan DAG.
    """
    node_id: str
    operation: OperationType
    capability: str
    implementation: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    resource_budget: Dict[str, Any] = field(default_factory=dict)
    quality_requirement: Dict[str, Any] = field(default_factory=dict)
    fallbacks: List[str] = field(default_factory=list)
    failure_policy: str = "FALLBACK"  # "RETRY", "FALLBACK", "FAIL_EARLY"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "operation": self.operation.value,
            "capability": self.capability,
            "implementation": self.implementation,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "dependencies": self.dependencies,
            "resource_budget": self.resource_budget,
            "quality_requirement": self.quality_requirement,
            "fallbacks": self.fallbacks,
            "failure_policy": self.failure_policy,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationPlanNode":
        return cls(
            node_id=data["node_id"],
            operation=OperationType.from_str(data.get("operation", "GENERATE")),
            capability=data["capability"],
            implementation=data["implementation"],
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", []),
            dependencies=data.get("dependencies", []),
            resource_budget=data.get("resource_budget", {}),
            quality_requirement=data.get("quality_requirement", {}),
            fallbacks=data.get("fallbacks", []),
            failure_policy=data.get("failure_policy", "FALLBACK"),
        )
