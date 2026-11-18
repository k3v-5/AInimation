from typing import List, Dict, Any, Optional
from ..core.qa_schema import GeometricDefect

class CrossCorrelationEngine:
    @classmethod
    def correlate_with_visual_evaluation(
        cls,
        visual_eval_result: Optional[Any],
        geometric_defects: List[GeometricDefect]
    ) -> List[Dict[str, Any]]:
        correlations: List[Dict[str, Any]] = []
        if not visual_eval_result:
            return correlations

        v_defects = getattr(visual_eval_result, "defects", [])
        for v_def in v_defects:
            v_type = getattr(v_def, "defect_type", "")
            v_region = getattr(v_def, "region", "")

            # Buscar correspondencia en defectos geométricos
            matching_g = [g for g in geometric_defects if g.location in v_region or v_region in g.location]
            if matching_g:
                for g_def in matching_g:
                    correlations.append({
                        "visual_defect_id": getattr(v_def, "defect_id", "V_DEF"),
                        "geometric_defect_id": g_def.defect_id,
                        "correlation_strength": 0.95,
                        "shared_region": v_region,
                        "primary_culprit": "GEOMETRIC_DISCREPANCY"
                    })

        return correlations
