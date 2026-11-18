import copy
import time
from typing import Dict, Any, List, Optional
from ..core.critic_schema import CheckpointSnapshot

class RollbackController:
    def __init__(self):
        self.checkpoints: List[CheckpointSnapshot] = []
        self.best_checkpoint: Optional[CheckpointSnapshot] = None

    def save_checkpoint(self, checkpoint_id: str, score: float, asset_state: Dict[str, Any]) -> CheckpointSnapshot:
        snap = CheckpointSnapshot(
            checkpoint_id=checkpoint_id,
            score=score,
            asset_state=copy.deepcopy(asset_state),
            timestamp=time.time()
        )
        self.checkpoints.append(snap)
        if self.best_checkpoint is None or score > self.best_checkpoint.score:
            self.best_checkpoint = snap
        return snap

    def rollback_to_best(self) -> Optional[CheckpointSnapshot]:
        return self.best_checkpoint

    def rollback_to_last(self) -> Optional[CheckpointSnapshot]:
        if self.checkpoints:
            return self.checkpoints[-1]
        return None

class CriticMemory:
    def __init__(self):
        self.failed_strategies: set = set()
        self.successful_strategies: set = set()

    def record_failure(self, strategy_key: str):
        self.failed_strategies.add(strategy_key)

    def is_failed_strategy(self, strategy_key: str) -> bool:
        return strategy_key in self.failed_strategies
