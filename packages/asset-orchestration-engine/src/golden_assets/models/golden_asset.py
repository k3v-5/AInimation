import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from ..core.golden_types import GoldenStatus
from .golden_version import GoldenVersionInfo

@dataclass
class GoldenAsset:
    golden_asset_id: str
    semantic_id: str
    asset_family: str
    category: str
    current_version: str = "1.0.0"
    versions: Dict[str, GoldenVersionInfo] = field(default_factory=dict)
    baselines: Dict[str, str] = field(default_factory=dict)
    status: GoldenStatus = GoldenStatus.GOLDEN
    source_asset: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    approved_at: Optional[float] = None
    approved_by: Optional[str] = None
    content_hash: str = ""
    manifest_hash: str = ""
    baseline_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    successor_id: Optional[str] = None

    def __post_init__(self):
        if not self.manifest_hash or not self.content_hash:
            self.compute_hashes()

    def compute_hashes(self):
        # 1. Content hash based on critical identity & versions
        c_data = {
            "golden_asset_id": self.golden_asset_id,
            "semantic_id": self.semantic_id,
            "asset_family": self.asset_family,
            "category": self.category,
            "current_version": self.current_version,
            "versions": {k: v.to_dict() for k, v in self.versions.items()},
            "baselines": self.baselines,
            "source_asset": self.source_asset
        }
        self.content_hash = hashlib.sha256(json.dumps(c_data, sort_keys=True, default=str).encode("utf-8")).hexdigest()

        # 2. Manifest hash
        m_data = {
            "golden_asset_id": self.golden_asset_id,
            "semantic_id": self.semantic_id,
            "version": self.current_version,
            "status": self.status.value,
            "content_hash": self.content_hash,
            "approved_at": self.approved_at,
            "approved_by": self.approved_by,
            "successor_id": self.successor_id
        }
        self.manifest_hash = hashlib.sha256(json.dumps(m_data, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        prev_content = self.content_hash
        prev_manifest = self.manifest_hash
        self.compute_hashes()
        is_valid = (self.content_hash == prev_content and self.manifest_hash == prev_manifest)
        # Restore in case it was checked
        self.content_hash = prev_content
        self.manifest_hash = prev_manifest
        return is_valid

    def to_dict(self) -> Dict[str, Any]:
        return {
            "golden_asset_id": self.golden_asset_id,
            "semantic_id": self.semantic_id,
            "asset_family": self.asset_family,
            "category": self.category,
            "current_version": self.current_version,
            "versions": {k: v.to_dict() for k, v in self.versions.items()},
            "baselines": self.baselines,
            "status": self.status.value,
            "source_asset": self.source_asset,
            "created_at": self.created_at,
            "approved_at": self.approved_at,
            "approved_by": self.approved_by,
            "content_hash": self.content_hash,
            "manifest_hash": self.manifest_hash,
            "baseline_hash": self.baseline_hash,
            "metadata": self.metadata,
            "successor_id": self.successor_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoldenAsset":
        versions = {
            k: GoldenVersionInfo.from_dict(v)
            for k, v in data.get("versions", {}).items()
        }
        return cls(
            golden_asset_id=data["golden_asset_id"],
            semantic_id=data.get("semantic_id", ""),
            asset_family=data.get("asset_family", "general"),
            category=data.get("category", "prop"),
            current_version=data.get("current_version", "1.0.0"),
            versions=versions,
            baselines=data.get("baselines", {}),
            status=GoldenStatus(data.get("status", "GOLDEN")),
            source_asset=data.get("source_asset"),
            created_at=data.get("created_at", time.time()),
            approved_at=data.get("approved_at"),
            approved_by=data.get("approved_by"),
            content_hash=data.get("content_hash", ""),
            manifest_hash=data.get("manifest_hash", ""),
            baseline_hash=data.get("baseline_hash", ""),
            metadata=data.get("metadata", {}),
            successor_id=data.get("successor_id")
        )
