import time
from typing import Dict, Any, List, Optional
from ..core.capability_types import OperationStatus
from ..core.capability_schema import OperationRequest, OperationResponse, TransactionRecord
from ..adapters.base_adapter import IBlenderAdapter

class TransactionManager:
    def __init__(self, adapter: IBlenderAdapter):
        self.adapter = adapter
        self._active_transactions: Dict[str, TransactionRecord] = {}

    def begin_transaction(self, transaction_id: str) -> TransactionRecord:
        tx = TransactionRecord(transaction_id=transaction_id)
        self._active_transactions[transaction_id] = tx
        return tx

    def register_operation(self, transaction_id: str, request: OperationRequest, compensation: Optional[OperationRequest] = None):
        if transaction_id in self._active_transactions:
            self._active_transactions[transaction_id].operations.append(request)
            if compensation:
                self._active_transactions[transaction_id].compensations.append(compensation)

    def commit(self, transaction_id: str):
        if transaction_id in self._active_transactions:
            self._active_transactions[transaction_id].status = "COMMITTED"
            del self._active_transactions[transaction_id]

    def rollback(self, transaction_id: str) -> List[OperationResponse]:
        responses = []
        if transaction_id in self._active_transactions:
            tx = self._active_transactions[transaction_id]
            # Ejecutar compensaciones en orden inverso
            for comp in reversed(tx.compensations):
                res = self.adapter.execute(comp)
                responses.append(res)
            tx.status = "ROLLED_BACK"
            del self._active_transactions[transaction_id]
        return responses
