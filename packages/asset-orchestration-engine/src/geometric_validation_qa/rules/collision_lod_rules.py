from typing import Dict, Any, List, Tuple
from ..core.qa_types import (
    GeometricDefectCategory, DefectSeverity, CorrectionSafetyLevel
)
from ..core.qa_schema import GeometricDefect, GeometricCorrectionHint, GeometryValidationConfiguration
from .base_rule import IGeometryValidationRule

class CollisionLODRule(IGeometryValidationRule):
    @property
    def rule_id(self) -> str:
        return "RULE_COLLISION_AND_LOD_QA"

    @property
    def category(self) -> GeometricDefectCategory:
        return GeometricDefectCategory.COLLISION_ERROR

    def validate(
        self,
        geometry_data: Any,
        context: Dict[str, Any],
        config: GeometryValidationConfiguration
    ) -> Tuple[float, List[GeometricDefect]]:
        defects: List[GeometricDefect] = []
        score = 1.0

        col_mesh = getattr(geometry_data, "collision_geometry", None) or getattr(geometry_data, "collision_mesh", None)
        if not col_mesh:
            score -= 0.15
            defects.append(GeometricDefect(
                defect_id="DEF_GEO_MISSING_COLLISION_UCX",
                category=GeometricDefectCategory.COLLISION_ERROR,
                severity=DefectSeverity.MODERATE,
                location="mesh.collision",
                measurement="collision_mesh=None",
                expected="UCX_CollisionMesh",
                confidence=0.95,
                probable_cause="COLLISION_MESH_NOT_GENERATED",
                correction_hint=GeometricCorrectionHint(
                    target="mesh.collision",
                    operation="REPAIR_BOUNDARY",
                    safety_level=CorrectionSafetyLevel.SAFE_AUTOMATION
                )
            ))

        return max(0.0, score), defects
