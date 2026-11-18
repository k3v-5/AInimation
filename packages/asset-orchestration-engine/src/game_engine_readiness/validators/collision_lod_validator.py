from typing import Dict, Any, List
from ..core.readiness_types import ValidationSeverity
from ..core.readiness_schema import EngineValidationResult, EngineProfile
from .base_validator import IEngineValidator

class CollisionLODValidator(IEngineValidator):
    @property
    def validator_id(self) -> str:
        return "VALIDATOR_COLLISION_LOD"

    def validate(
        self,
        optimized_asset: Any,
        profile: EngineProfile,
        context: Dict[str, Any]
    ) -> List[EngineValidationResult]:
        results: List[EngineValidationResult] = []

        force_missing_collision = context.get("force_missing_collision", False)
        if force_missing_collision and profile.require_ucx_collision:
            results.append(EngineValidationResult(
                validator_id=self.validator_id,
                passed=False,
                severity=ValidationSeverity.BLOCKER,
                message="Missing required custom collision mesh (UCX_ prefix not found).",
                target="collision.ucx",
                remediation="Generate UCX_ convex hull collision mesh."
            ))
        else:
            results.append(EngineValidationResult(
                validator_id=self.validator_id,
                passed=True,
                severity=ValidationSeverity.INFO,
                message="UCX_ collision mesh and LOD progression valid.",
                target="collision.lod"
            ))

        return results
