"""
Capability contracts, categories, preconditions, and guarantees.
UAF-81.2 Sections 5, 6, 10, 11, 13, 14, 15.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.identity.asset_types import AssetType
from ...core.operations.operation_types import OperationType


class CapabilityType(str, Enum):
    GEOMETRY = "GEOMETRY"
    ANATOMY = "ANATOMY"
    FACE = "FACE"
    CLOTHING = "CLOTHING"
    HAIR = "HAIR"
    RIGGING = "RIGGING"
    SKINNING = "SKINNING"
    MATERIAL = "MATERIAL"
    TEXTURE = "TEXTURE"
    UV = "UV"
    ANIMATION = "ANIMATION"
    PHYSICS = "PHYSICS"
    MODULAR_ASSEMBLY = "MODULAR_ASSEMBLY"
    TERRAIN = "TERRAIN"
    VEGETATION = "VEGETATION"
    ENVIRONMENT = "ENVIRONMENT"
    LEVEL = "LEVEL"
    WORLD = "WORLD"
    VFX = "VFX"
    AUDIO = "AUDIO"
    OPTIMIZATION = "OPTIMIZATION"
    VALIDATION = "VALIDATION"
    PACKAGING = "PACKAGING"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"


@dataclass(frozen=True)
class CapabilityContract:
    """
    Formal IO and guarantee contract for a capability.
    """
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    quality_guarantees: Dict[str, Any] = field(default_factory=dict)
    failure_modes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "quality_guarantees": self.quality_guarantees,
            "failure_modes": self.failure_modes,
        }


@dataclass(frozen=True)
class ComprehensiveCapability:
    """
    Granular capability descriptor declaring inputs, outputs, preconditions, limitations, and targets.
    """
    capability_id: str
    name: str
    capability_type: CapabilityType
    version: str = "1.0.0"
    description: str = ""
    asset_types: List[AssetType] = field(default_factory=list)
    operations: List[OperationType] = field(default_factory=lambda: [OperationType.GENERATE])
    contract: CapabilityContract = field(default_factory=CapabilityContract)
    limitations: List[str] = field(default_factory=list)
    quality_levels: List[str] = field(default_factory=lambda: ["preview", "production"])
    targets: List[str] = field(default_factory=lambda: ["generic"])
    determinism: str = "SEEDED_DETERMINISTIC"
    resource_profile: Dict[str, Any] = field(default_factory=dict)
    compatible_with: List[str] = field(default_factory=list)
    incompatible_with: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "capability_type": self.capability_type.value,
            "version": self.version,
            "description": self.description,
            "asset_types": [at.value for at in self.asset_types],
            "operations": [op.value for op in self.operations],
            "contract": self.contract.to_dict(),
            "limitations": self.limitations,
            "quality_levels": self.quality_levels,
            "targets": self.targets,
            "determinism": self.determinism,
            "resource_profile": self.resource_profile,
            "compatible_with": self.compatible_with,
            "incompatible_with": self.incompatible_with,
        }
