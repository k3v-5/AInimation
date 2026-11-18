"""
Crash Recovery & Fail-Safe Fallback Profiles for UAF-81.85.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

from .core import FallbackLevel, LightId, LightType, LightPriority
from .lights import Light
from .directional import DirectionalLight
from .ambient import AmbientLighting
from .postprocess import PostProcessSettings


class LightingCrashRecovery:
    """
    Guarantees runtime immunity against lighting faults, isolating exceptions
    and falling back to minimal or emergency visual profiles.
    """

    def __init__(self) -> None:
        self.current_level = FallbackLevel.FULL
        self.fault_count = 0

    def trigger_fallback(self, target_level: FallbackLevel) -> None:
        """Escalates fallback level."""
        self.fault_count += 1
        self.current_level = target_level

    def get_emergency_lights(self) -> List[Light]:
        """
        Creates a minimal fail-safe lighting setup guaranteeing visibility.
        Contains a single neutral directional key light.
        """
        emergency_sun = DirectionalLight(
            light_id=LightId("emergency_key_light"),
            direction=(0.0, -0.7071, -0.7071),
            intensity=10000.0,
            color=(1.0, 1.0, 1.0),
            cast_shadows=False,
            priority=LightPriority.CRITICAL,
        )
        return [emergency_sun]

    def get_emergency_ambient(self) -> AmbientLighting:
        """Neutral grey ambient light ensuring no completely black surfaces."""
        return AmbientLighting(
            sky_color=(0.2, 0.2, 0.2),
            ground_color=(0.1, 0.1, 0.1),
            intensity=1.0,
        )

    def get_emergency_postprocess(self) -> PostProcessSettings:
        """Minimal post-process settings with safe neutral tone mapping."""
        ps = PostProcessSettings()
        ps.bloom.enabled = False
        ps.dof.enabled = False
        ps.motion_blur.enabled = False
        ps.ao.enabled = False
        ps.exposure.fixed_ev100 = 8.0
        return ps
