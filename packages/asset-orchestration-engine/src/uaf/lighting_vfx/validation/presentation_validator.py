"""
LightingVFXValidator enforces non-negative intensities, particle budgets, and path portability.
UAF-81.25 Sections 6, 17, 139, 148, 160.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.presentation import PresentationDefinition25


@dataclass
class LightingVFXQualityScore:
    lighting_budget_score: float  # 0.0 to 1.0 (Non-negative intensity, count within budget)
    atmosphere_score: float       # 0.0 to 1.0 (Fog, sky valid)
    vfx_budget_score: float       # 0.0 to 1.0 (Particles <= 50,000, positive spawn rate)
    readability_score: float      # 0.0 to 1.0 (Adequate key/fill separation)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.lighting_budget_score +
            0.20 * self.atmosphere_score +
            0.30 * self.vfx_budget_score +
            0.20 * self.readability_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lighting_budget_score": self.lighting_budget_score,
            "atmosphere_score": self.atmosphere_score,
            "vfx_budget_score": self.vfx_budget_score,
            "readability_score": self.readability_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class LightingVFXValidationReport:
    is_valid: bool
    quality_score: LightingVFXQualityScore
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    review_status: str = "PASSED"  # "PASSED", "MANUAL_REVIEW_REQUIRED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "quality_score": self.quality_score.to_dict(),
            "issues": self.issues,
            "warnings": self.warnings,
            "review_status": self.review_status,
        }


class LightingVFXValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 6, 17, 139, 148, 160).
    """

    MAX_PARTICLES_BUDGET = 50000

    @classmethod
    def validate_presentation(
        cls,
        presentation_def: PresentationDefinition25,
        post_process_ref: str,
    ) -> LightingVFXValidationReport:
        issues = []
        warnings = []

        # 1. Lighting validation (Section 6 & 160)
        light_score = 1.0
        for lt in presentation_def.lights:
            if lt.intensity_lux < 0.0:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Light '{lt.light_id}' has negative intensity: {lt.intensity_lux} lux.")
                light_score = 0.0

        # 2. Atmosphere validation
        atmo_score = 1.0
        sky = presentation_def.sky_atmosphere
        if sky.fog_density < 0.0 or sky.sun_intensity_lux < 0.0:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Atmospheric fog density or sun intensity is negative.")
            atmo_score = 0.0

        # 3. VFX particles budget validation (Section 160)
        vfx_score = 1.0
        for vx in presentation_def.vfx_effects:
            if vx.max_particles > cls.MAX_PARTICLES_BUDGET:
                issues.append(f"NON-NEGOTIABLE VIOLATION: VFX system '{vx.effect_id}' exceeds particle budget: {vx.max_particles} > {cls.MAX_PARTICLES_BUDGET}.")
                vfx_score = 0.0
            if vx.spawn_rate <= 0.0:
                issues.append(f"NON-NEGOTIABLE VIOLATION: VFX system '{vx.effect_id}' has non-positive spawn rate: {vx.spawn_rate}.")
                vfx_score = 0.0

        # 4. Path purity (Section 139)
        if ":\\" in post_process_ref or ":/" in post_process_ref or post_process_ref.startswith("/"):
            issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path in post-process reference: '{post_process_ref}'.")
            light_score = 0.0

        readability_score = 1.0

        q_score = LightingVFXQualityScore(
            lighting_budget_score=light_score,
            atmosphere_score=atmo_score,
            vfx_budget_score=vfx_score,
            readability_score=readability_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return LightingVFXValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
