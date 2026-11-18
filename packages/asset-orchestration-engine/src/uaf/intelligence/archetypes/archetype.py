"""
AssetArchetype defines functional classes of assets with baseline parameters and profiles.
UAF-81.1 Sections 14, 15.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.identity.asset_types import AssetType


@dataclass(frozen=True)
class AssetArchetype:
    """
    Contract defining parameter requirements, baseline constraints, and default profiles for an asset archetype.
    """
    archetype_id: str
    asset_type: AssetType
    description: str = ""
    required_parameters: List[str] = field(default_factory=list)
    optional_parameters: List[str] = field(default_factory=list)
    default_parameters: Dict[str, Any] = field(default_factory=dict)
    default_constraints: List[Dict[str, Any]] = field(default_factory=list)
    default_profiles: Dict[str, str] = field(default_factory=dict)
    supported_targets: List[str] = field(default_factory=lambda: ["generic"])
    supported_quality_profiles: List[str] = field(default_factory=lambda: ["preview", "production", "cinematic"])
    required_capabilities: List[str] = field(default_factory=list)

    def validate_parameters(self, params: Dict[str, Any]) -> List[str]:
        """Returns list of missing required parameter names."""
        missing = [p for p in self.required_parameters if p not in params and p not in self.default_parameters]
        return missing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "archetype_id": self.archetype_id,
            "asset_type": self.asset_type.value,
            "description": self.description,
            "required_parameters": self.required_parameters,
            "optional_parameters": self.optional_parameters,
            "default_parameters": self.default_parameters,
            "default_constraints": self.default_constraints,
            "default_profiles": self.default_profiles,
            "supported_targets": self.supported_targets,
            "supported_quality_profiles": self.supported_quality_profiles,
            "required_capabilities": self.required_capabilities,
        }
