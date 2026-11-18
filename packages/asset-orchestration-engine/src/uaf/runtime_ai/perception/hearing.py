"""
UAF-81.82: Hearing Sensor (Acoustic Attenuation and Sound Events).
"""

from __future__ import annotations

import math
from typing import Optional

from ..models.definition import SoundStimulus, Vec3, vec3_distance


class HearingSensor:
    """
    Evaluates acoustic stimulus reception based on sound intensity,
    distance attenuation, and agent hearing sensitivity.
    """

    def __init__(self, sensitivity: float = 1.0, max_hearing_range: float = 50.0):
        self.sensitivity = sensitivity
        self.max_hearing_range = max_hearing_range

    def perceive_sound(self, observer_position: Vec3, sound: SoundStimulus) -> Optional[float]:
        """
        Evaluate sound stimulus. Returns perceived intensity if heard, else None.
        Perceived intensity model: I_perc = (intensity * sensitivity) / (1.0 + 0.05 * d^2).
        """
        dist = vec3_distance(observer_position, sound.position)
        if dist > self.max_hearing_range:
            return None

        attenuation = 1.0 + 0.05 * (dist * dist)
        perceived = (sound.intensity * self.sensitivity) / max(1e-4, attenuation)

        # Hearing perception threshold
        if perceived >= 0.1:
            return perceived
        return None
