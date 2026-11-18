"""
UAF-81.82: Base Sensory Interface and Perception Pipeline Contracts.
"""

from __future__ import annotations

from typing import Optional, Protocol, Tuple
from ..models.definition import Vec3


class PerceptionSensor(Protocol):
    """Protocol for sensory perception channels."""
    sensor_name: str
    enabled: bool
