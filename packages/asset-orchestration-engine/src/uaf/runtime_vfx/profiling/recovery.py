"""
UAF-81.84.11: Crash Recovery and Fail-Safe Isolation.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from ..emitter.emitter import VFXEmitter


logger = logging.getLogger("UAF.VFX.Recovery")


class VFXRecoveryManager:
    """
    Isolates faulty VFX instances so that exceptions during simulation,
    rendering, or spawning never crash the runtime simulation tick.
    """

    def __init__(self):
        self.fault_log: List[Dict[str, Any]] = []
        self.disabled_emitters: set[str] = set()

    def execute_safe(self, emitter: VFXEmitter, action: Callable[[], Any], action_name: str = "update") -> Optional[Any]:
        """
        Execute an emitter operation within a fail-safe boundary.
        If an exception is raised, catches it, records diagnostic fault,
        disables the emitter, and returns None.
        """
        if emitter.config.emitter_id in self.disabled_emitters or not emitter.is_enabled:
            return None

        try:
            return action()
        except Exception as ex:
            emitter_id = emitter.config.emitter_id
            self.disabled_emitters.add(emitter_id)
            emitter.is_enabled = False
            emitter.reset()

            fault_record = {
                "emitter_id": emitter_id,
                "action": action_name,
                "error_type": type(ex).__name__,
                "error_message": str(ex),
            }
            self.fault_log.append(fault_record)
            logger.warning(f"VFX Fail-Safe: Disabled faulty emitter '{emitter_id}' during {action_name}: {ex}")
            return None

    def is_disabled(self, emitter_id: str) -> bool:
        return emitter_id in self.disabled_emitters

    def clear(self) -> None:
        self.fault_log.clear()
        self.disabled_emitters.clear()
