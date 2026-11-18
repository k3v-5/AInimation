"""
ResolvedAssetSpecification encapsulates the fully resolved, normalized, and validated specification.
UAF-81.1 Sections 47, 48, 54.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.specification.asset_specification import AssetSpecification
from ...core.hashing.canonical_hasher import CanonicalHasher
from ..constraints.constraint_resolver import ResolutionTraceEntry


@dataclass(frozen=True)
class ResolvedAssetSpecification:
    """
    Immutable post-resolution specification ready for strategy selection and execution.
    """
    original_specification: AssetSpecification
    resolved_parameters: Dict[str, Any]
    resolved_dependencies: List[str]
    resolved_constraints: List[Dict[str, Any]]
    required_capabilities: List[str]
    effective_quality_profile: str
    effective_target_profile: str
    resolution_trace: List[Dict[str, Any]] = field(default_factory=list)
    blueprint_hash: Optional[str] = None

    @property
    def intent_hash(self) -> str:
        return self.original_specification.specification_hash

    @property
    def resolved_specification_hash(self) -> str:
        """Computes the canonical hash of the resolved state."""
        return CanonicalHasher.compute_hash({
            "resolved_parameters": self.resolved_parameters,
            "resolved_dependencies": self.resolved_dependencies,
            "required_capabilities": self.required_capabilities,
            "effective_quality_profile": self.effective_quality_profile,
            "effective_target_profile": self.effective_target_profile,
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_specification": self.original_specification.to_dict(),
            "resolved_parameters": self.resolved_parameters,
            "resolved_dependencies": self.resolved_dependencies,
            "resolved_constraints": self.resolved_constraints,
            "required_capabilities": self.required_capabilities,
            "effective_quality_profile": self.effective_quality_profile,
            "effective_target_profile": self.effective_target_profile,
            "resolution_trace": self.resolution_trace,
            "intent_hash": self.intent_hash,
            "resolved_specification_hash": self.resolved_specification_hash,
            "blueprint_hash": self.blueprint_hash,
        }
