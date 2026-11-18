from typing import Dict, Any, List, Optional
from ..core.adaptive_schema import CorrectionTransactionRecord

class CorrectionTransaction:
    def __init__(self):
        self.active_transactions: Dict[str, CorrectionTransactionRecord] = {}

    def begin_transaction(self, tx_id: str, attempt_id: str, current_parameters: Dict[str, Any], dirty_components: List[str]) -> CorrectionTransactionRecord:
        record = CorrectionTransactionRecord(
            tx_id=tx_id,
            attempt_id=attempt_id,
            state="OPEN",
            checkpoint_parameters=dict(current_parameters),
            dirty_components=list(dirty_components),
            rollback_available=True
        )
        self.active_transactions[tx_id] = record
        return record

    def commit(self, tx_id: str):
        if tx_id in self.active_transactions:
            self.active_transactions[tx_id].state = "COMMITTED"

    def rollback(self, tx_id: str) -> Dict[str, Any]:
        if tx_id not in self.active_transactions:
            raise KeyError(f"Transaction '{tx_id}' not found.")
        record = self.active_transactions[tx_id]
        record.state = "ROLLED_BACK"
        return dict(record.checkpoint_parameters)
