import time
from typing import Dict, Any, Optional, Set
from ..core.runtime_types import ExecutionState, RuntimeEventType
from ..core.runtime_schema import ExecutionUnit
from .mcp_adapter import MCPAdapter
from ..events.event_bus import EventBus

class ExecutionManager:
    def __init__(self, mcp_adapter: MCPAdapter, event_bus: Optional[EventBus] = None):
        self.mcp_adapter = mcp_adapter
        self.event_bus = event_bus
        self.execution_ledger: Dict[str, ExecutionUnit] = {}

    def run_unit(
        self,
        task_id: str,
        operation: str,
        agent_id: str,
        asset_id: str,
        parameters: Dict[str, Any],
        idempotency_key: str,
        simulated_timeout: bool = False
    ) -> ExecutionUnit:
        unit_id = f"EXEC_{int(time.time()*1000)}_{len(self.execution_ledger)}"
        unit = ExecutionUnit(
            execution_id=unit_id,
            task_id=task_id,
            operation=operation,
            agent_id=agent_id,
            idempotency_key=idempotency_key,
            status=ExecutionState.RUNNING
        )
        self.execution_ledger[unit_id] = unit

        try:
            res = self.mcp_adapter.execute_command(
                command=operation,
                asset_id=asset_id,
                parameters=parameters,
                idempotency_key=idempotency_key,
                simulated_timeout=simulated_timeout
            )
            unit.status = ExecutionState.SUCCESS
            unit.result = res
        except TimeoutError as te:
            unit.status = ExecutionState.TIMEOUT
            unit.error = str(te)
            if self.event_bus:
                self.event_bus.publish(RuntimeEventType.TIMEOUT, task_id=task_id, asset_id=asset_id, payload={"error": str(te)})
            raise te
        except Exception as e:
            unit.status = ExecutionState.FAILED
            unit.error = str(e)
            if self.event_bus:
                self.event_bus.publish(RuntimeEventType.MCP_ERROR, task_id=task_id, asset_id=asset_id, payload={"error": str(e)})
            raise e

        return unit

    def verify_agent_result(self, asset_id: str, claimed_object: str):
        """State Verification: Protege contra alucinaciones del agente comparando con el estado real."""
        actual_objects = self.mcp_adapter.query_scene(asset_id)
        if claimed_object not in actual_objects:
            raise RuntimeError(f"AGENT_RESULT_MISMATCH: Agent claimed '{claimed_object}' exists, but actual scene objects are {list(actual_objects)}.")
