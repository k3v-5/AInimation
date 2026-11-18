import time
from typing import Dict, Any, List, Optional
from ..core.orchestrator_schema import Checkpoint, TaskState

class CheckpointManager:
    def __init__(self):
        self.checkpoints: Dict[str, Checkpoint] = {}

    def create_checkpoint(
        self,
        checkpoint_id: str,
        asset_id: str,
        parameters: Dict[str, Any],
        task_states: Dict[str, TaskState]
    ) -> Checkpoint:
        cp = Checkpoint(
            checkpoint_id=checkpoint_id,
            asset_id=asset_id,
            parameters=dict(parameters),
            task_states=dict(task_states),
            timestamp=time.time()
        )
        self.checkpoints[checkpoint_id] = cp
        return cp

    def restore_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        return self.checkpoints.get(checkpoint_id)

class ReworkDetector:
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts
        self.history: List[Dict[str, Any]] = []

    def record_attempt(self, task_id: str, parameter_name: str, value: Any) -> Tuple[bool, str]:
        """
        Retorna (should_stop, reason).
        Detecta oscilaciones y límites de reintentos.
        """
        self.history.append({"task_id": task_id, "param": parameter_name, "val": value})
        task_history = [h for h in self.history if h["task_id"] == task_id]

        if len(task_history) >= self.max_attempts:
            return True, f"MAX_ATTEMPTS_EXCEEDED: Task '{task_id}' reached limit of {self.max_attempts} attempts without resolution."

        # Detección de Oscilación A -> B -> A
        if len(task_history) >= 3:
            v0 = task_history[-3]["val"]
            v1 = task_history[-2]["val"]
            v2 = task_history[-1]["val"]
            if v0 == v2 and v0 != v1:
                return True, f"OSCILLATION_DETECTED: Parameter '{parameter_name}' oscillating ({v0} -> {v1} -> {v2})."

        return False, ""
