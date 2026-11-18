from typing import Dict, Any, List, Optional
from ..core.orchestrator_schema import OrchestrationCorrectionPlan

class CorrectionAgent:
    """
    Agente de Corrección Quirúrgica:
    Analiza fallos de QA y genera planes de corrección mínimos.
    REGLA: NUNCA RECONSTRUIR LA CASA COMPLETA SI SOLO FALLÓ LA PUERTA O LA ESCALERA.
    """
    @staticmethod
    def generate_correction_plan(
        problem: str,
        current_parameters: Dict[str, Any]
    ) -> Optional[OrchestrationCorrectionPlan]:
        if "DOOR_TOO_NARROW" in problem:
            old_w = current_parameters.get("door_width", 0.62)
            new_w = round(max(0.85, old_w + 0.20), 2)
            return OrchestrationCorrectionPlan(
                problem="DOOR_TOO_NARROW",
                parameter_to_change="door_width",
                old_value=old_w,
                new_value=new_w,
                affected_subtrees=["door", "collision", "interaction", "navigation"],
                rebuild_scope="SUBTREE"
            )

        if "STAIR_TOO_STEEP" in problem:
            old_slope = current_parameters.get("stair_slope", 46.0)
            return OrchestrationCorrectionPlan(
                problem="STAIR_TOO_STEEP",
                parameter_to_change="stair_slope",
                old_value=old_slope,
                new_value=32.5,
                affected_subtrees=["stair", "navigation", "traversal"],
                rebuild_scope="SUBTREE"
            )

        return None
