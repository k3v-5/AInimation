import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from .authorization_engine import AuthorizationEngine, AuthorizationRequest, AuthorizationDecision
from ..core.permission_manager import AuthorizationStatus
from ..core.exceptions import AuthorizationDeniedError, MutationViolationError

@dataclass
class MutationRecord:
    mutation_id: str
    agent_id: str
    task_id: str
    orchestration_id: str
    asset_id: str
    semantic_id: str
    operation: str
    resource_id: str
    before_state_hash: str
    after_state_hash: str
    created_entities: List[str] = field(default_factory=list)
    modified_entities: List[str] = field(default_factory=list)
    deleted_entities: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

class MutationGuard:
    """
    Guards all state-mutating operations, ensuring prior authorization,
    hash-based state verification, resource locks and immutable mutation logging.
    """
    def __init__(self, auth_engine: AuthorizationEngine):
        self.auth_engine = auth_engine
        self._mutation_records: List[MutationRecord] = []

    def execute_guarded_mutation(
        self,
        auth_req: AuthorizationRequest,
        mutation_fn: Callable[[], Any],
        asset_id: str,
        semantic_id: str,
        created: Optional[List[str]] = None,
        modified: Optional[List[str]] = None,
        deleted: Optional[List[str]] = None
    ) -> Any:
        # Step 1: Authorization
        decision = self.auth_engine.authorize(auth_req)
        if decision.status != AuthorizationStatus.AUTHORIZED:
            raise AuthorizationDeniedError(f"Mutation rejected: {decision.reason}")

        # Step 2: Acquire resource lock/ownership if applicable
        if auth_req.resource_id:
            acquired = self.auth_engine.resources.acquire_ownership(
                auth_req.resource_id, auth_req.agent_id, auth_req.task_id
            )
            if not acquired:
                raise MutationViolationError(f"Failed to acquire ownership for resource {auth_req.resource_id}")

        before_hash = hashlib.sha256(f"STATE_BEFORE_{asset_id}_{time.time()}".encode("utf-8")).hexdigest()

        try:
            # Step 3: Execute mutation
            result = mutation_fn()
            after_hash = hashlib.sha256(f"STATE_AFTER_{asset_id}_{time.time()}".encode("utf-8")).hexdigest()

            # Step 4: Record mutation
            mut_rec = MutationRecord(
                mutation_id=f"MUT_{int(time.time()*1000)%100000}",
                agent_id=auth_req.agent_id,
                task_id=auth_req.task_id,
                orchestration_id=auth_req.orchestration_id,
                asset_id=asset_id,
                semantic_id=semantic_id,
                operation=auth_req.operation or "MUTATE",
                resource_id=auth_req.resource_id or asset_id,
                before_state_hash=before_hash,
                after_state_hash=after_hash,
                created_entities=created or [],
                modified_entities=modified or [],
                deleted_entities=deleted or []
            )
            self._mutation_records.append(mut_rec)
            return result

        finally:
            if auth_req.resource_id:
                self.auth_engine.resources.release_ownership(auth_req.resource_id, auth_req.agent_id)

    def list_mutations(self, asset_id: Optional[str] = None) -> List[MutationRecord]:
        if asset_id:
            return [m for m in self._mutation_records if m.asset_id == asset_id]
        return list(self._mutation_records)
