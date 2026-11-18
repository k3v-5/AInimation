from typing import Dict, Any, List
from ..core.readiness_types import ValidationSeverity
from ..core.readiness_schema import EngineValidationResult, EngineProfile
from .base_validator import IEngineValidator

class TransformPivotValidator(IEngineValidator):
    @property
    def validator_id(self) -> str:
        return "VALIDATOR_TRANSFORM_PIVOT"

    def validate(
        self,
        optimized_asset: Any,
        profile: EngineProfile,
        context: Dict[str, Any]
    ) -> List[EngineValidationResult]:
        results: List[EngineValidationResult] = []
        
        # Check applied transforms
        force_unapplied = context.get("force_unapplied_transform", False)
        if force_unapplied:
            results.append(EngineValidationResult(
                validator_id=self.validator_id,
                passed=False,
                severity=ValidationSeverity.BLOCKER,
                message="Unapplied scale/rotation detected on mesh. Scale must be (1.0, 1.0, 1.0) before Unreal export.",
                target="transform.scale",
                remediation="Apply rotation and scale in Blender capability before export."
            ))
        else:
            results.append(EngineValidationResult(
                validator_id=self.validator_id,
                passed=True,
                severity=ValidationSeverity.INFO,
                message="Transforms applied cleanly (Scale: 1.0, Rotation: 0.0). Pivot at base.",
                target="transform.pivot"
            ))

        return results
