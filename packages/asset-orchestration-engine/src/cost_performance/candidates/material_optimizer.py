from typing import List, Dict, Any

class MaterialOptimizer:
    """Analyzes shader complexity and detects opportunities for deduplication and merging."""

    @staticmethod
    def analyze_materials(materials: List[str], max_allowed: int = 4) -> Dict[str, Any]:
        count = len(materials)
        unique_mats = list(set(materials))
        has_duplicates = len(unique_mats) < count

        opportunities = []
        if has_duplicates:
            opportunities.append("MATERIAL_DEDUPLICATION")
        if len(unique_mats) > max_allowed:
            opportunities.append("MATERIAL_MERGE")

        return {
            "total_material_slots": count,
            "unique_materials": len(unique_mats),
            "opportunities": opportunities,
            "can_optimize": len(opportunities) > 0
        }
