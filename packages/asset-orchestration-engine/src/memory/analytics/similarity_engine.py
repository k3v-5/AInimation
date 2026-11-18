from typing import Dict, Any

class SimilarityEngine:
    @staticmethod
    def calculate_similarity(query: Dict[str, Any], record_data: Dict[str, Any]) -> float:
        score = 0.0
        weights = {"failure_type": 0.40, "asset_type": 0.30, "component_type": 0.20, "engine_version": 0.10}

        if query.get("failure_type") == record_data.get("failure_type"):
            score += weights["failure_type"]
        if query.get("asset_type") == record_data.get("asset_type"):
            score += weights["asset_type"]
        if query.get("component_type") == record_data.get("component_type"):
            score += weights["component_type"]
        if query.get("engine_version", "1.0") == record_data.get("engine_version", "1.0"):
            score += weights["engine_version"]

        return round(score, 4)
