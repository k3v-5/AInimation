"""
AssetBuildRecord and GeometrySnapshot provenance tracking.
UAF-81.3 Sections 70, 73.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class AssetBuildRecord:
    asset_id: str
    build_id: str
    specification_hash: str
    generator_versions: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    seed: int = 42
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    @property
    def record_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "build_id": self.build_id,
            "specification_hash": self.specification_hash,
            "generator_versions": self.generator_versions,
            "parameters": self.parameters,
            "seed": self.seed,
            "outputs": self.outputs,
            "validation_results": self.validation_results,
            "warnings": self.warnings,
            "errors": self.errors,
            "created_at": self.created_at,
        }
