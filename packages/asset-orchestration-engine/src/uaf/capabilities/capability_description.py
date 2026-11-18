"""
CapabilityDescription formalizes what a generator, tool, or engine component can execute.
UAF-81.0 Section 53.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Union
from ..core.identity.asset_types import AssetType
from ..core.operations.operation_types import OperationType


@dataclass(frozen=True)
class CapabilityDescription:
    """
    Metadata declaring supported asset types, targets, operations, and quality profiles.
    """
    capability_id: str
    version: str = "1.0.0"
    asset_types: List[AssetType] = field(default_factory=list)
    operations: List[OperationType] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    limitations: Dict[str, Any] = field(default_factory=dict)
    quality_profiles: List[str] = field(default_factory=lambda: ["preview", "production", "cinematic"])
    targets: List[str] = field(default_factory=lambda: ["generic"])

    def supports_asset_type(self, asset_type: Union[AssetType, str]) -> bool:
        at = AssetType.from_str(asset_type) if isinstance(asset_type, str) else asset_type
        return at in self.asset_types

    def supports_operation(self, operation: Union[OperationType, str]) -> bool:
        op = OperationType.from_str(operation) if isinstance(operation, str) else operation
        return op in self.operations

    def supports_target(self, target: str) -> bool:
        return target.strip().lower() in [t.strip().lower() for t in self.targets]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "version": self.version,
            "asset_types": [at.value for at in self.asset_types],
            "operations": [op.value for op in self.operations],
            "requirements": self.requirements,
            "limitations": self.limitations,
            "quality_profiles": self.quality_profiles,
            "targets": self.targets,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CapabilityDescription":
        return cls(
            capability_id=data["capability_id"],
            version=data.get("version", "1.0.0"),
            asset_types=[AssetType.from_str(at) for at in data.get("asset_types", [])],
            operations=[OperationType.from_str(op) for op in data.get("operations", [])],
            requirements=data.get("requirements", {}),
            limitations=data.get("limitations", {}),
            quality_profiles=data.get("quality_profiles", ["preview", "production"]),
            targets=data.get("targets", ["generic"]),
        )
