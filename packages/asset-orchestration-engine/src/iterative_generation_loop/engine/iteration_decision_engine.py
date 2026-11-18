from typing import List, Dict, Any, Tuple
from ..core.loop_types import DecisionOutcome, StopReason
from ..core.loop_schema import IterationRecord, IterationLoopConfiguration

class IterationDecisionEngine:
    @classmethod
    def evaluate_decision(
        cls,
        current_iter: int,
        current_score: float,
        visual_score: float,
        geometry_score: float,
        has_critical_blocker: bool,
        history: List[IterationRecord],
        config: IterationLoopConfiguration
    ) -> Tuple[DecisionOutcome, StopReason]:
        # 1. Chequeo de Fallas Críticas (Hard Constraints)
        if has_critical_blocker:
            if current_iter >= config.max_iterations:
                return DecisionOutcome.BUDGET_EXHAUSTED, StopReason.MAX_ITERATIONS_REACHED
            return DecisionOutcome.CONTINUE, StopReason.CONVERGENCE_REACHED

        # 2. Chequeo de Convergencia
        targets = config.targets
        if (current_score >= targets.overall_target_score and
            visual_score >= targets.minimum_visual_score and
            geometry_score >= targets.minimum_geometry_score):
            return DecisionOutcome.CONVERGED, StopReason.CONVERGENCE_REACHED

        # 3. Chequeo de Presupuesto / Máximas Iteraciones
        if current_iter >= config.max_iterations:
            return DecisionOutcome.BUDGET_EXHAUSTED, StopReason.MAX_ITERATIONS_REACHED

        # 4. Chequeo de Ciclos (Cycle Detection)
        if config.cycle_detection_enabled and len(history) >= 2:
            current_hash = history[-1].state_hash if history else ""
            for prev in history[:-1]:
                if prev.state_hash == current_hash and current_hash != "":
                    return DecisionOutcome.STAGNATED, StopReason.CYCLE_DETECTED

        # 5. Chequeo de Estancamiento (Stagnation Detection)
        if len(history) >= config.stagnation_window:
            recent_improvements = [
                history[i].overall_score - history[i-1].overall_score
                for i in range(len(history)-config.stagnation_window+1, len(history))
            ]
            if all(imp < config.minimum_improvement for imp in recent_improvements):
                return DecisionOutcome.STAGNATED, StopReason.STAGNATION_DETECTED

        return DecisionOutcome.CONTINUE, StopReason.CONVERGENCE_REACHED
