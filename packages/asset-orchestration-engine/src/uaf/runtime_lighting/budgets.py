"""
Lighting Budgets & 7-Step Degradation Ladder for UAF-81.85.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from typing import List

from .core import LightPriority, VolumetricQuality
from .lights import Light


class DegradationStep(IntEnum):
    NONE = 0
    CULL_COSMETIC_LIGHTS = 1
    REDUCE_SHADOW_RESOLUTION = 2
    REDUCE_SHADOW_UPDATE_FREQUENCY = 3
    DISABLE_CONTACT_SHADOWS = 4
    REDUCE_VOLUMETRICS = 5
    REDUCE_POSTPROCESS = 6
    PRESERVE_CRITICAL_ONLY = 7


@dataclass
class LightingBudgets:
    """
    Resource budgets for the dynamic lighting and shadow subsystem.
    """
    max_dynamic_lights: int = 128
    max_shadow_maps: int = 16
    max_shadow_memory_bytes: int = 128 * 1024 * 1024  # 128 MB
    max_probe_memory_bytes: int = 32 * 1024 * 1024   # 32 MB
    max_volumetric_cost_ms: float = 2.5
    max_postprocess_ms: float = 3.0
    max_gpu_ms: float = 16.6                         # 60 FPS target


class BudgetManager:
    """
    Monitors resource usage and steps through the 7-level degradation ladder under load.
    """

    def __init__(self, budgets: LightingBudgets = LightingBudgets()) -> None:
        self.budgets = budgets
        self.current_degradation_step = DegradationStep.NONE

    def evaluate_pressure(
        self,
        active_light_count: int,
        active_shadow_count: int,
        shadow_memory_bytes: int,
        estimated_frame_ms: float
    ) -> DegradationStep:
        """Evaluates whether current load exceeds budgets and determines appropriate degradation step."""
        is_overloaded = (
            active_light_count > self.budgets.max_dynamic_lights
            or active_shadow_count > self.budgets.max_shadow_maps
            or shadow_memory_bytes > self.budgets.max_shadow_memory_bytes
            or estimated_frame_ms > self.budgets.max_gpu_ms
        )

        if not is_overloaded:
            self.current_degradation_step = DegradationStep.NONE
            return DegradationStep.NONE

        # Calculate severity
        excess_ratio = max(
            active_light_count / max(1, self.budgets.max_dynamic_lights),
            active_shadow_count / max(1, self.budgets.max_shadow_maps),
            shadow_memory_bytes / max(1, self.budgets.max_shadow_memory_bytes),
            estimated_frame_ms / max(1.0, self.budgets.max_gpu_ms),
        )

        if excess_ratio < 1.2:
            step = DegradationStep.CULL_COSMETIC_LIGHTS
        elif excess_ratio < 1.5:
            step = DegradationStep.REDUCE_SHADOW_RESOLUTION
        elif excess_ratio < 1.8:
            step = DegradationStep.REDUCE_SHADOW_UPDATE_FREQUENCY
        elif excess_ratio < 2.0:
            step = DegradationStep.DISABLE_CONTACT_SHADOWS
        elif excess_ratio < 2.5:
            step = DegradationStep.REDUCE_VOLUMETRICS
        elif excess_ratio < 3.0:
            step = DegradationStep.REDUCE_POSTPROCESS
        else:
            step = DegradationStep.PRESERVE_CRITICAL_ONLY

        self.current_degradation_step = step
        return step

    def apply_degradation(self, lights: List[Light]) -> List[Light]:
        """Filters or modifies lights according to current degradation level."""
        if self.current_degradation_step == DegradationStep.NONE:
            return lights

        filtered: List[Light] = []
        for l in lights:
            if self.current_degradation_step >= DegradationStep.CULL_COSMETIC_LIGHTS:
                if l.priority == LightPriority.COSMETIC:
                    continue
            if self.current_degradation_step >= DegradationStep.PRESERVE_CRITICAL_ONLY:
                if l.priority not in (LightPriority.CRITICAL, LightPriority.GAMEPLAY):
                    continue

            # Modify shadow properties based on degradation
            if self.current_degradation_step >= DegradationStep.DISABLE_CONTACT_SHADOWS:
                l.contact_shadow_length = 0.0
            if self.current_degradation_step >= DegradationStep.REDUCE_SHADOW_RESOLUTION:
                l.shadow_resolution_scale = min(0.5, l.shadow_resolution_scale)

            filtered.append(l)

        return filtered
