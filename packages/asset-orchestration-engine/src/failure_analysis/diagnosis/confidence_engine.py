from typing import Dict, Any, List

class ConfidenceEngine:
    """Calculates diagnostic confidence score (0.0 - 1.0) based on corroborating evidence."""

    @staticmethod
    def calculate_confidence(
        has_blender_evidence: bool = False,
        has_benchmark_score: bool = False,
        has_historical_match: bool = False,
        has_stack_trace: bool = False
    ) -> float:
        score = 0.50
        if has_blender_evidence:
            score += 0.25
        if has_benchmark_score:
            score += 0.15
        if has_historical_match:
            score += 0.10
        if has_stack_trace:
            score += 0.05
        return min(1.0, round(score, 2))
