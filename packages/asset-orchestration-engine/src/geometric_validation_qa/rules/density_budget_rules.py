from typing import Dict, Any, List, Tuple
from ..core.qa_types import (
    GeometricDefectCategory, DefectSeverity, CorrectionSafetyLevel
)
from ..core.qa_schema import GeometricDefect, GeometricCorrectionHint, GeometryValidationConfiguration
from .base_rule import IGeometryValidationRule

class DensityBudgetRule(IGeometryValidationRule):
    @property
    def rule_id(self) -> str:
        return "RULE_DENSITY_POLYGON_BUDGET"

    @property
    def category(self) -> GeometricDefectCategory:
        return GeometricDefectCategory.DENSITY_ERROR

    def validate(
        self,
        geometry_data: Any,
        context: Dict[str, Any],
        config: GeometryValidationConfiguration
    ) -> Tuple[float, List[GeometricDefect]]:
        defects: List[GeometricDefect] = []
        score = 1.0

        tris = getattr(geometry_data, "triangle_count", 0)
        if tris > config.max_triangles:
            score -= 0.30
            defects.append(GeometricDefect(
                defect_id="DEF_GEO_POLY_BUDGET_EXCEEDED",
                category=GeometricDefectCategory.DENSITY_ERROR,
                severity=DefectSeverity.MAJOR,
                location="mesh.density",
                measurement=f"triangles={tris}",
                expected=f"max_triangles={config.max_triangles}",
                confidence=0.98,
                probable_cause="EXCESSIVE_TESSELLATION_OR_SUBDIVISION",
                correction_hint=GeometricCorrectionHint(
                    target="mesh.density",
                    operation="REDUCE_DENSITY",
                    magnitude=round((tris - config.max_triangles) / float(tris), 2),
                    safety_level=CorrectionSafetyLevel.SAFE_AUTOMATION
                )
            ))

        return max(0.0, score), defects
