import uuid
from typing import List, Dict, Any, Optional
from .action_schema import ActionPlan
from ..evaluation.utility_calculator import UtilityCalculator
from ...visual_intelligence.qa.quality_scorer import VerificationReport
from ...memory.api.asset_memory_api import AssetMemoryAPI

class ActionPlanner:
    def __init__(self, memory_api: Optional[AssetMemoryAPI] = None, max_risk_budget: float = 0.50):
        self.memory = memory_api
        self.max_risk_budget = max_risk_budget

    def plan_next_action(
        self,
        report: VerificationReport,
        asset_type: str = "SWORD"
    ) -> Optional[ActionPlan]:
        candidates: List[ActionPlan] = []

        # 1. Analizar fallos
        for fail in report.hard_failures + report.warnings:
            if "BLADE_RATIO" in fail:
                # Consultar memoria si existe
                strat_info = None
                if self.memory:
                    strat_info = self.memory.retrieve_recommended_strategy("BLADE_TOO_SHORT", asset_type, "BLADE")

                exp_imp = 0.15
                conf = strat_info.get("confidence", 0.80) if strat_info else 0.80
                pref_op = strat_info.get("preferred_operation", "SET_DIMENSIONS") if strat_info else "SET_DIMENSIONS"
                params = {"length": 0.95}

                u = UtilityCalculator.calculate_utility(
                    expected_improvement=exp_imp,
                    confidence=conf,
                    similarity=1.0,
                    risk=0.10,
                    estimated_cost=1.0
                )
                candidates.append(ActionPlan(
                    action_id=f"act_{uuid.uuid4().hex[:6]}",
                    target="blade",
                    strategy_id=strat_info.get("strategy_id", "strat_scale_blade") if strat_info else "strat_scale_blade",
                    operation_type=pref_op,
                    parameters=params,
                    expected_improvement=exp_imp,
                    risk=0.10,
                    estimated_cost=1.0,
                    utility=u,
                    reason=f"Blade ratio below goal. Historical strategy {pref_op} expected to improve +{exp_imp:.2f}."
                ))

            elif "METALLIC" in fail or "MATERIAL" in fail:
                u = UtilityCalculator.calculate_utility(expected_improvement=0.10, confidence=0.90, risk=0.05, estimated_cost=0.5)
                candidates.append(ActionPlan(
                    action_id=f"act_{uuid.uuid4().hex[:6]}",
                    target="blade",
                    strategy_id="strat_metallic",
                    operation_type="CHANGE_METALLIC",
                    parameters={"value": 0.90},
                    expected_improvement=0.10,
                    risk=0.05,
                    estimated_cost=0.5,
                    utility=u,
                    reason="Correct blade material to metallic standard."
                ))

        # 2. Filtrar por presupuesto de riesgo
        valid_candidates = [c for c in candidates if c.risk <= self.max_risk_budget]
        if not valid_candidates:
            return None

        # 3. Ordenar por Utilidad (Mayor a Menor)
        valid_candidates.sort(key=lambda x: x.utility, reverse=True)
        return valid_candidates[0]
