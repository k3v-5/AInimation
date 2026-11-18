import hashlib
import json
from typing import Dict, Any, List

class CorrectionHasher:
    @classmethod
    def compute_correction_hash(
        cls,
        asset_id: str,
        actions_applied: List[str],
        param_changes: List[Any],
        status: str
    ) -> str:
        data = {
            "asset_id": asset_id,
            "actions": actions_applied,
            "params": [
                {
                    "id": getattr(p, "parameter_id", ""),
                    "old": getattr(p, "old_value", None),
                    "new": getattr(p, "new_value", None)
                } for p in param_changes
            ],
            "status": status
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
