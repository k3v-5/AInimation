from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .snapshot_manager import AssetSnapshot

class TransactionState(str, Enum):
    CREATED = "CREATED"
    PRECHECKING = "PRECHECKING"
    SNAPSHOTTED = "SNAPSHOTTED"
    EXECUTING = "EXECUTING"
    POSTCHECKING = "POSTCHECKING"
    VALIDATING = "VALIDATING"
    COMMITTED = "COMMITTED"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

@dataclass
class MutationTransaction:
    transaction_id: str
    plan_id: str
    asset_id: str
    state: TransactionState = TransactionState.CREATED
    snapshot: Optional[AssetSnapshot] = None
    error_message: Optional[str] = None
