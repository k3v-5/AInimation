from typing import Dict, Any, List, Tuple
from ..core.qa_types import (
    GeometricDefectCategory, DefectSeverity, CorrectionSafetyLevel
)
from ..core.qa_schema import GeometricDefect, GeometricCorrectionHint, GeometryValidationConfiguration
from .base_rule import IGeometryValidationRule

class TransformDimensionRule(IGeometryValidationRule):
    @property
    def rule_id(self) -> str:
        return "RULE_TRANSFORM_SCALE_DIMENSIONS"

    @property
    def category(self) -> GeometricDefectCategory:
        return GeometricDefectCategory.TRANSFORM_ERROR

    def validate(
        self,
        geometry_data: Any,
        context: Dict[str, Any],
        config: GeometryValidationConfiguration
    ) -> Tuple[float, List[GeometricDefect]]:
        defects: List[GeometricDefect] = []
        score = 1.0

        geom_objs = getattr(geometry_data, "geometry_objects", [])
        for obj in geom_objs:
            s_x, s_y, s_z = getattr(obj, "scale", (1.0, 1.0, 1.0))
            if s_x < 0 or s_y < 0 or s_z < 0:
                score -= 0.30
                defects.append(GeometricDefect(
                    defect_id=f"DEF_GEO_NEGATIVE_SCALE_{getattr(obj, 'object_id', 'OBJ')}",
                    category=GeometricDefectCategory.SCALE_ERROR,
                    severity=DefectSeverity.CRITICAL,
                    location=getattr(obj, "name", "SM_Object"),
                    component_id=getattr(obj, "semantic_component_id", "comp_main"),
                    measurement=f"scale=({s_x}, {s_y}, {s_z})",
                    expected="scale >= 0.0",
                    confidence=0.99,
                    probable_cause="NEGATIVE_TRANSFORM_SCALE",
                    correction_hint=GeometricCorrectionHint(
                        target=getattr(obj, "name", "SM_Object"),
                        operation="APPLY_TRANSFORM",
                        safety_level=CorrectionSafetyLevel.SAFE_AUTOMATION
                    )
                ))
            elif not config.allow_unapplied_transforms and (s_x != 1.0 or s_y != 1.0 or s_z != 1.0):
                score -= 0.15
                defects.append(GeometricDefect(
                    defect_id=f"DEF_GEO_UNAPPLIED_SCALE_{getattr(obj, 'object_id', 'OBJ')}",
                    category=GeometricDefectCategory.TRANSFORM_ERROR,
                    severity=DefectSeverity.MODERATE,
                    location=getattr(obj, "name", "SM_Object"),
                    component_id=getattr(obj, "semantic_component_id", "comp_main"),
                    measurement=f"scale=({s_x}, {s_y}, {s_z})",
                    expected="scale=(1.0, 1.0, 1.0)",
                    confidence=0.95,
                    probable_cause="TRANSFORM_NOT_APPLIED",
                    correction_hint=GeometricCorrectionHint(
                        target=getattr(obj, "name", "SM_Object"),
                        operation="APPLY_TRANSFORM",
                        safety_level=CorrectionSafetyLevel.SAFE_AUTOMATION
                    )
                ))

        return max(0.0, score), defects
