import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..core.permission_manager import Permission, PermissionManager, AuthorizationStatus, ResourceClassification
from ..core.agent_contract_v2 import AgentContractV2
from ..core.contract_registry import ContractRegistry
from ..policies.capability_policy import CapabilityRegistry
from ..policies.tool_policy import ToolRegistry
from ..policies.resource_policy import ResourceManager
from ..policies.execution_policy import EmergencyStopController
from ..audit.audit_logger import AuditLogger, AuditRecord

@dataclass
class AuthorizationRequest:
    agent_id: str
    tool_id: Optional[str] = None
    capability_id: Optional[str] = None
    resource_id: Optional[str] = None
    operation: Optional[str] = None
    task_id: str = "T_UNKNOWN"
    orchestration_id: str = "ORCH_UNKNOWN"
    payload: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuthorizationDecision:
    status: AuthorizationStatus
    reason: str
    agent_id: str
    tool_id: Optional[str] = None
    capability_id: Optional[str] = None
    resource_id: Optional[str] = None
    operation: Optional[str] = None
    policy_version: str = "2.0.0"
    timestamp: float = field(default_factory=time.time)

class AuthorizationEngine:
    """
    Multi-stage deterministic Authorization Engine enforcing deny-by-default,
    tool governance, resource scopes, delete protection and audit trails.
    """
    def __init__(
        self,
        contract_registry: Optional[ContractRegistry] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        tool_registry: Optional[ToolRegistry] = None,
        resource_manager: Optional[ResourceManager] = None,
        emergency_controller: Optional[EmergencyStopController] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        self.contracts = contract_registry or ContractRegistry()
        self.capabilities = capability_registry or CapabilityRegistry()
        self.tools = tool_registry or ToolRegistry()
        self.resources = resource_manager or ResourceManager()
        self.emergency = emergency_controller or EmergencyStopController()
        self.audit = audit_logger or AuditLogger()

    def authorize(self, req: AuthorizationRequest) -> AuthorizationDecision:
        # 1. Emergency Stop Check
        if self.emergency.is_active:
            decision = AuthorizationDecision(
                status=AuthorizationStatus.DENIED,
                reason=f"EMERGENCY_STOP_ACTIVE: {self.emergency.reason}",
                agent_id=req.agent_id, tool_id=req.tool_id,
                capability_id=req.capability_id, resource_id=req.resource_id, operation=req.operation
            )
            self._log_and_return(decision, req)
            return decision

        # 2. Contract Lookup
        contract = self.contracts.get_contract(req.agent_id)
        if not contract:
            decision = AuthorizationDecision(
                status=AuthorizationStatus.DENIED,
                reason=f"NO_REGISTERED_CONTRACT: Agent {req.agent_id} has no registered contract.",
                agent_id=req.agent_id, tool_id=req.tool_id
            )
            self._log_and_return(decision, req)
            return decision

        # 3. Contract Integrity Verification
        if not contract.verify_integrity():
            decision = AuthorizationDecision(
                status=AuthorizationStatus.DENIED,
                reason=f"CONTRACT_INTEGRITY_ERROR: Contract for agent {req.agent_id} has been tampered with.",
                agent_id=req.agent_id
            )
            self._log_and_return(decision, req)
            return decision

        # 4. Tool Governance & Denylist Check
        if req.tool_id:
            if req.tool_id in contract.forbidden_tools:
                decision = AuthorizationDecision(
                    status=AuthorizationStatus.DENIED,
                    reason=f"TOOL_FORBIDDEN: Tool {req.tool_id} is explicitly forbidden for agent {req.agent_id}.",
                    agent_id=req.agent_id, tool_id=req.tool_id
                )
                self._log_and_return(decision, req)
                return decision

            tool_def = self.tools.get(req.tool_id)
            if not tool_def:
                decision = AuthorizationDecision(
                    status=AuthorizationStatus.DENIED,
                    reason=f"UNREGISTERED_TOOL: Tool {req.tool_id} is not registered in ToolRegistry.",
                    agent_id=req.agent_id, tool_id=req.tool_id
                )
                self._log_and_return(decision, req)
                return decision

            if not contract.validate_tool_access(req.tool_id):
                decision = AuthorizationDecision(
                    status=AuthorizationStatus.DENIED,
                    reason=f"TOOL_ACCESS_DENIED: Tool {req.tool_id} not authorized in contract.",
                    agent_id=req.agent_id, tool_id=req.tool_id
                )
                self._log_and_return(decision, req)
                return decision

            # Check tool required permissions
            if not PermissionManager.validate_permissions_subset(contract.permissions, tool_def.required_permissions):
                decision = AuthorizationDecision(
                    status=AuthorizationStatus.DENIED,
                    reason=f"PERMISSION_DENIED: Agent lacks required permissions for tool {req.tool_id}.",
                    agent_id=req.agent_id, tool_id=req.tool_id
                )
                self._log_and_return(decision, req)
                return decision

        # 5. Capability Governance Check
        if req.capability_id:
            cap_def = self.capabilities.get(req.capability_id)
            if not cap_def:
                decision = AuthorizationDecision(
                    status=AuthorizationStatus.DENIED,
                    reason=f"UNKNOWN_CAPABILITY: Capability {req.capability_id} is not registered.",
                    agent_id=req.agent_id, capability_id=req.capability_id
                )
                self._log_and_return(decision, req)
                return decision

            if not PermissionManager.validate_permissions_subset(contract.permissions, cap_def.required_permissions):
                decision = AuthorizationDecision(
                    status=AuthorizationStatus.DENIED,
                    reason=f"PERMISSION_DENIED: Agent lacks permissions for capability {req.capability_id}.",
                    agent_id=req.agent_id, capability_id=req.capability_id
                )
                self._log_and_return(decision, req)
                return decision

        # 6. Resource Scope & Project Protection Check
        if req.resource_id:
            scope = self.resources.get_scope(req.resource_id)
            if scope.classification == ResourceClassification.PROTECTED and req.operation and "WRITE" in req.operation.upper():
                if Permission.PROJECT_WRITE not in contract.permissions:
                    decision = AuthorizationDecision(
                        status=AuthorizationStatus.DENIED,
                        reason=f"PROTECTED_RESOURCE_VIOLATION: Resource {req.resource_id} is PROTECTED and requires PROJECT_WRITE.",
                        agent_id=req.agent_id, resource_id=req.resource_id
                    )
                    self._log_and_return(decision, req)
                    return decision

            # Resource Ownership check
            if scope.owner_agent_id and scope.owner_agent_id != req.agent_id:
                decision = AuthorizationDecision(
                    status=AuthorizationStatus.DENIED,
                    reason=f"RESOURCE_OWNERSHIP_CONFLICT: Resource {req.resource_id} is currently owned by {scope.owner_agent_id}.",
                    agent_id=req.agent_id, resource_id=req.resource_id
                )
                self._log_and_return(decision, req)
                return decision

        # 7. Delete Protection Check
        if req.operation and "DELETE" in req.operation.upper():
            if Permission.ASSET_DELETE not in contract.permissions and Permission.FILESYSTEM_DELETE not in contract.permissions:
                decision = AuthorizationDecision(
                    status=AuthorizationStatus.DENIED,
                    reason=f"DELETE_PROTECTION_VIOLATION: Destructive delete operation {req.operation} requires explicit DELETE permission.",
                    agent_id=req.agent_id, operation=req.operation
                )
                self._log_and_return(decision, req)
                return decision

        # All checks passed -> AUTHORIZED
        decision = AuthorizationDecision(
            status=AuthorizationStatus.AUTHORIZED,
            reason="AUTHORIZED: All governance checks passed successfully.",
            agent_id=req.agent_id, tool_id=req.tool_id,
            capability_id=req.capability_id, resource_id=req.resource_id, operation=req.operation
        )
        self._log_and_return(decision, req)
        return decision

    def _log_and_return(self, decision: AuthorizationDecision, req: AuthorizationRequest):
        self.audit.log_decision(AuditRecord(
            record_id=f"AUD_{int(time.time()*1000)%100000}",
            agent_id=req.agent_id,
            task_id=req.task_id,
            orchestration_id=req.orchestration_id,
            tool_id=req.tool_id,
            capability_id=req.capability_id,
            resource_id=req.resource_id,
            operation=req.operation,
            status=decision.status,
            reason=decision.reason,
            sanitized_input=req.payload
        ))
