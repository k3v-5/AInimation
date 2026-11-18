from typing import Optional, Dict, Any
from ...golden import GoldenAPI, GoldenAsset

class GoldenAssetBridge:
    """Bridges Strategy Learning to F76 Golden Assets & Baselines."""

    def __init__(self, golden_api: Optional[GoldenAPI] = None):
        self.golden = golden_api or GoldenAPI()

    def get_golden(self, semantic_id: str) -> Optional[GoldenAsset]:
        return self.golden.get_active_golden(semantic_id)

    def check_regression(self, semantic_id: str, new_score: float) -> bool:
        golden = self.get_golden(semantic_id)
        if not golden:
            return False
        delta = new_score - golden.baseline_score
        return delta < -0.05
