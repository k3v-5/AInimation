from typing import Dict, Any, List, Optional
from ...visual_reference_matching.core.reference_schema import ReferenceProfile, ErrorMap
from ...visual_reference_matching.matching.geometric_matcher import GeometricMatcher
from ...parametric_builder.core.parametric_types import AssetType
from ...parametric_builder.core.parametric_schema import ParameterChange
from ...parametric_builder.api.parametric_builder_api import ParametricBuilderAPI
from ..core.loop_schema import (
    AutonomousLoopResult, LoopStatus, LoopIterationRecord, CorrectionPlan
)
from ..analysis.correction_planner import CorrectionPlanner

class FeedbackLoopController:
    MAX_ITERATIONS = 5
    QUALITY_THRESHOLD = 0.90

    @classmethod
    def run_correction_loop(
        cls,
        target_asset_id: str,
        asset_type: AssetType,
        initial_parameters: Dict[str, Any],
        reference: ReferenceProfile,
        builder: ParametricBuilderAPI,
        force_unresolvable: bool = False
    ) -> AutonomousLoopResult:
        current_params = dict(initial_parameters)
        iteration = 0
        history: List[LoopIterationRecord] = []
        diagnostics: List[str] = []

        # 1. Construcción Inicial
        build_res = builder.build_parametric_asset(asset_type, current_params)
        model_data = {
            "dimensions": build_res.dimensions,
            "components": build_res.created_components,
            "parameters": current_params
        }

        # 2. Evaluación Inicial
        error_map = GeometricMatcher.compare_model_against_reference(target_asset_id, model_data, reference)
        current_score = error_map.overall_geometric_score

        if current_score >= cls.QUALITY_THRESHOLD and not error_map.discrepancies:
            return AutonomousLoopResult(
                status=LoopStatus.ACCEPTED,
                iterations_run=0,
                final_score=current_score,
                target_asset_id=target_asset_id,
                message=f"Asset '{target_asset_id}' met quality threshold ({current_score:.2f} >= {cls.QUALITY_THRESHOLD}) on initial build."
            )

        # 3. Bucle de Corrección Autónomo
        while iteration < cls.MAX_ITERATIONS:
            score_before = current_score
            iteration += 1

            if force_unresolvable:
                # Simular discrepancia no resoluble por parámetros (ej. mismatch de estilo arquitectónico)
                diagnostics.append(f"Iteration {iteration}: Architectural style mismatch persists.")
                history.append(LoopIterationRecord(
                    iteration_index=iteration,
                    score_before=score_before,
                    score_after=score_before,
                    applied_patches={},
                    affected_components=[]
                ))
                continue

            # Planificar correcciones dirigidas
            plan = CorrectionPlanner.plan_corrections(error_map, current_params)
            if not plan.steps:
                break

            # Aplicar parches paramétricos (sin reconstruir la casa completa)
            changes = [
                ParameterChange(step.parameter_name, step.current_value, step.recommended_value)
                for step in plan.steps
            ]
            ok_upd, new_build_res, logs = builder.update_parameters(asset_type, current_params, changes)
            if not ok_upd:
                diagnostics.append(f"Iteration {iteration}: Parameter update failed: {logs}")
                break

            current_params = new_build_res.parameters
            applied_map = {step.parameter_name: step.recommended_value for step in plan.steps}

            # Re-evaluar contra la referencia
            updated_model_data = {
                "dimensions": new_build_res.dimensions,
                "components": new_build_res.created_components,
                "parameters": current_params
            }
            error_map = GeometricMatcher.compare_model_against_reference(target_asset_id, updated_model_data, reference)
            current_score = error_map.overall_geometric_score

            history.append(LoopIterationRecord(
                iteration_index=iteration,
                score_before=score_before,
                score_after=current_score,
                applied_patches=applied_map,
                affected_components=plan.affected_components
            ))

            diagnostics.append(f"Iteration {iteration}: Score improved {score_before:.2f} -> {current_score:.2f} | Affected: {plan.affected_components} (Scope: {plan.rebuild_scope})")

            # Comprobar si superó el Quality Gate
            if current_score >= cls.QUALITY_THRESHOLD and not error_map.discrepancies:
                return AutonomousLoopResult(
                    status=LoopStatus.ACCEPTED,
                    iterations_run=iteration,
                    final_score=current_score,
                    target_asset_id=target_asset_id,
                    history=history,
                    diagnostics=diagnostics,
                    message=f"Asset '{target_asset_id}' reached acceptable quality ({current_score:.2f} >= {cls.QUALITY_THRESHOLD}) in {iteration} iteration(s)."
                )

        # Si agotó las 5 iteraciones sin alcanzar el umbral, detener y generar diagnóstico
        unresolved = [d.description for d in error_map.discrepancies]
        if force_unresolvable:
            unresolved.append("Architectural style mismatch persists.")

        return AutonomousLoopResult(
            status=LoopStatus.NEEDS_REVIEW,
            iterations_run=iteration,
            final_score=current_score,
            target_asset_id=target_asset_id,
            history=history,
            unresolved_problems=unresolved,
            diagnostics=diagnostics,
            message=f"Asset '{target_asset_id}' halted at max iterations ({iteration}/{cls.MAX_ITERATIONS}) with score {current_score:.2f} < {cls.QUALITY_THRESHOLD}."
        )
