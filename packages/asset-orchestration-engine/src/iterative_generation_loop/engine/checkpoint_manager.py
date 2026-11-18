from typing import Dict, Any, Optional
from ..core.loop_schema import IterationContext, IterationRecord

class CheckpointManager:
    _checkpoints: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def save_checkpoint(
        cls,
        loop_id: str,
        iteration_number: int,
        context: IterationContext,
        state_payload: Dict[str, Any]
    ):
        cls._checkpoints[loop_id] = {
            "iteration_number": iteration_number,
            "context": context,
            "payload": state_payload
        }

    @classmethod
    def load_checkpoint(cls, loop_id: str) -> Optional[Dict[str, Any]]:
        return cls._checkpoints.get(loop_id)
