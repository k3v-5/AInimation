"""
ExecutionContext encapsulates the immutable parameters and resources allocated for an operation.
UAF-81.0 Sections 9, 10.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .project_context import ProjectContext
from .resource_budget import ResourceBudget


@dataclass(frozen=True)
class ExecutionContext:
    """
    Immutable execution context for an operation.
    Guarantees operation determinism and isolation.
    """
    production_id: str
    operation_id: str
    asset_id: str
    project_context: ProjectContext
    seed: int = 42
    target: str = "generic"
    quality_profile: str = "production"
    configuration: Dict[str, Any] = field(default_factory=dict)
    permissions: Dict[str, bool] = field(default_factory=lambda: {"read": True, "write": True, "network": False})
    resource_budget: ResourceBudget = field(default_factory=ResourceBudget)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "production_id": self.production_id,
            "operation_id": self.operation_id,
            "asset_id": self.asset_id,
            "project_context": self.project_context.to_dict(),
            "seed": self.seed,
            "target": self.target,
            "quality_profile": self.quality_profile,
            "configuration": self.configuration,
            "permissions": self.permissions,
            "resource_budget": self.resource_budget.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionContext":
        return cls(
            production_id=data["production_id"],
            operation_id=data["operation_id"],
            asset_id=data["asset_id"],
            project_context=ProjectContext.from_dict(data["project_context"]),
            seed=int(data.get("seed", 42)),
            target=data.get("target", "generic"),
            quality_profile=data.get("quality_profile", "production"),
            configuration=data.get("configuration", {}),
            permissions=data.get("permissions", {"read": True, "write": True, "network": False}),
            resource_budget=ResourceBudget.from_dict(data.get("resource_budget", {})),
        )
