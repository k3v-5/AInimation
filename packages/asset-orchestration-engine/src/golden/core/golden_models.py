import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .golden_types import GoldenAssetStatus

@dataclass
class GoldenAsset:
    golden_id: str
    semantic_id: str
    asset_name: str
    asset_type: str = "weapon"
    version: int = 1
    source_asset_id: Optional[str] = None
    source_path: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    created_by: str = "agent.strategy"
    status: GoldenAssetStatus = GoldenAssetStatus.DRAFT
    fingerprint: Dict[str, str] = field(default_factory=dict)
    evaluation_id: Optional[str] = None
    baseline_score: float = 0.0
    minimum_acceptable_score: float = 0.85
    manifest_hash: str = ""
    parent_golden_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.manifest_hash:
            self.manifest_hash = self.compute_manifest_hash()

    def compute_manifest_hash(self) -> str:
        data = {
            "golden_id": self.golden_id,
            "semantic_id": self.semantic_id,
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
            "version": self.version,
            "source_asset_id": self.source_asset_id,
            "fingerprint": {k: self.fingerprint[k] for k in sorted(self.fingerprint.keys())},
            "baseline_score": round(self.baseline_score, 4),
            "minimum_acceptable_score": round(self.minimum_acceptable_score, 4),
            "parent_golden_id": self.parent_golden_id
        }
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        return self.compute_manifest_hash() == self.manifest_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "golden_id": self.golden_id,
            "semantic_id": self.semantic_id,
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
            "version": self.version,
            "source_asset_id": self.source_asset_id,
            "source_path": self.source_path,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "status": self.status.value,
            "fingerprint": self.fingerprint,
            "evaluation_id": self.evaluation_id,
            "baseline_score": round(self.baseline_score, 4),
            "minimum_acceptable_score": round(self.minimum_acceptable_score, 4),
            "manifest_hash": self.manifest_hash,
            "parent_golden_id": self.parent_golden_id,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoldenAsset":
        return cls(
            golden_id=data["golden_id"],
            semantic_id=data["semantic_id"],
            asset_name=data.get("asset_name", ""),
            asset_type=data.get("asset_type", "weapon"),
            version=data.get("version", 1),
            source_asset_id=data.get("source_asset_id"),
            source_path=data.get("source_path"),
            created_at=data.get("created_at", time.time()),
            created_by=data.get("created_by", "agent.strategy"),
            status=GoldenAssetStatus(data.get("status", "DRAFT")),
            fingerprint=data.get("fingerprint", {}),
            evaluation_id=data.get("evaluation_id"),
            baseline_score=data.get("baseline_score", 0.0),
            minimum_acceptable_score=data.get("minimum_acceptable_score", 0.85),
            manifest_hash=data.get("manifest_hash", ""),
            parent_golden_id=data.get("parent_golden_id"),
            metadata=data.get("metadata", {})
        )
