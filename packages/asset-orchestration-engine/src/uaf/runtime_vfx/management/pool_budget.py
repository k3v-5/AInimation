"""
UAF-81.84.7: Object Pooling (Zero Ghost State) and Budget Degradation Manager.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Set

from ..emitter.emitter import VFXEmitter
from ..models.definition import (
    VFXBudget,
    VFXBudgetExceededError,
    VFXLOD,
    VFXMetrics,
    VFXPriority,
)


class VFXPool:
    """Recycles particle emitters cleanly, enforcing zero ghost state upon acquisition."""

    def __init__(self, factory_fn: Callable[[], VFXEmitter], initial_size: int = 10):
        self.factory_fn = factory_fn
        self._available: List[VFXEmitter] = []
        self._in_use: Set[VFXEmitter] = set()

        for _ in range(initial_size):
            emitter = self.factory_fn()
            emitter.reset()
            self._available.append(emitter)

    def acquire(self) -> VFXEmitter:
        """Acquire a clean, reset emitter instance."""
        if self._available:
            emitter = self._available.pop()
        else:
            emitter = self.factory_fn()

        emitter.reset()
        self._in_use.add(emitter)
        return emitter

    def release(self, emitter: VFXEmitter) -> None:
        """Release an emitter instance back to the pool after complete reset."""
        if emitter in self._in_use:
            self._in_use.remove(emitter)

        # Zero ghost state rule: reset all particles, parameters and timers
        emitter.reset()
        self._available.append(emitter)

    @property
    def available_count(self) -> int:
        return len(self._available)

    @property
    def in_use_count(self) -> int:
        return len(self._in_use)


class VFXBudgetManager:
    """
    Monitors particle and system budgets and applies orderly degradation
    when resource thresholds are exceeded.
    """

    def __init__(self, budget: VFXBudget | None = None):
        self.budget = budget or VFXBudget()
        self.metrics = VFXMetrics()
        self.degradation_level: int = 0  # 0: None, 1..7: degradation steps

    def check_and_degrade(
        self,
        current_particle_count: int,
        current_system_count: int,
    ) -> int:
        """
        Evaluate budget pressure and determine degradation level (0 to 7):
        Step 1: Cull cosmetic effects
        Step 2: Reduce spawn rates
        Step 3: Reduce particle lifetime
        Step 4: Lower LOD globally
        Step 5: Disable expensive collisions
        Step 6: Disable secondary/sub-emitters
        Step 7: Preserve critical gameplay VFX only
        """
        self.metrics.active_particles = current_particle_count
        self.metrics.active_systems = current_system_count

        particle_pressure = current_particle_count / max(1, self.budget.max_particles)
        system_pressure = current_system_count / max(1, self.budget.max_active_systems)
        pressure = max(particle_pressure, system_pressure)

        if pressure < 0.70:
            self.degradation_level = 0
        elif pressure < 0.80:
            self.degradation_level = 1  # Cull cosmetic
        elif pressure < 0.90:
            self.degradation_level = 2  # Reduce spawn
        elif pressure < 0.95:
            self.degradation_level = 3  # Reduce lifetime
        elif pressure < 1.00:
            self.degradation_level = 4  # Lower LOD
        elif pressure < 1.10:
            self.degradation_level = 5  # Disable collisions
        elif pressure < 1.25:
            self.degradation_level = 6  # Disable sub-emitters
        else:
            self.degradation_level = 7  # Critical gameplay only

        return self.degradation_level

    def should_cull_priority(self, priority: VFXPriority) -> bool:
        """Determine if an effect should be culled based on degradation level and priority."""
        if priority == VFXPriority.CRITICAL:
            return False  # Critical is never culled

        if self.degradation_level >= 7 and priority < VFXPriority.CRITICAL:
            return True
        if self.degradation_level >= 6 and priority <= VFXPriority.LOW:
            return True
        if self.degradation_level >= 1 and priority == VFXPriority.COSMETIC:
            return True

        return False
