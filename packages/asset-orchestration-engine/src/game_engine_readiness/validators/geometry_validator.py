from typing import Dict, Any, List
from ..core.readiness_types import ValidationSeverity
from ..core.readiness_schema import EngineValidationResult, EngineProfile
from .base_validator import IEngineValidator

class GeometryValidator(IEngineValidator):
    @property
    def validator_id(self) -> str:
        return "VALIDATOR_GEOMETRY"

    def validate(
        self,
        optimized_asset: Any,
        profile: EngineProfile,
        context: Dict[str, Any]
    ) -> List[EngineValidationResult]:
        results: List[EngineValidationResult] = []
        cost = getattr(optimized_asset, "optimized_cost", None)
        tris = getattr(cost, "triangle_count", 68) if cost else 68

        if tris > profile.max_triangle_count:
            results.append(EngineValidationResult(
                validator_id=self.validator_id,
                passed=False,
                severity=ValidationSeverity.BLOCKER,
                message=f"Triangle count ({tris}) exceeds engine profile limit ({profile.max_triangle_count}).",
                target="mesh.geometry",
                remediation="Apply decimation in F67 before export."
            ))
        else:
            results.append(EngineValidationResult(
                validator_id=self.validator_id,
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"Geometry triangle count ({tris}) within engine budget.",
                target="mesh.geometry"
            ))

        return results
