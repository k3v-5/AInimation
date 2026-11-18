import hashlib
import json
from typing import Dict, Any, List

class CriticHasher:
    @classmethod
    def compute_critic_hash(
        cls,
        semantic_id: str,
        diagnoses: List[Any],
        root_causes: List[Any],
        plan_id: str,
        recommendation: str
    ) -> str:
        data = {
            "semantic_id": semantic_id,
            "diags": [getattr(d, "diagnosis_id", "") for d in diagnoses],
            "causes": [getattr(c, "cause_id", "") for c in root_causes],
            "plan_id": plan_id,
            "rec": recommendation
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
