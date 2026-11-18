import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class AuditRecord:
    optimization_id: str
    asset_id: str
    baseline_id: str
    profile: str
    selected_candidate_id: Optional[str]
    rejected_candidate_ids: List[str]
    rejection_reasons: Dict[str, str]
    is_committed: bool = False
    is_rolled_back: bool = False
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "optimization_id": self.optimization_id,
            "asset_id": self.asset_id,
            "baseline_id": self.baseline_id,
            "profile": self.profile,
            "selected_candidate_id": self.selected_candidate_id,
            "rejected_candidate_ids": self.rejected_candidate_ids,
            "rejection_reasons": self.rejection_reasons,
            "is_committed": self.is_committed,
            "is_rolled_back": self.is_rolled_back,
            "timestamp": self.timestamp
        }
