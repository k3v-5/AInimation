"""
Operation represents a single auditable, deterministic unit of work in UAF.
UAF-81.0 Section 17.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .operation_types import OperationType
from .operation_status import OperationStatus
from .state_machine import OperationStateMachine


@dataclass
class Operation:
    """
    Mutable state container for an individual operation instance.
    """
    operation_id: str
    operation_type: OperationType
    asset_id: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: OperationStatus = OperationStatus.PENDING
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def transition_to(self, new_status: OperationStatus) -> None:
        """
        Transitions the operation status after validating through the state machine.
        """
        OperationStateMachine.validate_transition(self.status, new_status)
        self.status = new_status
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type.value,
            "asset_id": self.asset_id,
            "inputs": self.inputs,
            "configuration": self.configuration,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Operation":
        return cls(
            operation_id=data["operation_id"],
            operation_type=OperationType.from_str(data["operation_type"]),
            asset_id=data["asset_id"],
            inputs=data.get("inputs", {}),
            configuration=data.get("configuration", {}),
            dependencies=data.get("dependencies", []),
            status=OperationStatus(data.get("status", "PENDING")),
            created_at=float(data.get("created_at", time.time())),
            updated_at=float(data.get("updated_at", time.time())),
        )
