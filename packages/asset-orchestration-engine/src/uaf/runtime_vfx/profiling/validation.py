"""
UAF-81.84.11: VFX Semantic and Integrity Validation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from ..emitter.emitter import VFXEmitter
from ..models.definition import VFXValidationError


@dataclass(frozen=True)
class VFXValidationIssue:
    severity: str  # "ERROR", "WARNING"
    code: str
    message: str
    context: str = ""


class VFXValidator:
    """Validates emitter configurations, capacities, and numeric invariants."""

    @classmethod
    def validate_emitter(cls, emitter: VFXEmitter) -> List[VFXValidationIssue]:
        issues: List[VFXValidationIssue] = []
        cfg = emitter.config

        if cfg.max_capacity <= 0:
            issues.append(
                VFXValidationIssue(
                    "ERROR",
                    "VFX_INVALID_CAPACITY",
                    f"Emitter {cfg.emitter_id} max_capacity must be > 0, got {cfg.max_capacity}",
                    cfg.emitter_id,
                )
            )

        if cfg.lifetime_min < 0.0 or cfg.lifetime_max < cfg.lifetime_min:
            issues.append(
                VFXValidationIssue(
                    "ERROR",
                    "VFX_INVALID_LIFETIME",
                    f"Emitter {cfg.emitter_id} invalid lifetime bounds [{cfg.lifetime_min}, {cfg.lifetime_max}]",
                    cfg.emitter_id,
                )
            )

        for idx, c in enumerate(cfg.initial_position):
            if math.isnan(c) or math.isinf(c):
                issues.append(
                    VFXValidationIssue(
                        "ERROR",
                        "VFX_NUMERIC_ERROR",
                        f"Emitter {cfg.emitter_id} non-finite initial_position[{idx}]={c}",
                        cfg.emitter_id,
                    )
                )

        return issues
