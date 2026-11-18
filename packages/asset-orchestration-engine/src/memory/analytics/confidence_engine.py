from ..core.memory_schema import StrategyRecord

class ConfidenceEngine:
    @staticmethod
    def update_strategy_confidence(strat: StrategyRecord, is_success: bool, is_rollback: bool = False) -> StrategyRecord:
        strat.sample_count += 1
        if is_success and not is_rollback:
            strat.success_count += 1
            strat.confidence = min(0.98, round(strat.confidence + 0.05, 4))
        else:
            strat.failure_count += 1
            strat.confidence = max(0.10, round(strat.confidence - 0.08, 4))

        strat.success_rate = round(strat.success_count / strat.sample_count, 4)
        return strat
