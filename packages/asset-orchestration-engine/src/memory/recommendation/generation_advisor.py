from typing import Dict, Any, List, Optional
from ..storage.sqlite_memory_store import SQLiteMemoryStore
from ..analytics.pattern_detector import PatternDetector

class GenerationAdvisor:
    @staticmethod
    def get_generation_recommendations(
        store: SQLiteMemoryStore,
        asset_type: str = "SWORD"
    ) -> List[Dict[str, Any]]:
        recs = []
        # Comprobar si hay bias sistemático
        bias = PatternDetector.check_systematic_bias(store, failure_type="BLADE_TOO_SHORT", asset_type=asset_type, threshold=5)
        if bias:
            recs.append({
                "type": "PARAMETER_ADJUSTMENT",
                "target_component": "blade",
                "recommended_scale_multiplier": 1.25,
                "reason": f"Systematic generation bias detected ({bias['frequency']} occurrences). Pre-scale initial blade by +25%."
            })

        return recs
