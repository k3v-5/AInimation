from typing import List, Dict, Any, Optional
from ..core.evaluation_types import (
    DefectType, DefectSeverity, DefectCauseCategory, EvaluationCategory
)
from ..core.evaluation_schema import VisualDefect, CorrectionHint, CategoryEvaluation

class DefectDetector:
    @classmethod
    def detect_defects(
        cls,
        category_evals: Dict[str, CategoryEvaluation],
        reference_data: Optional[Any],
        generated_data: Optional[Any],
        context: Dict[str, Any]
    ) -> List[VisualDefect]:
        defects: List[VisualDefect] = []

        # 1. Chequeo de Silueta
        sil_eval = category_evals.get(EvaluationCategory.SILHOUETTE.value)
        if sil_eval and sil_eval.score < 0.85:
            d = VisualDefect(
                defect_id=f"DEFECT_SIL_{len(defects)+1}",
                defect_type=DefectType.WRONG_SILHOUETTE,
                severity=DefectSeverity.MAJOR if sil_eval.score < 0.70 else DefectSeverity.MODERATE,
                region="asset.silhouette",
                semantic_id="asset.root",
                bbox=(0.1, 0.1, 0.9, 0.9),
                score=sil_eval.score,
                confidence=0.92,
                expected="Aspect Ratio 1.42",
                actual=f"Measured Aspect Ratio Error: {sil_eval.metrics.get('aspect_ratio_error', 0.15)}",
                error_pct=round(sil_eval.metrics.get("aspect_ratio_error", 0.15) * 100.0, 1),
                probable_causes={DefectCauseCategory.GEOMETRY.value: 0.85, DefectCauseCategory.CAMERA.value: 0.15},
                correction_hint=CorrectionHint(
                    target="asset.root",
                    parameter="aspect_ratio",
                    direction="MODIFY",
                    magnitude=0.08,
                    priority=0.88,
                    expected_score_gain=0.12
                )
            )
            defects.append(d)

        # 2. Chequeo de Proporciones y Componentes Faltantes
        prop_eval = category_evals.get(EvaluationCategory.PROPORTION.value)
        if prop_eval and prop_eval.score < 0.80:
            d = VisualDefect(
                defect_id=f"DEFECT_PROP_{len(defects)+1}",
                defect_type=DefectType.WRONG_PROPORTION,
                severity=DefectSeverity.MAJOR,
                region="component.body",
                semantic_id="asset.root",
                score=prop_eval.score,
                confidence=0.90,
                expected="Width ratio 0.80",
                actual="Width ratio deviation",
                error_pct=round(prop_eval.metrics.get("width_error", 0.10) * 100.0, 1),
                probable_causes={DefectCauseCategory.GEOMETRY.value: 0.92},
                correction_hint=CorrectionHint(
                    target="component.body",
                    parameter="width",
                    direction="MODIFY",
                    magnitude=0.05,
                    priority=0.84,
                    expected_score_gain=0.10
                )
            )
            defects.append(d)

        # 3. Chequeo de Materiales
        mat_eval = category_evals.get(EvaluationCategory.MATERIAL.value)
        if mat_eval and mat_eval.score < 0.80:
            d = VisualDefect(
                defect_id=f"DEFECT_MAT_{len(defects)+1}",
                defect_type=DefectType.WRONG_MATERIAL,
                severity=DefectSeverity.MODERATE,
                region="surface.wood",
                semantic_id="asset.root",
                score=mat_eval.score,
                confidence=0.88,
                expected="Roughness 0.68",
                actual="Roughness deviation",
                error_pct=round(mat_eval.metrics.get("roughness_error", 0.08) * 100.0, 1),
                probable_causes={DefectCauseCategory.MATERIAL.value: 0.90, DefectCauseCategory.LIGHTING.value: 0.10},
                correction_hint=CorrectionHint(
                    target="surface.wood",
                    parameter="roughness",
                    direction="DECREASE" if mat_eval.metrics.get("roughness_error", 0) > 0 else "INCREASE",
                    magnitude=0.04,
                    priority=0.75,
                    expected_score_gain=0.08
                )
            )
            defects.append(d)

        return defects
