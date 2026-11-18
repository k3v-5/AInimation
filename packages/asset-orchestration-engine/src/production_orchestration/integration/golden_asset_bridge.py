from typing import Optional, Tuple
from ...golden import GoldenAPI, GoldenAsset

class GoldenAssetBridge:
    """Integrates with F76 Golden Assets / Regression Baselines."""

    def __init__(self, golden_api: Optional[GoldenAPI] = None):
        self.golden = golden_api or GoldenAPI()

    def check_regression(self, semantic_id: str, candidate_score: float) -> Tuple[bool, float]:
        golden = self.golden.get_active_golden(semantic_id)
        if not golden:
            return False, 0.0
        delta = candidate_score - golden.baseline_score
        is_regression = delta < -0.02
        return is_regression, delta
