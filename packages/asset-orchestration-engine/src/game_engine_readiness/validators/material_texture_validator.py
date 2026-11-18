from typing import Dict, Any, List
from ..core.readiness_types import ValidationSeverity
from ..core.readiness_schema import EngineValidationResult, EngineProfile
from .base_validator import IEngineValidator

class MaterialTextureValidator(IEngineValidator):
    @property
    def validator_id(self) -> str:
        return "VALIDATOR_MATERIAL_TEXTURE"

    def validate(
        self,
        optimized_asset: Any,
        profile: EngineProfile,
        context: Dict[str, Any]
    ) -> List[EngineValidationResult]:
        results: List[EngineValidationResult] = []
        cost = getattr(optimized_asset, "optimized_cost", None)
        mats = getattr(cost, "material_count", 1) if cost else 1

        if mats > profile.max_material_slots:
            results.append(EngineValidationResult(
                validator_id=self.validator_id,
                passed=False,
                severity=ValidationSeverity.WARNING,
                message=f"Material slots count ({mats}) is higher than recommended ({profile.max_material_slots}).",
                target="materials.slots",
                remediation="Consolidate materials to reduce draw calls."
            ))
        else:
            results.append(EngineValidationResult(
                validator_id=self.validator_id,
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"Material slot count ({mats}) valid for Unreal Engine.",
                target="materials.slots"
            ))

        return results
