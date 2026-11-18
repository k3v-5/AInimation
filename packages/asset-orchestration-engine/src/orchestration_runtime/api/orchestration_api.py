from typing import Dict, Any, List, Optional
from ..core.runtime_types import (
    RuntimeTaskStatus, RuntimeTaskType, RuntimePriority,
    RuntimeLockType, AgentState, ExecutionState, RuntimeEventType
)
from ..core.runtime_schema import (
    Task, EventEnvelope, LockLease, AgentProfile, ExecutionUnit,
    Workflow, AssetManifest
)
from ..events.event_bus import EventBus
from ..tasks.task_manager import TaskManager, TaskQueue
from ..resources.lock_manager import LockManager
from ..agents.agent_manager import AgentManager
from ..execution.mcp_adapter import MCPAdapter
from ..execution.execution_manager import ExecutionManager
from ..workflow.workflow_engine import WorkflowEngine

class OrchestrationAPI:
    """
    Orchestration Runtime API (AOE v38)
    
    Regla Fundamental:
    NINGÚN AGENTE TIENE CONTROL GLOBAL DEL SISTEMA. ANTIGRAVITY ES EL DIRECTOR
    Y EL ORCHESTRATION RUNTIME COORDINA TAREAS, ESTADOS, PERMISOS, BLOQUEOS
    DE RECURSOS, EJECUCIÓN MCP CONTROLADA Y VERIFICACIÓN EMPÍRICA DE ESTADO.
    """
    def __init__(self):
        self.event_bus = EventBus()
        self.task_manager = TaskManager(self.event_bus)
        self.task_queue = TaskQueue()
        self.lock_manager = LockManager(self.event_bus)
        self.agent_manager = AgentManager()
        self.mcp_adapter = MCPAdapter()
        self.execution_manager = ExecutionManager(self.mcp_adapter, self.event_bus)
        self.workflow_engine = WorkflowEngine(self.task_manager)
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

    def create_task(
        self,
        asset_id: str,
        task_type: RuntimeTaskType,
        priority: RuntimePriority = RuntimePriority.NORMAL,
        parent_task_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        inputs: Optional[Dict] = None
    ) -> Task:
        return self.task_manager.create_task(
            asset_id=asset_id,
            task_type=task_type,
            parent_task_id=parent_task_id,
            priority=priority,
            dependencies=dependencies,
            inputs=inputs
        )

    def transition_task(self, task_id: str, new_status: RuntimeTaskStatus):
        self.task_manager.transition_task(task_id, new_status)

    def acquire_lock(self, resource_id: str, task_id: str, lock_type: RuntimeLockType = RuntimeLockType.EXCLUSIVE) -> LockLease:
        return self.lock_manager.acquire_lock(resource_id, task_id, lock_type)

    def release_lock(self, resource_id: str, task_id: str):
        self.lock_manager.release_lock(resource_id, task_id)

    def register_agent(self, agent_id: str, capabilities: List[str], permissions: Optional[List[str]] = None) -> AgentProfile:
        return self.agent_manager.register_agent(agent_id, capabilities, permissions)

    def execute_operation(
        self,
        task_id: str,
        operation: str,
        agent_id: str,
        asset_id: str,
        parameters: Dict[str, Any],
        idempotency_key: str,
        simulated_timeout: bool = False
    ) -> ExecutionUnit:
        # Verificar permisos del agente
        self.agent_manager.verify_permission(agent_id, "EXECUTE")
        return self.execution_manager.run_unit(
            task_id=task_id,
            operation=operation,
            agent_id=agent_id,
            asset_id=asset_id,
            parameters=parameters,
            idempotency_key=idempotency_key,
            simulated_timeout=simulated_timeout
        )

    def verify_claimed_state(self, asset_id: str, claimed_object: str):
        self.execution_manager.verify_agent_result(asset_id, claimed_object)

    def request_approval(self, operation: str, target: str, reason: str) -> str:
        app_id = f"APP_{len(self.pending_approvals) + 1}"
        self.pending_approvals[app_id] = {
            "operation": operation,
            "target": target,
            "reason": reason,
            "status": "PENDING_APPROVAL"
        }
        return "PENDING_APPROVAL"

    def replay_events(self) -> List[EventEnvelope]:
        return self.event_bus.replay()
