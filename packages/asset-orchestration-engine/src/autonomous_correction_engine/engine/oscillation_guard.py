from typing import Dict, Any, List, Optional
from ..core.correction_schema import ParameterChange

class OscillationGuard:
    @classmethod
    def check_oscillation(
        cls,
        param_change: ParameterChange,
        history: List[Dict[str, Any]]
    ) -> bool:
        if len(history) < 2:
            return False

        # If last change on this param was opposite delta
        recent = [h for h in history if h.get("parameter_id") == param_change.parameter_id]
        if len(recent) >= 2:
            last_delta = recent[-1].get("delta", 0.0)
            if last_delta * param_change.delta < 0 and abs(last_delta + param_change.delta) < 0.01:
                return True # Exact opposite oscillation
        return False
