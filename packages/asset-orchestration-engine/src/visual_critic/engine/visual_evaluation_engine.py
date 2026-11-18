from typing import Dict, Any, List, Optional, Tuple
from ..context.evaluation_context import EvaluationContext
from ..critic.critic_schema import CriticReport, CriticStatus
from ..critic.ai_visual_critic import AIVisualCritic
from ..patching.patch_generator import ParameterPatchGenerator, ParameterPatch
from ...spec_compiler.core.asset_spec import AssetSpec
from ...procedural_templates.api.procedural_templates_api import ProceduralTemplatesAPI
from ...correction_execution.providers.blender_provider import IBlenderProvider

class VisualEvaluationEngine:
    """
    Visual Evaluation & AI Critic Engine (AOE v16)
    
    Regla Fundamental:
    La IA no rehace el modelo. Diagnostica y sugiere ParameterPatches estructurados.
    El motor aplica parches localizados reconstruyendo únicamente componentes afectados.
    """
    def __init__(
        self,
        templates_api: ProceduralTemplatesAPI,
        provider: IBlenderProvider,
        max_visual_iterations: int = 4
    ):
        self.templates_api = templates_api
        self.provider = provider
        self.max_visual_iterations = max_visual_iterations

    def evaluate_and_refine(
        self,
        asset_id: str,
        spec: AssetSpec,
        initial_params: Dict[str, Any],
        protected_params: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        iteration = 0
        current_params = dict(initial_params)
        history = []

        while iteration < self.max_visual_iterations:
            iteration += 1

            # 1. Leer estado actual del asset
            asset = self.provider.assets.get(asset_id, {})
            comps = list(asset.get("components", {}).keys())
            blade_dims = asset.get("components", {}).get("blade", {}).get("dimensions", (0.05, 0.02, 0.90))

            live_measurements = {
                "components": comps,
                "blade_dimensions": blade_dims
            }

            # 2. Construir Contexto de Evaluación
            ctx = EvaluationContext(
                asset_id=asset_id,
                generation_id=f"gen_{asset_id}_{iteration}",
                template_id="weapon.sword.standard",
                template_version="1.0.0",
                asset_spec=spec,
                resolved_parameters=current_params,
                iteration_number=iteration,
                iteration_budget=self.max_visual_iterations,
                protected_parameters=protected_params or []
            )

            # 3. Crítica Visual Estructurada
            report: CriticReport = AIVisualCritic.evaluate(ctx, live_measurements)

            if report.status == CriticStatus.PASS:
                return {
                    "final_status": "ACCEPT",
                    "iterations": iteration,
                    "overall_score": report.overall_visual_score,
                    "report": report,
                    "history": history,
                    "message": "Visual evaluation PASSED with zero critical issues."
                }

            if report.status == CriticStatus.FAIL:
                return {
                    "final_status": "REJECT",
                    "iterations": iteration,
                    "overall_score": report.overall_visual_score,
                    "report": report,
                    "history": history,
                    "message": f"Visual evaluation FAILED: {report.summary}"
                }

            # 4. Generación de ParameterPatches
            patches = ParameterPatchGenerator.generate_patches(report, protected_parameters=protected_params)
            if not patches:
                return {
                    "final_status": "ACCEPT_WITH_WARNINGS",
                    "iterations": iteration,
                    "overall_score": report.overall_visual_score,
                    "report": report,
                    "history": history,
                    "message": "No actionable patches generated. Accepted with warnings."
                }

            # 5. Aplicar Patch y Reconstrucción Parcial (Fase 15)
            applied_patches = []
            for p in patches:
                ok_patch, msg_patch = self.templates_api.apply_parameter_patch(
                    asset_id=asset_id,
                    target_component=p.target_component,
                    parameter_name=p.parameter_name,
                    new_value=p.value
                )
                if ok_patch:
                    current_params[p.parameter_name] = p.value
                    applied_patches.append(p)

            history.append({
                "iteration": iteration,
                "score_before": report.overall_visual_score,
                "issues": [i.property_name for i in report.issues],
                "applied_patches": [p.parameter_name for p in applied_patches]
            })

        return {
            "final_status": "CONVERGENCE_FAILURE",
            "iterations": iteration,
            "overall_score": report.overall_visual_score,
            "report": report,
            "history": history,
            "message": "Maximum visual critique iterations reached."
        }
