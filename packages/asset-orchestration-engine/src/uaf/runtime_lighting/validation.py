"""
Semantic Validation & Sanitization for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List

from .lights import Light
from .spot import SpotLight
from .directional import DirectionalLight
from .postprocess import PostProcessSettings


@dataclass
class LightingValidationReport:
    """Outcome of validating lighting resources."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class LightingValidator:
    """
    Validates physical parameters, detects numeric anomalies, and enforces UAF-81.85 rules.
    """

    @staticmethod
    def validate_light(light: Light) -> LightingValidationReport:
        errors: List[str] = []
        warnings: List[str] = []

        # Check intensity
        if light.intensity < 0.0:
            errors.append(f"Light '{light.light_id.value}' has negative intensity: {light.intensity}")

        # Check range
        if light.range <= 0.0:
            errors.append(f"Light '{light.light_id.value}' has non-positive range: {light.range}")

        # Check direction
        dx, dy, dz = light.direction
        len_sq = dx * dx + dy * dy + dz * dz
        if abs(len_sq - 1.0) > 0.05:
            warnings.append(f"Light '{light.light_id.value}' direction is not unit length: len^2={len_sq:.4f}")

        # Check Kelvin
        if light.use_temperature and not (1000.0 <= light.temperature <= 40000.0):
            warnings.append(f"Light '{light.light_id.value}' temperature outside recommended 1000K-40000K range: {light.temperature}")

        # Spot light specific checks
        if isinstance(light, SpotLight):
            if light.inner_cone_angle > light.outer_cone_angle:
                errors.append(f"SpotLight '{light.light_id.value}' inner cone ({light.inner_cone_angle}) exceeds outer cone ({light.outer_cone_angle})")

        # Directional light specific checks
        if isinstance(light, DirectionalLight):
            if not (1 <= light.cascade_count <= 8):
                errors.append(f"DirectionalLight '{light.light_id.value}' invalid cascade count: {light.cascade_count}")

        return LightingValidationReport(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    @staticmethod
    def validate_postprocess(settings: PostProcessSettings) -> LightingValidationReport:
        errors: List[str] = []
        warnings: List[str] = []

        if settings.exposure.min_ev100 > settings.exposure.max_ev100:
            errors.append("Exposure min_ev100 cannot be greater than max_ev100.")

        if settings.dof.enabled and settings.dof.focus_distance <= 0.0:
            errors.append("Depth of Field focus_distance must be positive.")

        return LightingValidationReport(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)
