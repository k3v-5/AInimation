"""
SemanticAsset provides the universal structured semantic representation of any asset.
UAF-81.1 Sections 4 to 12.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.identity.asset_identity import AssetIdentity
from ...core.hashing.canonical_hasher import CanonicalHasher
from .complexity_level import ComplexityLevel


@dataclass
class SemanticAsset:
    """
    Universal semantic model expressing asset intent, structure, appearance, and constraints
    without binding to any specific DCC software, modifier, or tool.
    """
    identity: AssetIdentity
    intent: Dict[str, Any] = field(default_factory=dict)
    structure: Dict[str, Any] = field(default_factory=dict)
    appearance: Dict[str, Any] = field(default_factory=dict)
    behavior: Dict[str, Any] = field(default_factory=dict)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    quality: Dict[str, Any] = field(default_factory=dict)
    target: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    complexity_level: ComplexityLevel = ComplexityLevel.C2_GAME_READY

    @property
    def intent_hash(self) -> str:
        """Computes the canonical hash of purely user/designer intent."""
        return CanonicalHasher.compute_hash({
            "identity": self.identity.to_dict(),
            "intent": self.intent,
            "complexity_level": self.complexity_level.value,
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "intent": self.intent,
            "structure": self.structure,
            "appearance": self.appearance,
            "behavior": self.behavior,
            "constraints": self.constraints,
            "dependencies": self.dependencies,
            "quality": self.quality,
            "target": self.target,
            "provenance": self.provenance,
            "complexity_level": self.complexity_level.value,
            "intent_hash": self.intent_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticAsset":
        return cls(
            identity=AssetIdentity.from_dict(data["identity"]),
            intent=data.get("intent", {}),
            structure=data.get("structure", {}),
            appearance=data.get("appearance", {}),
            behavior=data.get("behavior", {}),
            constraints=data.get("constraints", []),
            dependencies=data.get("dependencies", []),
            quality=data.get("quality", {}),
            target=data.get("target", {}),
            provenance=data.get("provenance", {}),
            complexity_level=ComplexityLevel.from_str(data.get("complexity_level", "C2")),
        )
