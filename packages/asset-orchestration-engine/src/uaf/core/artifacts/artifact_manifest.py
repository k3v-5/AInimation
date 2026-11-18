"""
ArtifactManifest provides lineage and dependency graph linking assets, operations, and artifacts.
UAF-81.0 Sections 25, 26.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .artifact import Artifact


@dataclass
class ArtifactManifest:
    """
    Provenance manifest containing the graph of generated artifacts and dependencies.
    """
    manifest_id: str
    asset_id: str
    production_id: str
    schema_version: str = "1.0.0"
    artifacts: List[Artifact] = field(default_factory=list)
    operations: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    consumed_by: List[str] = field(default_factory=list)
    derived_from: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_artifact(self, artifact: Artifact) -> None:
        self.artifacts.append(artifact)

    def verify_all_artifacts(self) -> bool:
        """Verify integrity of all contained artifacts."""
        return all(artifact.verify_integrity() for artifact in self.artifacts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "asset_id": self.asset_id,
            "production_id": self.production_id,
            "schema_version": self.schema_version,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "operations": self.operations,
            "depends_on": self.depends_on,
            "consumed_by": self.consumed_by,
            "derived_from": self.derived_from,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArtifactManifest":
        artifacts = [Artifact.from_dict(a) for a in data.get("artifacts", [])]
        return cls(
            manifest_id=data["manifest_id"],
            asset_id=data["asset_id"],
            production_id=data["production_id"],
            schema_version=data.get("schema_version", "1.0.0"),
            artifacts=artifacts,
            operations=data.get("operations", []),
            depends_on=data.get("depends_on", []),
            consumed_by=data.get("consumed_by", []),
            derived_from=data.get("derived_from", []),
            created_at=float(data.get("created_at", time.time())),
            metadata=data.get("metadata", {}),
        )
