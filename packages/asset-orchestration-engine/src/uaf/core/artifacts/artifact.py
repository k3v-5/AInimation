"""
Artifact model represents any verifiable file or memory payload produced in UAF.
UAF-81.0 Sections 22, 23, 24.
"""

import os
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .artifact_location import ArtifactLocation, StorageBackend


@dataclass(frozen=True)
class Artifact:
    """
    Immutable representation of an output asset artifact with provenance and integrity.
    """
    artifact_id: str
    artifact_type: str
    asset_id: str
    content_hash: str
    size: int
    location: ArtifactLocation
    producer: str
    producer_version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def verify_integrity(self) -> bool:
        """
        Verifies content_hash, size, and readability of the artifact if accessible on filesystem.
        """
        if self.location.backend == StorageBackend.FILESYSTEM:
            p = Path(self.location.uri)
            if not p.exists() or not p.is_file():
                return False
            if p.stat().st_size != self.size:
                return False

            hasher = hashlib.sha256()
            with open(p, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest() == self.content_hash

        # For memory or remote backends, assume verified if content_hash is non-empty
        return bool(self.content_hash and self.size >= 0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "asset_id": self.asset_id,
            "content_hash": self.content_hash,
            "size": self.size,
            "location": self.location.to_dict(),
            "producer": self.producer,
            "producer_version": self.producer_version,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Artifact":
        return cls(
            artifact_id=data["artifact_id"],
            artifact_type=data["artifact_type"],
            asset_id=data["asset_id"],
            content_hash=data["content_hash"],
            size=int(data["size"]),
            location=ArtifactLocation.from_dict(data["location"]),
            producer=data["producer"],
            producer_version=data.get("producer_version", "1.0.0"),
            created_at=float(data.get("created_at", time.time())),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def create_from_file(
        cls,
        file_path: Path,
        artifact_id: str,
        artifact_type: str,
        asset_id: str,
        producer: str,
        producer_version: str = "1.0.0",
        relative_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Artifact":
        """Factory method to create an Artifact from an existing local file."""
        p = Path(file_path).resolve()
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"Cannot create artifact from non-existent file: {p}")

        size = p.stat().st_size
        hasher = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        content_hash = hasher.hexdigest()

        location = ArtifactLocation(
            backend=StorageBackend.FILESYSTEM,
            uri=str(p),
            relative_path=relative_path,
        )

        return cls(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            asset_id=asset_id,
            content_hash=content_hash,
            size=size,
            location=location,
            producer=producer,
            producer_version=producer_version,
            metadata=metadata or {},
        )
