from typing import List
from ..core.golden_models import GoldenAsset
from ...evaluation import EvaluationBenchmark

class CompatibilityChecker:
    """Validates structural and semantic compatibility between candidate assets and Golden references."""
    
    @staticmethod
    def check_compatibility(candidate_bench: EvaluationBenchmark, golden_asset: GoldenAsset) -> List[str]:
        errors: List[str] = []
        if candidate_bench.asset_semantic_id != golden_asset.semantic_id:
            errors.append(
                f"Semantic ID mismatch: candidate has '{candidate_bench.asset_semantic_id}', "
                f"golden has '{golden_asset.semantic_id}'."
            )
        return errors
