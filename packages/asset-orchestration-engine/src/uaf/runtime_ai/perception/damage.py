"""
UAF-81.82: Damage Perception Sensor (Gameplay Damage Events).
"""

from __future__ import annotations

from typing import Optional
from ..models.definition import DamageStimulus


class DamageSensor:
    """Detects and parses incoming combat damage events directed at the agent."""

    @staticmethod
    def process_damage(agent_id: str, damage: DamageStimulus) -> bool:
        """Return True if the damage was inflicted upon agent_id."""
        return damage.target_id == agent_id and damage.amount > 0.0
