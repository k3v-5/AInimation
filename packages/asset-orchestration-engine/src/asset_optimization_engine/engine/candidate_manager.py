from typing import List, Optional
from ..core.optimization_schema import OptimizationCandidate, OptimizationProfile

class CandidateManager:
    @classmethod
    def evaluate_candidate(
        cls,
        candidate: OptimizationCandidate,
        profile: OptimizationProfile
    ) -> bool:
        # 1. Regla de No Degradación Visual Excesiva
        if abs(candidate.visual_delta) > profile.visual_degradation_limit and candidate.visual_delta < 0:
            candidate.accepted = False
            candidate.rejection_reason = f"EXCESSIVE_VISUAL_LOSS: {abs(candidate.visual_delta):.1%} > limit {profile.visual_degradation_limit:.1%}"
            return False

        # 2. Zero-Gain Rejection
        if candidate.performance_delta <= 0 and candidate.memory_delta <= 0 and candidate.visual_delta < 0:
            candidate.accepted = False
            candidate.rejection_reason = "ZERO_GAIN_REJECTION: Quality degraded without any performance or memory gain."
            return False

        candidate.accepted = True
        return True

    @classmethod
    def select_best_candidate(
        cls,
        candidates: List[OptimizationCandidate]
    ) -> Optional[OptimizationCandidate]:
        valid_cands = [c for c in candidates if c.accepted]
        if not valid_cands:
            return None
        
        # Maximize gain (performance + memory) with minimal visual loss
        valid_cands.sort(
            key=lambda c: (c.performance_delta + c.memory_delta * 0.05 + c.visual_delta),
            reverse=True
        )
        return valid_cands[0]
