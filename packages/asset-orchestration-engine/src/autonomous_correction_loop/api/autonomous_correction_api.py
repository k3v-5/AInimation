from typing import Dict, Any, Optional
from ..core.loop_schema import AutonomousLoopResult, LoopStatus
from ..loop.feedback_loop_controller import FeedbackLoopController
from ...visual_reference_matching.core.reference_schema import ReferenceProfile
from ...parametric_builder.core.parametric_types import AssetType
from ...parametric_builder.api.parametric_builder_api import ParametricBuilderAPI

class AutonomousCorrectionLoopAPI:
    """
    Visual Feedback & Autonomous Correction Loop API (AOE v26)
    
    Regla Fundamental:
    CONECTA EVALUACIÓN VISUAL CON CORRECCIÓN PARAMÉTRICA DIRIGIDA.
    MODIFICA PARÁMETROS ESPECÍFICOS (ROOF_HEIGHT, WINDOW_SCALE) Y RECONSTRUYE SÓLO SUBÁRBOLES AFECTADOS.
    DETIENE AUTOMÁTICAMENTE TRAS 5 ITERACIONES CON ESTADO 'NEEDS_REVIEW' SI NO CONVERGE.
    """
    def __init__(self, builder: Optional[ParametricBuilderAPI] = None):
        self.builder = builder or ParametricBuilderAPI()

    def run_correction_loop(
        self,
        target_asset_id: str,
        asset_type: AssetType,
        initial_parameters: Dict[str, Any],
        reference: ReferenceProfile,
        force_unresolvable: bool = False
    ) -> AutonomousLoopResult:
        return FeedbackLoopController.run_correction_loop(
            target_asset_id=target_asset_id,
            asset_type=asset_type,
            initial_parameters=initial_parameters,
            reference=reference,
            builder=self.builder,
            force_unresolvable=force_unresolvable
        )
