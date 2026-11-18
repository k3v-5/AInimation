from typing import Dict, Any, Optional, List
from ..context.evaluation_context import EvaluationContext
from ..critic.critic_schema import CriticReport, CriticIssue, CriticStatus, IssueSeverity
from ..critic.ai_visual_critic import AIVisualCritic
from ..patching.patch_generator import ParameterPatchGenerator, ParameterPatch
from ..engine.visual_evaluation_engine import VisualEvaluationEngine
from ...spec_compiler.core.asset_spec import AssetSpec
from ...procedural_templates.api.procedural_templates_api import ProceduralTemplatesAPI
from ...correction_execution.providers.blender_provider import IBlenderProvider

class VisualCriticAPI:
    """
    Visual Evaluation & AI Critic API (AOE v16)
    
    Regla Fundamental:
    LA IA NO REHACE EL MODELO. DIAGNOSTICA Y GENERA PARAMETER PATCHES.
    EL MOTOR RECONSTRUYE PARCIALMENTE ÚNICAMENTE LOS COMPONENTES AFECTADOS.
    """
    def __init__(
        self,
        templates_api: ProceduralTemplatesAPI,
        provider: IBlenderProvider,
        max_visual_iterations: int = 4
    ):
        self.engine = VisualEvaluationEngine(
            templates_api=templates_api,
            provider=provider,
            max_visual_iterations=max_visual_iterations
        )

    def evaluate_and_refine(
        self,
        asset_id: str,
        spec: AssetSpec,
        initial_params: Dict[str, Any],
        protected_params: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        return self.engine.evaluate_and_refine(
            asset_id=asset_id,
            spec=spec,
            initial_params=initial_params,
            protected_params=protected_params
        )

    def critique(self, context: EvaluationContext, live_measurements: Dict[str, Any]) -> CriticReport:
        return AIVisualCritic.evaluate(context, live_measurements)
