"""
AssetSpecification provides the base immutable specification contract for any asset.
UAF-81.0 Sections 13, 14, 15.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..identity.asset_identity import AssetIdentity
from ..hashing.canonical_hasher import CanonicalHasher


@dataclass(frozen=True)
class AssetSpecification:
    """
    Immutable, hashable specification describing the desired asset.
    """
    identity: AssetIdentity
    schema_version: str = "1.0.0"
    target: str = "generic"
    quality_profile: str = "production"
    generation_profile: str = "default"
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    seed: int = 42
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def specification_hash(self) -> str:
        """
        Computes the canonical hash of this specification.
        """
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "schema_version": self.schema_version,
            "target": self.target,
            "quality_profile": self.quality_profile,
            "generation_profile": self.generation_profile,
            "parameters": self.parameters,
            "constraints": self.constraints,
            "dependencies": self.dependencies,
            "seed": self.seed,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetSpecification":
        identity_data = data["identity"]
        identity = AssetIdentity.from_dict(identity_data) if isinstance(identity_data, dict) else identity_data
        return cls(
            identity=identity,
            schema_version=data.get("schema_version", "1.0.0"),
            target=data.get("target", "generic"),
            quality_profile=data.get("quality_profile", "production"),
            generation_profile=data.get("generation_profile", "default"),
            parameters=data.get("parameters", {}),
            constraints=data.get("constraints", {}),
            dependencies=data.get("dependencies", []),
            seed=int(data.get("seed", 42)),
            metadata=data.get("metadata", {}),
        )
