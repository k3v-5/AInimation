import hashlib
import json
from typing import Dict, Any, List

class EvaluationHasher:
    @classmethod
    def compute_evaluation_hash(
        cls,
        global_score: float,
        category_scores: Dict[str, Any],
        defects: List[Any],
        acceptance_status: str
    ) -> str:
        data = {
            "global_score": round(global_score, 4),
            "categories": {
                k: round(v.score, 4) if hasattr(v, "score") else round(float(v), 4)
                for k, v in sorted(category_scores.items())
            },
            "defects": [
                {
                    "type": d.defect_type.value if hasattr(d.defect_type, "value") else str(d.defect_type),
                    "region": d.region,
                    "severity": d.severity.value if hasattr(d.severity, "value") else str(d.severity)
                } for d in defects
            ],
            "acceptance": acceptance_status
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
