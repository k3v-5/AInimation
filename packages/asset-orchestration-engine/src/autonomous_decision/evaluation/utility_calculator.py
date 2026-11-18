from typing import Dict, Any

class UtilityCalculator:
    @staticmethod
    def calculate_utility(
        expected_improvement: float,
        confidence: float = 0.80,
        similarity: float = 1.0,
        risk: float = 0.10,
        estimated_cost: float = 1.0
    ) -> float:
        """
        Fórmula: Utility = Expected_Improvement * Confidence * Similarity * (1 - Risk) / Cost
        """
        cost = max(0.1, estimated_cost)
        safety_multiplier = max(0.0, 1.0 - risk)
        utility = (expected_improvement * confidence * similarity * safety_multiplier) / cost
        return round(utility, 4)
