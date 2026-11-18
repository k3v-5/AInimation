from typing import List, Tuple
from ..core.memory_schema import StrategyRecord

class MemoryRanker:
    @staticmethod
    def rank_strategies(
        strategies_with_sim: List[Tuple[StrategyRecord, float]]
    ) -> List[Tuple[StrategyRecord, float]]:
        """
        Calcula: StrategyScore = SuccessRate * Confidence * Similarity * SafetyFactor
        """
        ranked = []
        for strat, sim in strategies_with_sim:
            safety_factor = 1.0 if "DELETE" not in strat.preferred_operation else 0.5
            final_score = round(strat.success_rate * strat.confidence * sim * safety_factor, 4)
            ranked.append((strat, final_score))

        # Ordenar de mayor a menor score
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
