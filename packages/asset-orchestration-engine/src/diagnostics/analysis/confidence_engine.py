from typing import List

class ConfidenceEngine:
    """Calculates confidence levels for diagnostic root causes based on evidence strength and corroboration."""
    
    @staticmethod
    def calculate_confidence(has_direct_evidence: bool, evidence_count: int, has_corroboration: bool) -> float:
        score = 0.4
        if has_direct_evidence:
            score += 0.4
        if evidence_count > 1:
            score += 0.1
        if has_corroboration:
            score += 0.1
        return min(1.0, max(0.0, score))

    @staticmethod
    def categorize_confidence(score: float) -> str:
        if score >= 0.8:
            return "HIGH"
        elif score >= 0.5:
            return "MEDIUM"
        return "LOW"
