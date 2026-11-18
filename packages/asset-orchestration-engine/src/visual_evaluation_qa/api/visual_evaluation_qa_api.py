from typing import Dict, Any, Optional
from ..core.evaluation_schema import (
    EvaluationReport, ExpectedVisualProfile, RepairPlan
)
from ..core.evaluation_profiles import ProfileRegistry, EvaluationProfile
from ..evaluators.dimension_evaluator import MultiDimensionEvaluator
from ..diagnosis.repair_planner import RepairPlanner
from ..loop.closed_loop_optimizer import ClosedLoopOptimizer

class VisualEvaluationQAAPI:
    """
    Visual Evaluation & Automatic Quality Control API (AOE v20)
    
    Regla Fundamental:
    LA IA NO ADIVINA QUÉ SALIÓ MAL.
    RECIBE DIAGNÓSTICO ESTRUCTURADO (DIMENSIÓN, COMPONENTE, PARÁMETRO, VALOR ACTUAL VS ESPERADO).
    APLICA REPARACIÓN MÍNIMA Y VERIFICA NO-REGRESIÓN EN BUCLE CERRADO.
    """
    def __init__(self):
        pass

    def evaluate(
        self,
        target_id: str,
        actual_data: Dict[str, Any],
        expected_profile: ExpectedVisualProfile,
        profile_name: str = "BALANCED"
    ) -> EvaluationReport:
        profile = ProfileRegistry.get_profile(profile_name)
        return MultiDimensionEvaluator.evaluate(target_id, actual_data, expected_profile, profile)

    def diagnose_and_plan_repair(self, report: EvaluationReport) -> Optional[RepairPlan]:
        return RepairPlanner.create_repair_plan(report)

    def optimize_closed_loop(
        self,
        target_id: str,
        initial_actual_data: Dict[str, Any],
        expected_profile: ExpectedVisualProfile,
        apply_repair_callback,
        profile_name: str = "BALANCED"
    ) -> Dict[str, Any]:
        profile = ProfileRegistry.get_profile(profile_name)
        return ClosedLoopOptimizer.run_optimization_loop(
            target_id=target_id,
            initial_actual_data=initial_actual_data,
            expected_profile=expected_profile,
            profile=profile,
            apply_repair_callback=apply_repair_callback
        )
