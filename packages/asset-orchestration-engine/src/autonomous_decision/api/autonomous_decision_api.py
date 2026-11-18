from typing import Dict, Any, Optional, List
from ..core.decision_engine import DecisionEngine
from ..controllers.budget_controller import CorrectionBudget
from ...visual_intelligence.api.visual_intelligence_api import VisualIntelligenceAPI
from ...visual_intelligence.core.visual_goal_builder import VisualGoalSpec
from ...correction_execution.api.correction_execution_api import CorrectionExecutionAPI
from ...memory.api.asset_memory_api import AssetMemoryAPI

class AutonomousDecisionAPI:
    """
    Autonomous Asset Optimization & Decision API (AOE v13)
    
    Regla Fundamental:
    LA IA PROPONE. EL MOTOR DECIDE. BLENDER EJECUTA. EL VALIDADOR COMPRUEBA. LA MEMORIA APRENDE.
    SI EL ASSET YA CUMPLE EL OBJETIVO (GOOD ENOUGH >= 0.85), NO HACER NADA MÁS (STOP).
    """
    def __init__(
        self,
        visual_api: VisualIntelligenceAPI,
        correction_api: CorrectionExecutionAPI,
        memory_api: Optional[AssetMemoryAPI] = None,
        acceptance_threshold: float = 0.85,
        budget: Optional[CorrectionBudget] = None
    ):
        self.engine = DecisionEngine(
            visual_api=visual_api,
            correction_api=correction_api,
            memory_api=memory_api,
            acceptance_threshold=acceptance_threshold,
            budget=budget
        )

    def optimize_asset(
        self,
        asset_id: str,
        goal_spec: VisualGoalSpec,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        return self.engine.optimize_asset_autonomously(asset_id, goal_spec, dry_run=dry_run)

    def trigger_emergency_stop(self):
        self.engine.stopping_ctrl.emergency_stop_triggered = True
