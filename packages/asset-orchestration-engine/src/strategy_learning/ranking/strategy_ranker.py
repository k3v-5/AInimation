from typing import List, Tuple, Optional
from ..core.strategy_models import StrategyRecord
from ..core.learning_models import StrategyOptimizationProfile
from .candidate_scorer import CandidateScorer

class StrategyRanker:
    """Ranks candidate strategies deterministically using explicit optimization profiles."""

    @staticmethod
    def rank(
        strategies: List[StrategyRecord],
        profile: Optional[StrategyOptimizationProfile] = None
    ) -> List[Tuple[StrategyRecord, float]]:
        prof = profile or StrategyOptimizationProfile.balanced()
        scored: List[Tuple[StrategyRecord, float]] = []

        for s in strategies:
            # Check hard constraints: if regression rate > max allowed, penalize heavily
            score = CandidateScorer.calculate_score(s, prof)
            if s.historical_regression_rate > prof.max_allowed_regression and prof.max_allowed_regression == 0.0:
                score *= 0.50 # heavy penalty for regression risk
            scored.append((s, score))

        # Sort descending by score, tie-break by confidence, then strategy_id
        scored.sort(key=lambda item: (item[1], item[0].confidence, item[0].strategy_id), reverse=True)
        return scored
