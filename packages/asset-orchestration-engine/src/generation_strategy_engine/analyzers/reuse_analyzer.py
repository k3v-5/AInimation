from typing import Dict, Any, List, Optional
from ..core.strategy_schema import ReuseAnalysisReport

class ReuseAnalyzer:
    @classmethod
    def analyze_reuse(
        cls,
        asset_class: str,
        existing_library: Dict[str, Dict[str, Any]],
        intent_type_str: str = "CREATE"
    ) -> ReuseAnalysisReport:
        best_match = None
        best_similarity = 0.0

        for asset_id, data in existing_library.items():
            if data.get("asset_class") == asset_class and data.get("status") == "APPROVED":
                sim = data.get("similarity", 0.90)
                if sim > best_similarity:
                    best_similarity = sim
                    best_match = asset_id

        # Si el intent es modificar o hay match alto con cambio de componente menor
        if best_match and (best_similarity >= 0.85 or intent_type_str == "MODIFY"):
            return ReuseAnalysisReport(
                has_match=True,
                matched_asset_id=best_match,
                similarity_score=best_similarity,
                recommended_action="EXISTING_ASSET_MODIFICATION"
            )

        return ReuseAnalysisReport(
            has_match=False,
            similarity_score=0.0,
            recommended_action="FULL_GENERATION"
        )
