from typing import Dict, Any, Optional, List, Tuple
from ..core.correction_types import CorrectionStatus, RollbackStatus
from ..core.correction_schema import AssetSnapshot
from .snapshot_manager import SnapshotManager

class TransactionManager:
    def __init__(self):
        self._active_transactions: Dict[str, AssetSnapshot] = {}

    def begin_transaction(
        self,
        tx_id: str,
        asset_id: str,
        iteration_id: int,
        parameters: Dict[str, Any],
        geometry_state: Dict[str, Any]
    ) -> AssetSnapshot:
        snap = SnapshotManager.create_snapshot(asset_id, iteration_id, parameters, geometry_state)
        self._active_transactions[tx_id] = snap
        return snap

    def rollback_transaction(self, tx_id: str) -> Tuple[RollbackStatus, Optional[AssetSnapshot]]:
        if tx_id not in self._active_transactions:
            return RollbackStatus.ROLLBACK_FAILED, None
        baseline = self._active_transactions.pop(tx_id)
        return RollbackStatus.ROLLBACK_SUCCESS, baseline

    def commit_transaction(self, tx_id: str) -> bool:
        if tx_id in self._active_transactions:
            self._active_transactions.pop(tx_id)
            return True
        return False
