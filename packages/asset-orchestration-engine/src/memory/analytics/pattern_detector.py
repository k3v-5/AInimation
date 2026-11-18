from typing import Optional, Dict, Any
from ..storage.sqlite_memory_store import SQLiteMemoryStore

class PatternDetector:
    @staticmethod
    def check_systematic_bias(
        store: SQLiteMemoryStore,
        failure_type: str = "BLADE_TOO_SHORT",
        asset_type: str = "SWORD",
        threshold: int = 5
    ) -> Optional[Dict[str, Any]]:
        count = store.count_failures_by_type(failure_type, asset_type)
        if count >= threshold:
            return {
                "alert": "SYSTEMATIC_GENERATION_BIAS",
                "failure_type": failure_type,
                "asset_type": asset_type,
                "frequency": count,
                "recommendation": f"Blender generation for '{asset_type}' systematically produces '{failure_type}'. Increase initial generation target."
            }
        return None
