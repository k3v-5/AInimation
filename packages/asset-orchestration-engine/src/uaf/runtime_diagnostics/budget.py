"""
Frame Budget Manager & Dynamic Budget Negotiation for UAF-81.86.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .core import SubsystemType, ensure_finite_scalar


@dataclass
class SubsystemBudget:
    """Budget limits for a single subsystem in milliseconds."""
    subsystem: SubsystemType
    allocated_ms: float
    soft_limit_ms: float
    warning_limit_ms: float
    hard_limit_ms: float
    emergency_limit_ms: float

    @property
    def target_ms(self) -> float:
        return self.allocated_ms


class FrameBudgetManager:
    """
    Manages total frame time budgets (e.g. 16.67ms @ 60 FPS, 8.33ms @ 120 FPS),
    distributes subsystem allocations, dynamically negotiates unused time slices,
    and escalates degradation policies under load.
    """

    def __init__(self, target_fps: float = 60.0) -> None:
        self.target_fps = max(15.0, float(target_fps))
        self.target_frame_ms = 1000.0 / self.target_fps
        self.budgets: Dict[SubsystemType, SubsystemBudget] = {}
        self._current_frame_usages: Dict[SubsystemType, float] = {}
        self._last_severity: str = "NORMAL"
        self._init_default_budgets()

    @property
    def total_budget_ms(self) -> float:
        return self.target_frame_ms

    def begin_frame(self) -> None:
        self._current_frame_usages = {}

    def record_duration(self, subsystem: SubsystemType, duration_ms: float) -> None:
        self._current_frame_usages[subsystem] = ensure_finite_scalar(duration_ms, "duration_ms", 0.0)

    def _init_default_budgets(self) -> None:
        # Standard 16.67ms allocation table
        scale = (1000.0 / self.target_fps) / 16.67
        allocations = {
            SubsystemType.PHYSICS: 2.00 * scale,
            SubsystemType.AI: 1.50 * scale,
            SubsystemType.ANIMATION: 1.00 * scale,
            SubsystemType.VFX: 1.00 * scale,
            SubsystemType.LIGHTING: 1.50 * scale,
            SubsystemType.AUDIO: 0.50 * scale,
            SubsystemType.STREAMING: 1.00 * scale,
            SubsystemType.GAMEPLAY: 2.00 * scale,
            SubsystemType.RENDERING: 5.00 * scale,
            SubsystemType.NETWORKING: 0.50 * scale,
            SubsystemType.UI: 0.50 * scale,
            SubsystemType.TELEMETRY: 0.17 * scale,
        }
        for sub, alloc in allocations.items():
            self.budgets[sub] = SubsystemBudget(
                subsystem=sub,
                allocated_ms=round(alloc, 3),
                soft_limit_ms=round(alloc * 1.1, 3),
                warning_limit_ms=round(alloc * 1.3, 3),
                hard_limit_ms=round(alloc * 1.6, 3),
                emergency_limit_ms=round(alloc * 2.0, 3),
            )

    def set_target_fps(self, fps: float) -> None:
        self.target_fps = max(15.0, float(fps))
        self.target_frame_ms = 1000.0 / self.target_fps
        self._init_default_budgets()

    def negotiate_budgets(
        self,
        actual_usages_ms: Optional[Dict[SubsystemType, float]] = None
    ) -> Dict[SubsystemType, float]:
        """
        Dynamically redistributes unused budget from under-budget subsystems
        to subsystems currently experiencing high demand.
        """
        usages = actual_usages_ms if actual_usages_ms is not None else self._current_frame_usages
        adjusted: Dict[SubsystemType, float] = {}
        unused_pool = 0.0
        deficit_subsystems: List[Tuple[SubsystemType, float]] = []

        for sub, b in self.budgets.items():
            used = usages.get(sub, 0.0)
            if used < b.allocated_ms:
                unused = b.allocated_ms - used
                unused_pool += unused
                adjusted[sub] = b.allocated_ms
            else:
                deficit = used - b.allocated_ms
                deficit_subsystems.append((sub, deficit))
                adjusted[sub] = b.allocated_ms

        if deficit_subsystems and unused_pool > 0.0:
            total_deficit = sum(d for _, d in deficit_subsystems)
            for sub, deficit in deficit_subsystems:
                share = (deficit / max(1e-4, total_deficit)) * unused_pool
                adjusted[sub] += round(share, 3)

        return adjusted

    def evaluate_frame_state(
        self,
        actual_usages_ms: Dict[SubsystemType, float]
    ) -> Tuple[str, List[str]]:
        """
        Evaluates overall frame performance and detects violations.
        Returns severity ('NORMAL', 'WARNING', 'DEGRADATION', 'EMERGENCY') and violation messages.
        """
        violations: List[str] = []
        total_used = sum(actual_usages_ms.values())
        max_severity = "NORMAL"

        for sub, used in actual_usages_ms.items():
            b = self.budgets.get(sub)
            if not b:
                continue

            if used >= b.emergency_limit_ms:
                violations.append(f"{sub.value} exceeded EMERGENCY limit ({used:.2f}ms >= {b.emergency_limit_ms:.2f}ms)")
                max_severity = "EMERGENCY"
            elif used >= b.hard_limit_ms:
                violations.append(f"{sub.value} exceeded HARD limit ({used:.2f}ms >= {b.hard_limit_ms:.2f}ms)")
                if max_severity != "EMERGENCY":
                    max_severity = "DEGRADATION"
            elif used >= b.warning_limit_ms:
                violations.append(f"{sub.value} exceeded WARNING limit ({used:.2f}ms >= {b.warning_limit_ms:.2f}ms)")
                if max_severity not in ("EMERGENCY", "DEGRADATION"):
                    max_severity = "WARNING"

        if total_used > self.target_frame_ms and max_severity == "NORMAL":
            violations.append(f"Total frame time exceeded target ({total_used:.2f}ms > {self.target_frame_ms:.2f}ms)")
            max_severity = "WARNING"

        return (max_severity, violations)

    def request_quality_degradations(self, severity: str) -> List[str]:
        """
        Recommends safe, non-destructive quality reductions based on budget overload severity.
        """
        if severity == "NORMAL":
            return []
        elif severity == "WARNING":
            return ["reduce_vfx_particles", "reduce_streaming_prefetch"]
        elif severity == "DEGRADATION":
            return [
                "reduce_shadow_quality",
                "reduce_vfx_particles",
                "reduce_ai_frequency",
                "reduce_animation_update",
                "reduce_volumetric_quality",
                "reduce_streaming_prefetch",
                "reduce_postprocess",
            ]
        else:  # EMERGENCY
            return [
                "disable_contact_shadows",
                "halve_shadow_resolution",
                "cull_cosmetic_vfx",
                "throttle_distant_ai",
                "disable_volumetrics",
                "disable_expensive_postprocess",
                "preserve_gameplay_critical",
            ]

    def end_frame(self, total_frame_ms: Optional[float] = None) -> Dict[str, Any]:
        usages = getattr(self, "_current_frame_usages", {})
        total = total_frame_ms if total_frame_ms is not None else sum(usages.values())
        eval_usages = dict(usages) if usages else {SubsystemType.RENDERING: total}
        severity, violations = self.evaluate_frame_state(eval_usages)
        is_overrun = total > self.target_frame_ms or len(violations) > 0
        self._last_severity = severity
        return {
            "total_frame_ms": total,
            "target_frame_ms": self.target_frame_ms,
            "is_overrun": is_overrun,
            "severity": severity,
            "violations": violations,
            "subsystems": {k.value: v for k, v in usages.items()},
        }

    def get_degradation_recommendation(self) -> Dict[str, Any]:
        severity = getattr(self, "_last_severity", "NORMAL")
        tier_map = {"NORMAL": 0, "WARNING": 1, "DEGRADATION": 2, "EMERGENCY": 3}
        tier = tier_map.get(severity, 0)
        actions = self.request_quality_degradations(severity)
        return {
            "degradation_tier": tier,
            "severity": severity,
            "recommended_actions": actions,
        }
