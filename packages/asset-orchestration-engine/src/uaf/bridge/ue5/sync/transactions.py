"""Atomic multi-operation transaction management and rollback mechanics."""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uaf.bridge.ue5.protocol.messages import BridgeMessage
from uaf.bridge.ue5.sync.patches import StatePatch


class TransactionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"


class TransactionError(Exception):
    """Raised when an operation within a transaction fails."""
    pass


@dataclass
class BridgeTransaction:
    """Encapsulates an atomic set of multi-asset or multi-actor operations."""
    transaction_id: str = field(default_factory=lambda: f"tx_{uuid.uuid4().hex[:12]}")
    status: TransactionStatus = TransactionStatus.ACTIVE
    description: str = ""
    operations: List[Dict[str, Any]] = field(default_factory=list)
    staged_messages: List[BridgeMessage] = field(default_factory=list)
    staged_patches: List[StatePatch] = field(default_factory=list)
    rollback_callbacks: List[Callable[[], None]] = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        return self.status == TransactionStatus.ACTIVE

    @property
    def is_committed(self) -> bool:
        return self.status == TransactionStatus.COMMITTED

    @property
    def is_rolled_back(self) -> bool:
        return self.status == TransactionStatus.ROLLED_BACK

    def stage_operation(
        self,
        op_type: str,
        payload: Any,
        rollback_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        if self.status != TransactionStatus.ACTIVE:
            raise TransactionError(f"Cannot stage operation on transaction with status {self.status.value}")
        self.operations.append({"type": op_type, "payload": payload})
        if rollback_callback:
            self.rollback_callbacks.append(rollback_callback)

    def stage_message(self, message: BridgeMessage, rollback_callback: Optional[Callable[[], None]] = None) -> None:
        if self.status != TransactionStatus.ACTIVE:
            raise TransactionError(f"Cannot stage message on transaction with status {self.status.value}")
        self.staged_messages.append(message)
        if rollback_callback:
            self.rollback_callbacks.append(rollback_callback)

    def stage_patch(self, patch: StatePatch, rollback_callback: Optional[Callable[[], None]] = None) -> None:
        if self.status != TransactionStatus.ACTIVE:
            raise TransactionError(f"Cannot stage patch on transaction with status {self.status.value}")
        self.staged_patches.append(patch)
        if rollback_callback:
            self.rollback_callbacks.append(rollback_callback)

    def commit(self) -> None:
        if self.status != TransactionStatus.ACTIVE:
            raise TransactionError(f"Cannot commit transaction with status {self.status.value}")
        self.status = TransactionStatus.COMMITTED
        self.rollback_callbacks.clear()

    def rollback(self) -> None:
        if self.status != TransactionStatus.ACTIVE:
            return
        for cb in reversed(self.rollback_callbacks):
            try:
                cb()
            except Exception:
                pass
        self.status = TransactionStatus.ROLLED_BACK
        self.staged_messages.clear()
        self.staged_patches.clear()
        self.rollback_callbacks.clear()


class TransactionManager:
    """Coordinates nested or active bridge transactions."""

    def __init__(self) -> None:
        self.active_transaction: Optional[BridgeTransaction] = None
        self.history: List[BridgeTransaction] = []
        self._by_id: Dict[str, BridgeTransaction] = {}

    def begin_transaction(self, description: str = "") -> BridgeTransaction:
        if self.active_transaction is not None and self.active_transaction.status == TransactionStatus.ACTIVE:
            raise TransactionError("A transaction is already active. Nested transactions not supported.")
        tx = BridgeTransaction(description=description)
        self.active_transaction = tx
        self.history.append(tx)
        self._by_id[tx.transaction_id] = tx
        return tx

    def begin(self, description: str = "") -> BridgeTransaction:
        return self.begin_transaction(description=description)

    def commit(self, transaction_id: Optional[str] = None) -> BridgeTransaction:
        tx = self._by_id.get(transaction_id) if transaction_id else self.active_transaction
        if not tx or tx.status != TransactionStatus.ACTIVE:
            raise TransactionError(f"No active transaction '{transaction_id}' to commit.")
        tx.commit()
        if self.active_transaction == tx:
            self.active_transaction = None
        return tx

    def rollback(self, transaction_id: Optional[str] = None) -> BridgeTransaction:
        tx = self._by_id.get(transaction_id) if transaction_id else self.active_transaction
        if not tx or tx.status != TransactionStatus.ACTIVE:
            raise TransactionError(f"No active transaction '{transaction_id}' to roll back.")
        tx.rollback()
        if self.active_transaction == tx:
            self.active_transaction = None
        return tx
