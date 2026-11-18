import time
from typing import Dict, Any, List, Optional
from ..core.capability_types import (
    OperationStatus, CapabilityCategory, ErrorTaxonomy, CircuitState, LockScope
)
from ..core.capability_schema import (
    OperationRequest, OperationResponse, BlenderSceneState,
    BlenderObjectState, TransactionRecord, HealthReport
)
from ..adapters.base_adapter import IBlenderAdapter
from ..adapters.mock_adapter import MockBlenderAdapter
from ..adapters.ahujasid.ahujasid_adapter import AhujasidBlenderAdapter
from ..engine.capability_registry import CapabilityRegistry
from ..engine.circuit_breaker import CircuitBreaker
from ..engine.transaction_manager import TransactionManager
from ..engine.state_reconciler import StateReconciler

class BlenderCapabilityAPI:
    """
    Blender Capability Abstraction & MCP Execution Layer API (AOE v53)
    
    Regla Fundamental:
    EL SISTEMA NUNCA DICE "LLAMA A AHUJASID PARA CREAR UN CUBO".
    DICE "EJECUTA OBJECT.CREATE".
    EL ADAPTER DECIDE CÓMO REALIZAR ESA OPERACIÓN, GARANTIZANDO
    INDEPENDENCIA DE MCP, IDEMPOTENCIA, CIRCUIT BREAKER, OBSERVABILIDAD Y ROLLBACK.
    """
    def __init__(self, adapter: Optional[IBlenderAdapter] = None):
        self.adapter = adapter or AhujasidBlenderAdapter()
        self.registry = CapabilityRegistry()
        self.circuit_breaker = CircuitBreaker()
        self.tx_manager = TransactionManager(self.adapter)
        self._locks: Dict[str, str] = {}

    def swap_adapter(self, new_adapter: IBlenderAdapter):
        self.adapter = new_adapter
        self.tx_manager.adapter = new_adapter

    def execute_operation(self, request: OperationRequest) -> OperationResponse:
        # 1. Validar parámetros según CapabilityContract
        self.registry.validate_request_parameters(request.capability_id, request.parameters)

        # 2. Comprobar Circuit Breaker
        if not self.circuit_breaker.allow_execution():
            return OperationResponse(
                operation_id=request.operation_id,
                status=OperationStatus.FAILED,
                errors=["CIRCUIT_OPEN: Blender backend is temporarily blocked due to repeated failures."],
                adapter_name=str(self.adapter.__class__.__name__)
            )

        # 3. Comprobar Locks de Recursos
        if request.asset_id in self._locks and self._locks[request.asset_id] != request.operation_id:
            raise BlockingIOError(f"RESOURCE_LOCKED: Asset '{request.asset_id}' is locked by operation '{self._locks[request.asset_id]}'.")

        # 4. Ejecutar vía Adapter con reconciliación de idempotencia
        start_t = time.time()
        if request.capability_id == "object.create":
            response = StateReconciler.reconcile_creation(self.adapter, request)
        else:
            response = self.adapter.execute(request)
        response.duration_ms = round((time.time() - start_t) * 1000, 2)

        # 5. Notificar Circuit Breaker
        if response.status == OperationStatus.SUCCEEDED:
            self.circuit_breaker.record_success()
        else:
            self.circuit_breaker.record_failure()

        return response

    def acquire_lock(self, asset_id: str, operation_id: str):
        if asset_id in self._locks and self._locks[asset_id] != operation_id:
            raise BlockingIOError(f"RESOURCE_LOCKED: Asset '{asset_id}' is already locked.")
        self._locks[asset_id] = operation_id

    def release_lock(self, asset_id: str):
        if asset_id in self._locks:
            del self._locks[asset_id]

    def begin_transaction(self, tx_id: str) -> TransactionRecord:
        return self.tx_manager.begin_transaction(tx_id)

    def register_compensation(self, tx_id: str, request: OperationRequest, compensation: OperationRequest):
        self.tx_manager.register_operation(tx_id, request, compensation)

    def commit_transaction(self, tx_id: str):
        self.tx_manager.commit(tx_id)

    def rollback_transaction(self, tx_id: str) -> List[OperationResponse]:
        return self.tx_manager.rollback(tx_id)

    def inspect_object(self, object_id: str) -> Optional[BlenderObjectState]:
        return self.adapter.inspect_object(object_id)

    def inspect_scene(self) -> BlenderSceneState:
        return self.adapter.inspect_scene()

    def health_check(self) -> HealthReport:
        h = self.adapter.health_check()
        return HealthReport(
            status=h.get("status", "HEALTHY"),
            circuit_state=self.circuit_breaker.state,
            latency_ms=h.get("latency_ms", 0.0),
            error_rate=0.0 if self.circuit_breaker.state == CircuitState.CLOSED else 1.0
        )
