from typing import Dict, Any, List, Optional
from ..core.reference_types import UncertaintyType
from ..core.reference_schema import UncertaintyItem

class UncertaintyEvaluator:
    @staticmethod
    def evaluate_uncertainties(
        has_multi_view: bool = False,
        has_explicit_scale: bool = False
    ) -> List[UncertaintyItem]:
        uncertainties = []

        if not has_explicit_scale:
            uncertainties.append(UncertaintyItem(
                uncertainty_type=UncertaintyType.SCALE_UNKNOWN,
                description="Absolute real-world scale is not specified in the reference image.",
                impact="HIGH",
                suggested_question="¿Cuál es la escala deseada para el edificio (ej. ancho de 8 metros)?"
            ))

        if not has_multi_view:
            uncertainties.append(UncertaintyItem(
                uncertainty_type=UncertaintyType.BACKSIDE_UNKNOWN,
                description="Backside and rear facade geometry is not visible in single perspective reference.",
                impact="MEDIUM",
                suggested_question="¿La fachada posterior debe ser idéntica a la frontal o plana/ciega?"
            ))

        return uncertainties
