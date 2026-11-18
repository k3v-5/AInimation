"""
Universal Animation Validator & Quality Score.
UAF-81.55 Sections 6, 18, 41, 42, 87, 102, 113, 114, 115, 117, 118, 121, 158, 174.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re

from ..models.definition import (
    AnimationDefinition,
    RetargetProfile55,
    AnimationCompressionProfile55,
    AnimationStateMachine55,
    RuntimeProfile55,
)


@dataclass
class AnimationQualityScore:
    track_timing_score: float = 1.0     # 0.0 to 1.0
    retarget_score: float = 1.0         # 0.0 to 1.0
    foot_slide_score: float = 1.0       # 0.0 to 1.0
    compression_score: float = 1.0      # 0.0 to 1.0
    runtime_budget_score: float = 1.0   # 0.0 to 1.0
    export_score: float = 1.0           # 0.0 to 1.0

    @property
    def aggregate_score(self) -> float:
        return round(
            0.20 * self.track_timing_score +
            0.20 * self.retarget_score +
            0.15 * self.foot_slide_score +
            0.15 * self.compression_score +
            0.15 * self.runtime_budget_score +
            0.15 * self.export_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_timing_score": self.track_timing_score,
            "retarget_score": self.retarget_score,
            "foot_slide_score": self.foot_slide_score,
            "compression_score": self.compression_score,
            "runtime_budget_score": self.runtime_budget_score,
            "export_score": self.export_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class AnimationValidationReport:
    is_valid: bool
    quality_score: AnimationQualityScore
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    review_status: str = "PASSED"  # "PASSED", "WARNING", "FAILED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "quality_score": self.quality_score.to_dict(),
            "issues": self.issues,
            "warnings": self.warnings,
            "review_status": self.review_status,
        }


class UniversalAnimationValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS & RUNTIME QUALITY GATES (Sections 121, 158, 174).
    """

    MACHINE_PATH_PATTERN = re.compile(r"^[A-Za-z]:[\\/]", re.IGNORECASE)

    @classmethod
    def validate_animation(
        cls,
        animation: AnimationDefinition,
        retarget: Optional[RetargetProfile55] = None,
        state_machine: Optional[AnimationStateMachine55] = None,
        compression: Optional[AnimationCompressionProfile55] = None,
        runtime_profile: Optional[RuntimeProfile55] = None,
        export_path: str = "/Game/Animations/Anim_Default.uasset",
    ) -> AnimationValidationReport:
        issues = []
        warnings = []

        timing_score = 1.0
        retarget_score = 1.0
        slide_score = 1.0
        comp_score = 1.0
        runtime_score = 1.0
        export_score = 1.0

        # 1. TIMING & TRACKS (Sections 3, 6, 158)
        if not animation.is_valid:
            issues.append("HARD FAIL CONDITION: INVALID_ANIMATION: Animation definition, duration, or sample rate invalid.")
            timing_score = 0.0

        if animation.duration <= 0.0:
            issues.append(f"HARD FAIL CONDITION: INVALID_DURATION: Duration {animation.duration}s must be strictly positive.")
            timing_score = 0.0

        if animation.sample_rate <= 0:
            issues.append(f"HARD FAIL CONDITION: INVALID_SAMPLE_RATE: Sample rate {animation.sample_rate}Hz must be positive.")
            timing_score = 0.0

        if len(animation.tracks) == 0:
            issues.append("HARD FAIL CONDITION: EMPTY_TRACKS: Animation must contain at least one track.")
            timing_score = 0.0

        for t in animation.tracks:
            if len(t.keyframes) == 0:
                issues.append(f"HARD FAIL CONDITION: INVALID_TRACK: Track for bone '{t.bone_name}' has 0 keyframes.")
                timing_score = 0.0
                break

        # 2. RETARGETING (Sections 25-44, 158)
        if retarget is not None:
            if not retarget.source_skeleton or not retarget.target_skeleton:
                issues.append("HARD FAIL CONDITION: INVALID_RETARGET: Missing source or target skeleton in retarget profile.")
                retarget_score = 0.0

            if len(retarget.bone_mapping) == 0:
                issues.append("HARD FAIL CONDITION: MISSING_RETARGET_BONE: Bone mapping is empty.")
                retarget_score = 0.0

            # Check for ambiguous mapping (multiple targets mapped to same source incorrectly)
            seen_targets = set()
            for src, tgt in retarget.bone_mapping.items():
                if tgt in seen_targets:
                    issues.append(f"HARD FAIL CONDITION: AMBIGUOUS_RETARGET: Target bone '{tgt}' mapped multiple times.")
                    retarget_score = 0.0
                    break
                seen_targets.add(tgt)

        # 3. STATE MACHINE CYCLES (Sections 74-79, 158)
        if state_machine is not None:
            if not state_machine.allow_cycles and state_machine.has_cycle():
                issues.append(f"HARD FAIL CONDITION: STATE_MACHINE_CYCLE: Cycle detected in state machine '{state_machine.machine_id}'.")
                timing_score = 0.0

        # 4. COMPRESSION & BUDGETS (Sections 98-102, 158)
        if compression is not None:
            if compression.max_error_cm > 0.5:
                warnings.append(f"High compression error tolerance: {compression.max_error_cm}cm.")
                comp_score = 0.7

            if compression.compressed_size_kb > compression.budget_kb:
                issues.append(f"HARD FAIL CONDITION: INVALID_COMPRESSION: Compressed size {compression.compressed_size_kb}KB exceeds budget {compression.budget_kb}KB.")
                comp_score = 0.0

        # 5. RUNTIME BUDGETS (Sections 119-122, 158)
        if runtime_profile is not None:
            if runtime_profile.memory_budget_mb <= 0.0:
                issues.append("HARD FAIL CONDITION: RUNTIME_BUDGET_FAILURE: Non-positive memory budget.")
                runtime_score = 0.0

        # 6. EXPORT PATH PURITY (Sections 130, 158, 174)
        if cls.MACHINE_PATH_PATTERN.match(export_path):
            issues.append(
                f"HARD FAIL CONDITION: MACHINE_DEPENDENT_PATH: Absolute path '{export_path}' detected. "
                "Unreal animation engine must use agnostic package paths (/Game/...)."
            )
            export_score = 0.0

        if not export_path.startswith("/Game/"):
            warnings.append(f"Non-standard export path '{export_path}' (expected /Game/...).")

        is_valid = len(issues) == 0
        review_status = "PASSED" if is_valid and len(warnings) == 0 else ("WARNING" if is_valid else "FAILED")

        quality_score = AnimationQualityScore(
            track_timing_score=timing_score,
            retarget_score=retarget_score,
            foot_slide_score=slide_score,
            compression_score=comp_score,
            runtime_budget_score=runtime_score,
            export_score=export_score,
        )

        return AnimationValidationReport(
            is_valid=is_valid,
            quality_score=quality_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
