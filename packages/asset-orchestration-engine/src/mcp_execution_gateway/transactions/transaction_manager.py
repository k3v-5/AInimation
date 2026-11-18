from typing import Dict, List, Set, Optional
from ..core.gateway_schema import TransactionRecord, SceneStateSnapshot, VerificationResult

class TransactionManager:
    def __init__(self):
        self.transactions: Dict[str, TransactionRecord] = {}

    def begin_transaction(self, operation_id: str, snapshot_before: SceneStateSnapshot) -> TransactionRecord:
        tx_id = f"TX_{operation_id}"
        tx = TransactionRecord(
            transaction_id=tx_id,
            operation_id=operation_id,
            snapshot_before=snapshot_before
        )
        self.transactions[tx_id] = tx
        return tx

    def track_created_object(self, tx_id: str, object_id: str):
        if tx_id in self.transactions:
            self.transactions[tx_id].created_objects.append(object_id)

    def commit(self, tx_id: str):
        if tx_id in self.transactions:
            self.transactions[tx_id].committed = True

    def rollback(self, tx_id: str) -> List[str]:
        if tx_id in self.transactions:
            tx = self.transactions[tx_id]
            # Devolver solo los objetos creados durante esta transacción
            return list(tx.created_objects)
        return []

class ResultVerifier:
    @staticmethod
    def verify_objects_exist(expected_ids: List[str], actual_scene_objects: Set[str]) -> VerificationResult:
        missing = [oid for oid in expected_ids if oid not in actual_scene_objects]
        if missing:
            return VerificationResult(
                verified=False,
                expected_objects_present=False,
                details=f"Verification failed: Expected objects missing in scene: {missing}"
            )
        return VerificationResult(
            verified=True,
            expected_objects_present=True,
            details="All expected objects successfully verified in scene."
        )
