from typing import Dict, Any, List, Optional, Tuple
from ..core.evaluation_schema import (
    EvaluationReport, ExpectedVisualProfile, RepairPlan
)
from ..core.evaluation_profiles import EvaluationProfile
from ..evaluators.dimension_evaluator import MultiDimensionEvaluator
from ..diagnosis.repair_planner import RepairPlanner
from .regression_detector import RegressionDetector, OscillationDetector

class ClosedLoopOptimizer:
    @staticmethod
    def run_optimization_loop(
        target_id: str,
        initial_actual_data: Dict[str, Any],
        expected_profile: ExpectedVisualProfile,
        profile: EvaluationProfile,
        apply_repair_callback
    ) -> Dict[str, Any]:
        iteration = 0
        current_data = dict(initial_actual_data)
        history_scores = []
        reports = []

        last_report = MultiDimensionEvaluator.evaluate(target_id, current_data, expected_profile, profile)
        history_scores.append(last_report.overall_score)
        reports.append(last_report)

        while iteration < profile.max_repair_iterations:
            if last_report.is_pass:
                return {
                    "final_status": "ACCEPT",
                    "iterations": iteration,
                    "final_score": last_report.overall_score,
                    "last_report": last_report,
                    "message": f"Asset '{target_id}' passed evaluation with score {last_report.overall_score}."
                }

            # Diagnosticar y Planificar Reparación
            plan = RepairPlanner.create_repair_plan(last_report)
            if not plan or not plan.candidates:
                break

            # Aplicar mejor candidato
            best_candidate = plan.candidates[0]
            current_data = apply_repair_callback(current_data, best_candidate)
            iteration += 1

            new_report = MultiDimensionEvaluator.evaluate(target_id, current_data, expected_profile, profile)

            # Comprobar Regresión
            is_regr, regr_msg = RegressionDetector.check_regression(last_report, new_report)
            if is_regr:
                return {
                    "final_status": "REJECT_REGRESSION",
                    "iterations": iteration,
                    "final_score": new_report.overall_score,
                    "last_report": new_report,
                    "message": regr_msg
                }

            history_scores.append(new_report.overall_score)
            reports.append(new_report)

            # Comprobar Estancamiento u Oscilación
            is_stagnant, stag_msg = OscillationDetector.check_stagnation_or_cycle(history_scores, profile.stagnation_threshold)
            if is_stagnant:
                return {
                    "final_status": "STOP_STAGNATION",
                    "iterations": iteration,
                    "final_score": new_report.overall_score,
                    "last_report": new_report,
                    "message": stag_msg
                }

            last_report = new_report

        final_status = "ACCEPT" if last_report.is_pass else "FAIL_MAX_ITERATIONS"
        return {
            "final_status": final_status,
            "iterations": iteration,
            "final_score": last_report.overall_score,
            "last_report": last_report,
            "message": f"Optimization ended with status {final_status}."
        }
