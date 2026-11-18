from typing import Optional, Dict, Any, List
from ..core.scene_graph import SceneGraph
from .operations import OperationResult

class Transaction:
    def __init__(self, transaction_id: str, graph: SceneGraph):
        self.transaction_id = transaction_id
        self.snapshot_graph = graph.clone()
        self.active_graph = graph
        self.executed_operations: List[str] = []
        self.is_committed = False
        self.is_rolled_back = False

class TransactionManager:
    def __init__(self):
        self.active_transactions: Dict[str, Transaction] = {}

    def begin_transaction(self, transaction_id: str, graph: SceneGraph) -> Transaction:
        tx = Transaction(transaction_id, graph)
        self.active_transactions[transaction_id] = tx
        return tx

    def commit(self, transaction_id: str) -> bool:
        tx = self.active_transactions.get(transaction_id)
        if not tx or tx.is_rolled_back:
            return False
        tx.is_committed = True
        del self.active_transactions[transaction_id]
        return True

    def rollback(self, transaction_id: str) -> Optional[SceneGraph]:
        tx = self.active_transactions.get(transaction_id)
        if not tx or tx.is_committed:
            return None
        # Restaurar estado del Scene Graph desde el snapshot
        tx.active_graph.nodes = tx.snapshot_graph.nodes
        tx.is_rolled_back = True
        del self.active_transactions[transaction_id]
        return tx.active_graph
