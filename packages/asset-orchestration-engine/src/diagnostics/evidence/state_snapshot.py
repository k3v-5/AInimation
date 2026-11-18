import hashlib
import json
from typing import Dict, Any, Tuple

class StateSnapshot:
    """Captures and compares asset/scene states before and after operations."""
    
    @staticmethod
    def compute_hash(state: Dict[str, Any]) -> str:
        raw = json.dumps(state, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def diff_states(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        diffs = {}
        all_keys = set(before.keys()).union(set(after.keys()))
        for k in all_keys:
            v_b = before.get(k)
            v_a = after.get(k)
            if v_b != v_a:
                diffs[k] = {"before": v_b, "after": v_a}
        return diffs
