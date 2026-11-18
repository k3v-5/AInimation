from typing import List, Dict, Any
from ..core.strategy_models import StrategyRecord

class TradeoffOptimizer:
    """Computes Pareto front of non-dominated strategies across quality, cost, and time."""

    @staticmethod
    def compute_pareto_front(strategies: List[StrategyRecord]) -> List[StrategyRecord]:
        pareto_front: List[StrategyRecord] = []

        for candidate in strategies:
            is_dominated = False
            for other in strategies:
                if candidate.strategy_id == other.strategy_id:
                    continue

                # 'other' dominates 'candidate' if it is >= in quality AND <= in cost & time, with at least one strictly better
                better_or_equal = (
                    other.average_quality_score >= candidate.average_quality_score and
                    other.estimated_cost <= candidate.estimated_cost and
                    other.estimated_time <= candidate.estimated_time
                )
                strictly_better = (
                    other.average_quality_score > candidate.average_quality_score or
                    other.estimated_cost < candidate.estimated_cost or
                    other.estimated_time < candidate.estimated_time
                )
                if better_or_equal and strictly_better:
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_front.append(candidate)

        return pareto_front
