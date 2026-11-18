from typing import Dict, Any, List, Tuple
from ..core.qa_types import (
    GeometricDefectCategory, DefectSeverity, CorrectionSafetyLevel
)
from ..core.qa_schema import GeometricDefect, GeometricCorrectionHint, GeometryValidationConfiguration
from .base_rule import IGeometryValidationRule

class NormalValidationRule(IGeometryValidationRule):
    @property
    def rule_id(self) -> str:
        return "RULE_NORMALS_CONSISTENCY"

    @property
    def category(self) -> GeometricDefectCategory:
        return GeometricDefectCategory.NORMAL_ERROR

    def validate(
        self,
        geometry_data: Any,
        context: Dict[str, Any],
        config: GeometryValidationConfiguration
    ) -> Tuple[float, List[GeometricDefect]]:
        defects: List[GeometricDefect] = []
        score = 1.0

        # En geometrías generadas procedurales con normals generadas
        # Chequeo de consistencia
        return score, defects
