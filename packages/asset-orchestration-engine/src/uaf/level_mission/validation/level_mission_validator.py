"""
LevelMissionValidator enforces flow continuity, valid player spawns, checkpoint safety, and path purity.
UAF-81.41 Sections 11, 19, 137, 155, 157, 158.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import PlayableLevelSpecification


@dataclass
class LevelMissionQualityScore:
    flow_score: float         # 0.0 to 1.0 (objectives >= 1, valid start, valid end)
    player_start_score: float # 0.0 to 1.0 (valid player start flag)
    encounter_score: float    # 0.0 to 1.0 (checkpoints >= 1, ai_spaces >= 1)
    unreal_score: float       # 0.0 to 1.0 (valid mission graph & gameplay package paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.flow_score +
            0.25 * self.player_start_score +
            0.25 * self.encounter_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flow_score": self.flow_score,
            "player_start_score": self.player_start_score,
            "encounter_score": self.encounter_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class LevelMissionValidationReport:
    is_valid: bool
    quality_score: LevelMissionQualityScore
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


class LevelMissionValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 11, 155, 158).
    """

    @classmethod
    def validate_playable_level(
        cls,
        spec: PlayableLevelSpecification,
        mission_graph_path: str,
        gameplay_package_path: str,
    ) -> LevelMissionValidationReport:
        issues = []
        warnings = []

        # 1. Mission flow & objective validation (Section 11, 158)
        flow_score = 1.0
        if spec.metrics.primary_objective_count < 1:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_MISSION_FLOW: primary_objective_count={spec.metrics.primary_objective_count} < 1."
            )
            flow_score = 0.0
        if not spec.metrics.has_extraction_or_end:
            issues.append("HARD FAIL CONDITION: INVALID_MISSION_FLOW: Missing extraction or terminal mission node (DEAD_END).")
            flow_score = 0.0

        # 2. Player start validation (Section 19, 158)
        start_score = 1.0
        if not spec.metrics.has_valid_player_start:
            issues.append("HARD FAIL CONDITION: INVALID_PLAYER_START: Missing or invalid player start spawn.")
            start_score = 0.0

        # 3. Checkpoint & Encounter safety (Section 23, 155, 158)
        enc_score = 1.0
        if spec.metrics.checkpoint_count < 1:
            issues.append(
                f"HARD FAIL CONDITION: ZERO_CHECKPOINTS: checkpoint_count={spec.metrics.checkpoint_count} < 1 (SOFTLOCK RISK)."
            )
            enc_score = 0.0
        if spec.ai_spaces_count < 1:
            issues.append(f"HARD FAIL CONDITION: INVALID_AI_SPACES: ai_spaces_count={spec.ai_spaces_count} < 1.")
            enc_score = 0.0

        # 4. Path purity check (Section 166)
        unreal_score = 1.0
        for p in [mission_graph_path, gameplay_package_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = LevelMissionQualityScore(
            flow_score=flow_score,
            player_start_score=start_score,
            encounter_score=enc_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return LevelMissionValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
