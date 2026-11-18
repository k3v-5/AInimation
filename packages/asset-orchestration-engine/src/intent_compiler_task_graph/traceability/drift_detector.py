from typing import List, Dict, Any
from ..core.intent_schema import CompiledIntent, ExecutionPlanStep, IntentDelta

class DriftDetector:
    @staticmethod
    def detect_drift(intent: CompiledIntent, plan_steps: List[ExecutionPlanStep]):
        # 1. Comprobar exclusiones (MODERN, SCI_FI, etc.)
        prohibited: List[str] = []
        for excl in intent.exclusions:
            prohibited.extend(excl.prohibited_terms)

        for step in plan_steps:
            params_str = str(step.parameters).lower()
            for p in prohibited:
                if p.lower() in params_str:
                    raise ValueError(f"INTENT_DRIFT_DETECTED: Step '{step.step_id}' introduced prohibited term '{p}' in violation of intent exclusions.")

class IncrementalReplanner:
    @staticmethod
    def calculate_affected_subgraph(delta: IntentDelta) -> List[str]:
        target = delta.target.upper()
        if "ROOF" in target:
            return ["T_ROOF", "T_MATERIALS", "T_VALIDATE"]
        elif "DOOR" in target or "WINDOW" in target or "OPENING" in target:
            return ["T_OPENINGS", "T_MATERIALS", "T_VALIDATE"]
        elif "MATERIAL" in target or "TEXTURE" in target:
            return ["T_MATERIALS", "T_VALIDATE"]
        elif "TOWER" in target or "STRUCTURE" in target or "WALL" in target:
            return ["T_WALLS", "T_ROOF", "T_OPENINGS", "T_MATERIALS", "T_VALIDATE"]
        return ["T_DIMENSIONS", "T_WALLS", "T_ROOF", "T_OPENINGS", "T_MATERIALS", "T_VALIDATE"]
