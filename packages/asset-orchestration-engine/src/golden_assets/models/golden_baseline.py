import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class GoldenBaseline:
    baseline_id: str
    golden_asset_id: str
    version: str = "1.0.0"
    metrics: Dict[str, Any] = field(default_factory=dict)
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    global_score: float = 0.0
    defects: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    evaluation_id: str = ""
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self.compute_hash()

    def compute_hash(self) -> str:
        data = {
            "baseline_id": self.baseline_id,
            "golden_asset_id": self.golden_asset_id,
            "version": self.version,
            "metrics": self.metrics,
            "dimension_scores": {k: round(v, 4) for k, v in self.dimension_scores.items()},
            "global_score": round(self.global_score, 4),
            "evaluation_id": self.evaluation_id
        }
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        return self.compute_hash() == self.content_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_id": self.baseline_id,
            "golden_asset_id": self.golden_asset_id,
            "version": self.version,
            "metrics": self.metrics,
            "dimension_scores": self.dimension_scores,
            "global_score": round(self.global_score, 4),
            "defects": self.defects,
            "created_at": self.created_at,
            "evaluation_id": self.evaluation_id,
            "content_hash": self.content_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoldenBaseline":
        return cls(
            baseline_id=data["baseline_id"],
            golden_asset_id=data.get("golden_asset_id", ""),
            version=data.get("version", "1.0.0"),
            metrics=data.get("metrics", {}),
            dimension_scores=data.get("dimension_scores", {}),
            global_score=data.get("global_score", 0.0),
            defects=data.get("defects", []),
            created_at=data.get("created_at", time.time()),
            evaluation_id=data.get("evaluation_id", ""),
            content_hash=data.get("content_hash", "")
        )
