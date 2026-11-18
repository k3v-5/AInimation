from typing import Dict, Any, List, Tuple
from ..core.qa_types import (
    GeometricDefectCategory, DefectSeverity, CorrectionSafetyLevel
)
from ..core.qa_schema import GeometricDefect, GeometricCorrectionHint, GeometryValidationConfiguration
from .base_rule import IGeometryValidationRule

class TopologyValidationRule(IGeometryValidationRule):
    @property
    def rule_id(self) -> str:
        return "RULE_TOPOLOGY_MANIFOLD_DEGENERACY"

    @property
    def category(self) -> GeometricDefectCategory:
        return GeometricDefectCategory.TOPOLOGY_ERROR

    def validate(
        self,
        geometry_data: Any,
        context: Dict[str, Any],
        config: GeometryValidationConfiguration
    ) -> Tuple[float, List[GeometricDefect]]:
        defects: List[GeometricDefect] = []
        score = 1.0

        top_summary = getattr(geometry_data, "topology_summary", None)
        is_manifold = getattr(top_summary, "is_manifold", True) if top_summary else True
        degen_faces = getattr(top_summary, "degenerate_faces", 0) if top_summary else 0
        ngons = getattr(top_summary, "ngon_count", 0) if top_summary else 0

        # 1. Non-Manifold check
        if not is_manifold:
            score -= 0.35
            defects.append(GeometricDefect(
                defect_id="DEF_GEO_NON_MANIFOLD",
                category=GeometricDefectCategory.NON_MANIFOLD,
                severity=DefectSeverity.CRITICAL,
                location="mesh.topology",
                measurement="is_manifold=False",
                expected="is_manifold=True",
                confidence=0.99,
                probable_cause="NON_MANIFOLD_EDGES_OR_VERTICES",
                correction_hint=GeometricCorrectionHint(
                    target="mesh.topology",
                    operation="REPAIR_BOUNDARY",
                    safety_level=CorrectionSafetyLevel.REQUIRES_REVIEW
                )
            ))

        # 2. Degenerate Faces check
        if degen_faces > 0:
            score -= 0.25
            defects.append(GeometricDefect(
                defect_id="DEF_GEO_DEGENERATE_FACES",
                category=GeometricDefectCategory.DEGENERATE_GEOMETRY,
                severity=DefectSeverity.MAJOR,
                location="mesh.faces",
                affected_elements=[f"face_{i}" for i in range(degen_faces)],
                measurement=f"count={degen_faces}",
                expected="count=0",
                confidence=0.98,
                probable_cause="ZERO_AREA_OR_COLLAPSED_POLYGONS",
                correction_hint=GeometricCorrectionHint(
                    target="mesh.faces",
                    operation="MERGE_VERTICES",
                    magnitude=0.001,
                    safety_level=CorrectionSafetyLevel.SAFE_AUTOMATION
                )
            ))

        return max(0.0, score), defects
