"""
ModularArchitectureValidator enforces grid quantization, valid socket definitions, piece dimensions, and relative paths.
UAF-81.31 Sections 7, 12, 16, 125, 145.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import ModularArchitectureKitDefinition


@dataclass
class ModularArchitectureQualityScore:
    grid_score: float    # 0.0 to 1.0 (Grid size >= 100cm)
    socket_score: float  # 0.0 to 1.0 (All pieces declare sockets)
    piece_score: float   # 0.0 to 1.0 (All piece dimensions strictly positive)
    kit_score: float     # 0.0 to 1.0 (Mesh refs match piece count)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.grid_score +
            0.25 * self.socket_score +
            0.25 * self.piece_score +
            0.25 * self.kit_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_score": self.grid_score,
            "socket_score": self.socket_score,
            "piece_score": self.piece_score,
            "kit_score": self.kit_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class ModularArchitectureValidationReport:
    is_valid: bool
    quality_score: ModularArchitectureQualityScore
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


class ModularArchitectureValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 7, 12, 16, 125).
    """

    @classmethod
    def validate_architecture_kit(
        cls,
        kit_def: ModularArchitectureKitDefinition,
        static_mesh_refs: List[str],
        master_material_ref: str,
    ) -> ModularArchitectureValidationReport:
        issues = []
        warnings = []

        # 1. Grid unit check (Section 7 & 125)
        grid_score = 1.0
        if not kit_def.is_valid_grid:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Kit grid unit {kit_def.grid_unit_cm}cm is below the 100.0cm threshold.")
            grid_score = 0.0

        # 2. Pieces & dimensions check (Section 125)
        piece_score = 1.0
        socket_score = 1.0
        if not kit_def.pieces:
            issues.append("NON-NEGOTIABLE VIOLATION: Kit definition contains zero modular pieces.")
            piece_score = 0.0

        for p in kit_def.pieces:
            if not p.is_valid:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Modular piece '{p.piece_id}' has invalid or non-positive dimensions: {p.dimensions_cm}.")
                piece_score = 0.0
            if not p.sockets:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Modular piece '{p.piece_id}' defines zero snapping sockets.")
                socket_score = 0.0

        # 3. Mesh references matching check
        kit_score = 1.0
        if len(static_mesh_refs) != len(kit_def.pieces):
            issues.append(f"NON-NEGOTIABLE VIOLATION: Mesh references count ({len(static_mesh_refs)}) does not match piece count ({len(kit_def.pieces)}).")
            kit_score = 0.0

        # 4. Path purity check (Section 125)
        for ref in static_mesh_refs + [master_material_ref]:
            if ":\\" in ref or ":/" in ref or ref.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path detected: '{ref}'.")
                kit_score = 0.0

        q_score = ModularArchitectureQualityScore(
            grid_score=grid_score,
            socket_score=socket_score,
            piece_score=piece_score,
            kit_score=kit_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return ModularArchitectureValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
