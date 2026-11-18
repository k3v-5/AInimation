from typing import List, Dict, Any, Tuple

class LoopController:
    @staticmethod
    def check_oscillation(action_history: List[str]) -> Tuple[bool, str]:
        if len(action_history) >= 4:
            # Detectar patrón A -> B -> A -> B
            last_4 = action_history[-4:]
            if last_4[0] == last_4[2] and last_4[1] == last_4[3] and last_4[0] != last_4[1]:
                return True, "OSCILLATION_DETECTED: Alternating repetitive operations detected. Stopping current strategy."
        return False, ""

    @staticmethod
    def check_no_progress(score_deltas: List[float], threshold_iterations: int = 3) -> Tuple[bool, str]:
        if len(score_deltas) >= threshold_iterations:
            recent = score_deltas[-threshold_iterations:]
            if all(abs(d) < 0.02 for d in recent):
                return True, f"NO_PROGRESS: Last {threshold_iterations} operations yielded zero significant improvement."
        return False, ""
