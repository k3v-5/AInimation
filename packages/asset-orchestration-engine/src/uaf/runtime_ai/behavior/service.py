"""
UAF-81.82: Behavior Tree Services (Periodic Background Evaluation).
"""

from __future__ import annotations

from typing import Callable, Optional
from .node import BTContext


class BTService:
    """
    Background service attached to a Behavior Tree node, executing periodically
    every interval_ticks while the corresponding branch or tree is active.
    """

    def __init__(
        self,
        service_id: str,
        interval_ticks: int = 5,
        action: Optional[Callable[[BTContext], None]] = None,
        name: str = "",
    ):
        self.service_id = service_id
        self.name = name or service_id
        self.interval_ticks = max(1, interval_ticks)
        self.action = action
        self._last_tick: int = -999999

    def tick_service(self, context: BTContext) -> None:
        """Execute service action if interval_ticks have elapsed."""
        if context.tick - self._last_tick >= self.interval_ticks:
            self._last_tick = context.tick
            self.execute(context)

    def execute(self, context: BTContext) -> None:
        if self.action is not None:
            self.action(context)
