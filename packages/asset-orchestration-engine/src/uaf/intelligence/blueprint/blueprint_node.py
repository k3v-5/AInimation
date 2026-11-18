"""
BlueprintNode represents a discrete structural node in an AssetBlueprint DAG.
UAF-81.1 Section 52.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass(frozen=True)
class BlueprintNode:
    """
    Sub-component production step planned within an AssetBlueprint.
    """
    node_id: str
    node_type: str  # e.g., "body", "head", "clothing", "armor", "skeleton", "material"
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    quality_requirements: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "required_capabilities": self.required_capabilities,
            "quality_requirements": self.quality_requirements,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlueprintNode":
        return cls(
            node_id=data["node_id"],
            node_type=data["node_type"],
            parameters=data.get("parameters", {}),
            dependencies=data.get("dependencies", []),
            required_capabilities=data.get("required_capabilities", []),
            quality_requirements=data.get("quality_requirements", {}),
        )
