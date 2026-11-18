"""Build and artifact manifest representations with SHA-256 cryptographic verification."""

from __future__ import annotations
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ArtifactEntry:
    artifact_path: str
    artifact_type: str  # "executable", "library", "package", "config", "symbols", "report"
    size_bytes: int
    sha256_hash: str


@dataclass
class BuildManifest:
    build_id: str = field(default_factory=lambda: f"bld_{uuid.uuid4().hex[:10]}")
    commit: str = "HEAD"
    engine_version: str = "5.4.0"
    uaf_version: str = "81.88.0"
    bridge_version: str = "1.0.0"
    asset_revision: int = 1
    content_hash: str = ""
    binary_hash: str = ""
    configuration: str = "Shipping"
    platform: str = "Windows"
    timestamp_utc: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def to_dict(self) -> Dict[str, Any]:
        return vars(self)


@dataclass
class ArtifactManifest:
    build_id: str
    artifacts: List[ArtifactEntry] = field(default_factory=list)

    def add_artifact(self, path: str, artifact_type: str, content_bytes: bytes) -> ArtifactEntry:
        h = hashlib.sha256(content_bytes).hexdigest()
        entry = ArtifactEntry(
            artifact_path=path,
            artifact_type=artifact_type,
            size_bytes=len(content_bytes),
            sha256_hash=h,
        )
        self.artifacts.append(entry)
        return entry

    def verify_all_hashes(self, content_provider: Dict[str, bytes]) -> bool:
        for a in self.artifacts:
            raw = content_provider.get(a.artifact_path)
            if raw is None:
                return False
            if hashlib.sha256(raw).hexdigest() != a.sha256_hash:
                return False
        return True
