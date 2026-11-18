"""
Checkpoint encapsulates an immutable snapshot of execution state and generated artifacts.
UAF-81.0 Section 39.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..artifacts.artifact import Artifact


@dataclass(frozen=True)
class Checkpoint:
    """
    Immutable checkpoint model for state recovery and checkpointing.
    """
    checkpoint_id: str
    production_id: str
    operation_id: str
    state: Dict[str, Any]
    artifacts: List[Dict[str, Any]]
    input_hash: str
    configuration_hash: str
    generator_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "production_id": self.production_id,
            "operation_id": self.operation_id,
            "state": self.state,
            "artifacts": self.artifacts,
            "input_hash": self.input_hash,
            "configuration_hash": self.configuration_hash,
            "generator_version": self.generator_version,
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        return cls(
            checkpoint_id=data["checkpoint_id"],
            production_id=data["production_id"],
            operation_id=data["operation_id"],
            state=data.get("state", {}),
            artifacts=data.get("artifacts", []),
            input_hash=data["input_hash"],
            configuration_hash=data["configuration_hash"],
            generator_version=data.get("generator_version", "1.0.0"),
            schema_version=data.get("schema_version", "1.0.0"),
            created_at=float(data.get("created_at", time.time())),
            metadata=data.get("metadata", {}),
        )
